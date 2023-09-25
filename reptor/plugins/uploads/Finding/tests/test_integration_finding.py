import json
import subprocess
import time

import pytest

from reptor.api.ProjectsAPI import ProjectsAPI
from reptor.lib.reptor import Reptor


@pytest.mark.integration
class TestIntegrationFinding(object):
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = Reptor()
        self.projects_api = ProjectsAPI(reptor=self.reptor)

        yield

        # Delete findings via projects_api
        for finding in self.projects_api.get_findings():
            self.projects_api.delete_finding(finding.id)
        # Assert findings are gone
        findings = self.projects_api.get_findings()
        assert len(findings) == 0

    def test_push_valid_finding(self):
        title = str(time.time())
        reference = "https://example.com/" + title
        affected_component = "https://example.com/affected/" + title
        finding = {
            "status": "in-progress",
            "data": {
                "cvss": "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:N",
                "title": title,
                "inexistent-field": "should be ignored",
                "summary": "We detected a reflected XSS vulnerability.",
                "references": [reference],
                "description": "The impact was heavy.",
                "recommendation": "HTML encode user-supplied inputs.",
                "affected_components": [
                    affected_component,
                    "https://example.com/q=alert(1)",
                ],
            },
        }
        p = subprocess.Popen(
            ["reptor", "finding"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        p.communicate(input=json.dumps(finding).encode())
        p.wait()
        assert p.returncode == 0

        findings = self.projects_api.get_findings()
        assert title in [f.data.title for f in findings]
        all_references = list()
        all_affected_components = list()
        for f in findings:
            all_references.extend(f.data.references)
            all_affected_components.extend(f.data.affected_components)
        assert reference in all_references
        assert affected_component in all_affected_components

    def test_push_invalid_finding(self):
        title = str(time.time())
        finding = {
            "status": "in-progress",
            "data": {
                "cvss": "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:N",
                "title": title,
                "inexistent-field": "should be ignored",
                "summary": "We detected a reflected XSS vulnerability.",
                "references": [],
                "description": "The impact was heavy.",
                "recommendation": "HTML encode user-supplied inputs.",
                "affected_components": "ERROR: This should be list",
            },
        }
        p = subprocess.Popen(
            ["reptor", "finding"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        _, err = p.communicate(input=json.dumps(finding).encode())
        p.wait()
        assert p.returncode == 2
        findings = self.projects_api.get_findings()
        assert title not in [f.data.title for f in findings]
        assert (
            "affected_components" in err.decode()
        )  # The errornous field should occur in error message
