import pathlib
import typing
from posixpath import join as urljoin
from typing import Optional

from reptor.api.APIClient import APIClient
from reptor.api.ProjectDesignsAPI import ProjectDesignsAPI
from reptor.api.models import Finding, FindingRaw, Project, FindingData


class ProjectsAPI(APIClient):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.project_design = None

        self.base_endpoint = (
            f"{self.reptor.get_config().get_server()}/api/v1/pentestprojects"
        )

        self.object_endpoint = urljoin(self.base_endpoint, self.project_id)
        self.debug(self.base_endpoint)

    def get_projects(self, readonly: bool = False) -> typing.List[Project]:
        """Gets list of projects

        Args:
            readonly (bool, optional): Only archived projects. Defaults to False.

        Returns:
            json: List of all Projects
        """
        url = self.base_endpoint
        if readonly:
            url = f"{url}?readonly=true"
        response = self.get(url)
        return_data = list()
        for item in response.json()["results"]:
            return_data.append(Project(item))
        return return_data

    def search(self, search_term: Optional[str] = "") -> typing.List[Project]:
        """Searches projects by search term and retrieves all projects that match

        Args:
            search_term (Optional[str], optional): Search Term to look for. Defaults to None.

        Returns:
            typing.List[Project]: List of projects that match search
        """

        response = self.get(f"{self.base_endpoint}?search={search_term}")

        return_data = list()
        for item in response.json()["results"]:
            return_data.append(Project(item))
        return return_data

    def get_project(self) -> Project:
        if not self.project_id:
            raise ValueError("Make sure you have a project specified.")
        url = self.object_endpoint
        response = self.get(url)
        return Project(response.json())

    def export(self, file_name: typing.Optional[pathlib.Path] = None):
        """Exports a Project to a .tar.gz file locally.

        Args:
            file_name (typing.Optional[pathlib.Path], optional): Local File path. Defaults to None.

        Raises:
            ValueError: Requires project_id
        """
        if not self.project_id:
            raise ValueError(
                "No project ID. Specify in reptor conf or via -p / --project-id"
            )

        if not file_name:
            filepath = pathlib.Path().cwd()
            file_name = filepath / f"{self.project_id}.tar.gz"

        url = urljoin(self.base_endpoint, f"{self.project_id}/export/all")
        data = self.post(url)
        with open(file_name, "wb") as f:
            f.write(data.content)

    def duplicate(self) -> Project:
        """Duplicates Projects

        Returns:
            Project: Project Object
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/copy/")
        duplicated_project = self.post(url).json()
        return Project(duplicated_project)

    def get_findings(self) -> typing.List[Finding]:
        """Gets all findings of a project

        Returns:
            typing.List[Finding]: List of findings for this project
        """
        return_data = list()
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/")
        response = self.get(url).json()

        if not response:
            return return_data

        if not self.project_design:
            project_design_id = response[0]['project_type']
            self.project_design = ProjectDesignsAPI(
                project_design_id=project_design_id).project_design

        for item in response:
            finding = Finding(
                self.project_design,
                FindingRaw(item)
            )
            return_data.append(finding)
        return return_data

    def update_finding(self, finding_id: str, data: dict) -> None:
        # Todo: Should accept a finding object ?
        url = urljoin(self.base_endpoint,
                      f"{self.project_id}/findings/{finding_id}/")
        self.patch(url, data)

    def update_project(self, data: dict) -> None:
        # Todo: Should return an updated object?
        url = urljoin(self.base_endpoint, f"{self.project_id}/")
        self.patch(url, data)

    def get_enabled_language_codes(self) -> list:
        url = urljoin(self.reptor.get_config().get_server(),
                      "api/v1/utils/settings/")
        settings = self.get(url).json()
        languages = [
            l["code"] for l in settings.get("languages", list()) if l["enabled"] == True
        ]
        return languages
