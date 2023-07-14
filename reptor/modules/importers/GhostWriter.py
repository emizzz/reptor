from reptor.lib.importers.BaseImporter import BaseImporter


class GhostWriter(BaseImporter):
    """
    Author: Richard Schwabe
    Version: 1.0
    Website: https://github.com/Syslifters/reptor
    License: MIT
    Tags: core, import, ghostwriter

    Short Help:
    Imports findings from GhostWriter

    Description:
    Connects to the API of a GhostWriter instance and imports its
    finding templates.

    """

    mapping = {}

    def next_findings_batch(self):
        ...


loader = GhostWriter
