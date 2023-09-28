import os
import subprocess
from pathlib import Path

import pytest

from reptor.plugins.core.Conf.tests.conftest import notes_api


@pytest.mark.integration
class TestIntegrationZap(object):
    @pytest.fixture(autouse=True)
    def tearDown(self, notes_api):
        yield
        # Delete Zap notes (prevents interference between xml and json)
        note = notes_api.get_note_by_title("zap")
        notes_api.delete_note(note.id)

    @pytest.mark.parametrize("format", ["xml", "json"])
    def test_notes(self, format, notes_api):
        input_path = Path(os.path.dirname(__file__)) / f"data/zap-report.{format}"

        p = subprocess.Popen(
            ["reptor", "zap", f"--{format}", "--upload"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        p.communicate(input=input_path.read_bytes())
        assert p.returncode == 0

        note = notes_api.get_note_by_title(
            "http://localhost (7)", parent_notename="zap"
        )
        note_lines = note.text.splitlines()
        assert "*Cross Site Scripting (Reflected)*" in note_lines

        note = notes_api.get_note_by_title(
            "https://localhost (5)", parent_notename="zap"
        )
        note_lines = note.text.splitlines()
        assert "*Application Error Disclosure*" in note_lines
