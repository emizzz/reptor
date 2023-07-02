import typing
from posixpath import join as urljoin

from api.APIClient import APIClient
from api.models import Project


class ProjectsAPI(APIClient):
    def __init__(self) -> None:
        super().__init__()

        self.base_endpoint = urljoin(self.server, f"api/v1/pentestprojects/")
        self.object_endpoint = urljoin(f"api/v1/pentestprojects/{self.project_id}")

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

    def search(self, search_term: str = None) -> typing.List[Project]:
        """Searches for search term"""
        if not search_term:
            raise ValueError("search_term is missing")

        response = self.get(f"{self.base_endpoint}?search={search_term}")

        return_data = list()
        for item in response.json()["results"]:
            return_data.append(Project(item))
        return return_data
