from reptor.lib.plugins.UploadBase import UploadBase
from reptor.api.NotesAPI import NotesAPI


class Note(UploadBase):
    """
    # Short Help:
    Uploads a note

    # Description:

    # Arguments:

    # Developer Notes:
    """

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)

    def run(self):
        notename = self.reptor.get_config().get_cli_overwrite().get("notename")
        parent_notename = None
        icon = None
        if notename:
            parent_notename = "Uploads"
        else:
            notename = "Uploads"
            icon = "📤"
        force_unlock = self.reptor.get_config().get_cli_overwrite().get("force_unlock")
        no_timestamp = self.reptor.get_config().get_cli_overwrite().get("no_timestamp")

        self.reptor.api.notes.write_note(
            notename=notename,
            parent_notename=parent_notename,
            icon=icon,
            force_unlock=force_unlock,  # type: ignore
            no_timestamp=no_timestamp,  # type: ignore
        )


loader = Note