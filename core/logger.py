import logging
import pathlib
import re
import sys

from datetime import datetime
from logging import LogRecord
from logging.handlers import RotatingFileHandler

from termcolor import colored
from rich.text import Text
from rich.logging import RichHandler

import settings

from core.console import reptor_console

# This code was heavily copied from https://github.com/mpgn/CrackMapExec/blob/master/cme/logger.py
# However it was also modified to our needs
# See NOTICE for the CrackMapExec License


class ReptorAdapter(logging.LoggerAdapter):
    def __init__(self, extra=None):
        logging.basicConfig(
            format="%(message)s",
            datefmt="[%X]",
            handlers=[
                RichHandler(
                    console=reptor_console,
                    rich_tracebacks=True,
                    tracebacks_show_locals=False,
                )
            ],
        )
        self.logger = logging.getLogger("reptor")
        self.extra = extra
        self.output_file = None

    def _print(self, msg, color="white", *args, **kwargs):
        msg, kwargs = self._format(
            f"{colored(f'{msg}', color, attrs=['bold'])}", kwargs
        )
        text = Text.from_ansi(msg)
        reptor_console.print(text, *args, **kwargs)
        self._log_console_to_file(text, *args, **kwargs)

    def _format(self, msg, *args, **kwargs):
        """
        Format msg for output if needed
        """
        return f"{msg}", kwargs

    def display(self, msg, color="blue", *args, **kwargs):
        self._print(msg, color, *args, **kwargs)

    def fail(self, msg, color="red", *args, **kwargs):
        self._print(msg, color, *args, **kwargs)

    def success(self, msg, color="green", *args, **kwargs):
        self._print(msg, color, *args, **kwargs)

    def highlight(self, msg, *args, **kwargs):
        """
        Prints a completely yellow highlighted message to the user
        """
        msg, kwargs = self._format(f"{colored(msg, 'yellow', attrs=['bold'])}", kwargs)
        text = Text.from_ansi(msg)
        reptor_console.print(text, *args, **kwargs)
        self._log_console_to_file(text, *args, **kwargs)

    def _log_console_to_file(self, text, *args, **kwargs):
        """
        If debug or info logging is not enabled, we still want display/success/fail logged to the file specified,
        so we create a custom LogRecord and pass it to all the additional handlers (which will be all the file handlers
        """
        if self.logger.getEffectiveLevel() >= logging.INFO:
            # will be 0 if it's just the console output, so only do this if we actually have file loggers
            if len(self.logger.handlers):
                try:
                    for handler in self.logger.handlers:
                        handler.handle(
                            LogRecord(
                                "reptor",
                                20,
                                "",
                                kwargs,  # type: ignore
                                msg=text,
                                args=args,
                                exc_info=None,
                            )
                        )
                except Exception as e:
                    self.logger.error(
                        f"Issue while trying to custom print handler: {e}"
                    )
        else:
            self.logger.info(text)

    def add_file_log(self, log_file: pathlib.Path | None = None):
        file_formatter = TermEscapeCodeFormatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        output_file = self.init_log_file() if log_file is None else log_file

        file_handler = RotatingFileHandler(output_file, maxBytes=100000)

        with open(output_file, "a", encoding="utf-8") as f:
            f.write(
                "\n[%s]> %s\n\n"
                % (datetime.now().strftime("%d-%m-%Y %H:%M:%S"), " ".join(sys.argv))
            )

        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        self.logger.debug(f"Added file handler: {file_handler}")

    @staticmethod
    def init_log_file():
        """Creates parent folder structure in home directory of user
        Sets the current Logfile name

        Returns:
            pathlib.Path: Full pathlib Path to log FILE
        """
        date_based_log_folder = settings.LOG_FOLDER / datetime.now().strftime(
            "%Y-%m-%d"
        )
        date_based_log_folder.mkdir(parents=True, exist_ok=True)
        return (
            date_based_log_folder
            / f"log_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log"
        )


class TermEscapeCodeFormatter(logging.Formatter):
    """A class to strip the escape codes for logging to files"""

    def __init__(self, fmt=None, datefmt=None, style="%", validate=True):
        super().__init__(fmt, datefmt, style, validate)  # type: ignore

    def format(self, record):
        escape_re = re.compile(r"\x1b\[[0-9;]*m")
        record.msg = re.sub(escape_re, "", str(record.msg))
        return super().format(record)


reptor_logger = ReptorAdapter()
