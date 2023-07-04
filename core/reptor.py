import argparse
import importlib
import sys
import typing

import logging

from inspect import cleandoc

import settings
from core.conf import Config

from utils.string_operations import truncate

from .interfaces.reptor import ReptorProtocol


log = logging.getLogger("reptor")
logging.basicConfig(format="%(message)s")
log.setLevel(logging.INFO)


class Reptor(ReptorProtocol):
    _config: Config

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Reptor, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._load_config()

    def get_config(self) -> Config:
        """Use this to access the current config

        Returns:
            Config: Current Configuration
        """
        return self._config

    def _load_config(self) -> None:
        """Load the config into Reptor"""
        self._config = Config()
        self._config.load_config()

    def _load_system_modules(self):
        """Loads a File and Folder based Modules from the ./modules folder in reptor

        Returns:
            typing.List: Holds absolute paths to each Module file
        """
        module_paths = list()
        for modules_path in settings.MODULE_DIRS.glob("*"):
            if "__pycache__" not in modules_path.name:
                if modules_path.is_dir():
                    module_main_file = modules_path / f"{modules_path.name}.py"
                    if module_main_file.is_file():
                        module_paths.append(str(module_main_file))
                else:
                    module_paths.append(str(modules_path))
        return module_paths

    def _load_community_modules(self) -> None:
        ...

    def _import_modules(self, module_paths: typing.List):
        """Loads each module

        Returns:
            typing.Dict: Dictionary holding each module name
        """
        loaded_modules = dict()
        for module in module_paths:
            # type: ignore
            spec = importlib.util.spec_from_file_location("module.name", module)  # type: ignore

            # type: ignore
            module = importlib.util.module_from_spec(spec)  # type: ignore
            sys.modules["module.name"] = module
            spec.loader.exec_module(module)

            # Add some metadata
            if not hasattr(module, "loader"):
                continue
            module.name = module.loader.__name__.lower()
            module.description = cleandoc(module.loader.__doc__)
            module.short_help = f"{module.name}{max(1,(15-len(module.name)))*' '}{truncate(module.description.split(settings.NEWLINE)[0], length=50)}"

            # Add short_help to tool help message
            if module.loader.__base__ in settings.SUBCOMMANDS_GROUPS:
                settings.SUBCOMMANDS_GROUPS[module.loader.__base__][1].append(
                    module.short_help
                )
            else:
                settings.SUBCOMMANDS_GROUPS["other"][1].append(module.short_help)

            loaded_modules[module.name] = module
        return loaded_modules

    def _create_parsers(self):
        """Creates the description in the help and the parsers to be used

        Returns:
            parser,subparsers: ArgumentParser and SubParser
        """
        # Argument parser description
        description = ""
        for (
            short_help_class,
            short_help_group_meta,
        ) in settings.SUBCOMMANDS_GROUPS.items():
            description += f"\n{short_help_group_meta[0]}:\n"
            description += f"{settings.NEWLINE.join(short_help_group_meta[1])}\n"

        # Argument parser
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        subparsers = parser.add_subparsers(
            dest="command", description=description, help=argparse.SUPPRESS
        )

        return parser, subparsers

    def _dynamically_add_module_options(self, loaded_modules, sub_parsers):
        # Dynamically add module options
        for name, module in loaded_modules.items():
            module.subparser = sub_parsers.add_parser(
                name,
                description=module.description,
                formatter_class=argparse.RawTextHelpFormatter,
            )
            module.loader.add_arguments(module.subparser)

    def _add_config_parse_options(self, parser: argparse.ArgumentParser):
        """Creates the configuration arguments

        Args:
            parser (argparse.ArgumentParser): main parser
        """
        config_parser = parser.add_argument_group("configuration")
        config_parser.add_argument("-s", "--server")
        config_parser.add_argument("-t", "--token", help="SysReptor API token")
        config_parser.add_argument(
            "-f",
            "--force-unlock",
            help="force unlock notes and sections",
            action="store_true",
        )
        config_parser.add_argument(
            "--insecure", help="do not verify server certificate", action="store_true"
        )
        private_or_project_parser = config_parser.add_mutually_exclusive_group()
        private_or_project_parser.add_argument(
            "-p", "--project-id", help="SysReptor project ID"
        )
        private_or_project_parser.add_argument(
            "--private-note", help="add notes to private notes", action="store_true"
        )

    def _configure_global_arguments(self, parser):
        """Enables the parameters
        - project_id
        - verbose
        - insecure
        """
        parser.add_argument(
            "-v", "--verbose", help="increase output verbosity", action="store_true"
        )
        parser.add_argument("-n", "--notename")
        parser.add_argument(
            "-nt",
            "--no-timestamp",
            help="do not prepent timestamp to note",
            action="store_true",
        )
        return parser

    def _parse_main_arguments_with_subparser(self, parser):
        # Parse main parser arguments also if provided in subparser
        previous_unknown = None
        args, unknown = parser.parse_known_args()
        while len(unknown) and unknown != previous_unknown:
            args, unknown = parser.parse_known_args(unknown, args)
            previous_unknown = unknown

        if args.verbose:
            log.setLevel(logging.DEBUG)

        # Override conf from config file by CLI
        args_dict = vars(args)
        config = Config()
        for k in ["server", "project_id", "session_id", "insecure"]:
            config.set(k, args_dict.get(k) or config.get(k, ""))
        # Add cli options to config/cli
        config.set("cli", args_dict)

        return args

    def run(self) -> None:
        module_paths = self._load_system_modules()

        loaded_modules = self._import_modules(module_paths)

        parser, sub_parsers = self._create_parsers()

        self._dynamically_add_module_options(loaded_modules, sub_parsers)

        # Static module options
        self._add_config_parse_options(parser)

        parser = self._configure_global_arguments(parser)
        args = self._parse_main_arguments_with_subparser(parser)

        # Subcommands
        if args.command in loaded_modules:
            module = loaded_modules[args.command]
            module.loader(self, **self._config.get("cli")).run()
