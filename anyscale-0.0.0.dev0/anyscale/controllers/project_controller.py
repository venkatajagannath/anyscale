import contextlib
import json
import os
from typing import Optional

import click
from openapi_client.rest import ApiException
import tabulate

import anyscale
from anyscale.cli_logger import BlockLogger
from anyscale.cloud import get_cloud_id_and_name
from anyscale.controllers.base_controller import BaseController
from anyscale.project import (  # pylint:disable=private-import
    attach_to_project_with_id,
    create_new_proj_def,
    get_proj_id_from_name,
    load_project_or_throw,
    register_or_attach_to_project,
    write_project_file_to_disk,
)
from anyscale.sdk.anyscale_client import (
    PageQuery,
    Project,
    ProjectListResponse,
    ProjectsQuery,
    TextQuery,
)
import anyscale.shared_anyscale_utils.conf as shared_anyscale_conf
from anyscale.util import get_endpoint


COMPUTE_CONFIG_FILENAME = "example_compute_config.json"


class ProjectController(BaseController):
    def __init__(
        self, log: Optional[BlockLogger] = None, initialize_auth_api_client: bool = True
    ):
        if log is None:
            log = BlockLogger()

        super().__init__(initialize_auth_api_client=initialize_auth_api_client)

        self.log = log
        self.log.open_block("Output")

    def get_proj_id_from_name(
        self, project_name: str, owner: Optional[str] = None
    ) -> str:
        """ Call API to get project id given a project name.  """
        return get_proj_id_from_name(project_name, self.api_client, owner)

    def clone(self, project_name: str, owner: Optional[str] = None) -> None:
        project_id = get_proj_id_from_name(project_name, self.api_client, owner)

        os.makedirs(project_name)
        write_project_file_to_disk(project_id, project_name)

        self._write_sample_compute_config(
            filepath=os.path.join(project_name, COMPUTE_CONFIG_FILENAME),
            project_id=project_id,
        )

    def create(self, name: str, parent_cloud_id: Optional[str]) -> None:
        """
        Call API to create a new project given a project name.
        """
        existing_projects = []
        with contextlib.suppress(click.ClickException, ApiException):
            user_info = self.api_client.get_user_info_api_v2_userinfo_get()
            existing_projects = self.api_client.find_project_by_project_name_api_v2_projects_find_by_name_get(
                name, owner=user_info.result.username
            ).results

        if len(existing_projects):
            project_id = existing_projects[0].id
            url = get_endpoint(f"/projects/{project_id}")
            self.log.info(
                f"Project with name {name} is already created by you at {url}."
            )
        else:
            if not parent_cloud_id and (
                self.api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get(
                    "cloud-isolation-phase-1"
                ).result.is_on
                is True
            ):
                raise click.ClickException(
                    "Parent cloud id should be specified when creating a new projet because "
                    "cloud isolation has been enabled."
                )
            # Create new project
            project_id = self.api_client.create_project_api_v2_projects_post(
                write_project={
                    "name": name,
                    "description": "",
                    "initial_cluster_config": None,
                    "parent_cloud_id": parent_cloud_id,
                }
            ).result.id
            url = get_endpoint(f"/projects/{project_id}")
            self.log.info(f"Created project with name {name} at {url}.")
        self.log.info(
            f"Please specify the project id as {project_id} when calling "
            "Anyscale CLI or SDK commands or Ray Client."
        )

    def init(
        self,
        project_id: Optional[str],
        name: Optional[str],
        config: Optional[str] = None,
        requirements: Optional[str] = None,  # noqa: ARG002
    ) -> None:
        if config:
            message = (
                "Warning: `anyscale init` is no longer accepting a cluster yaml in "
                "the --config argument. All sessions should be started with cluster envs "
                "and compute configs."
            )
            self.log.warning(message)
        project_id_path = anyscale.project.ANYSCALE_PROJECT_FILE

        if project_id:
            # Exactly one of project_id or name must be provided
            assert not name
            attach_to_project_with_id(project_id, self.api_client)
        else:
            # Exactly one of project_id or name must be provided
            assert name

            if os.path.exists(project_id_path):
                # Project id exists.
                project_definition = load_project_or_throw()
                project_id = project_definition.config["project_id"]

                # Checking if the project is already registered.
                # TODO: Fetch project by id rather than listing all projects
                try:
                    resp = self.api_client.get_project_api_v2_projects_project_id_get(
                        project_id
                    )
                except Exception:  # noqa: BLE001
                    resp = None
                if resp and resp.result.id == project_id:
                    if name != resp.result.name:
                        self.log.info(
                            "This directory is already attached to a project named {name}: {url}. ".format(
                                name=resp.result.name,
                                url=get_endpoint(f"/projects/{resp.result.id}"),
                            )
                            + "Delete .anyscale.yaml if you wish to attach to a different project."
                        )
                    else:
                        self.log.info(
                            "This directory is already attached to this project: {url}".format(
                                url=get_endpoint(f"/projects/{resp.result.id}")
                            )
                        )
                    return
                # Project id exists locally but not registered in the db.
                if click.confirm(
                    "The Anyscale project associated with this directory doesn't "
                    "seem to exist anymore or is not valid. Do you want "
                    "to re-init this directory?",
                    abort=True,
                ):
                    os.remove(project_id_path)
                    _, project_definition = create_new_proj_def(
                        name, api_client=self.api_client,
                    )
            else:
                # Project id doesn't exist and not enough info to create project.
                _, project_definition = create_new_proj_def(
                    name, api_client=self.api_client,
                )

            register_or_attach_to_project(project_definition, self.api_client)

    def _write_sample_compute_config(
        self, filepath: str, project_id: Optional[str] = None,
    ) -> None:
        """Writes a sample compute config JSON file to be used with anyscale up.
        If no default cloud is available from the organization and the user
        has never used a cloud before, don't write the sample compute config.
        """

        # Compute configs need a real cloud ID.
        cloud_id = None
        user = self.api_client.get_user_info_api_v2_userinfo_get().result
        organization = user.organizations[0]  # Each user only has one org
        if organization.default_cloud_id:
            # Use default cloud id if organization has one and if user has correct
            # permissions for it.
            with contextlib.suppress(Exception):
                get_cloud_id_and_name(
                    self.api_client, cloud_id=organization.default_cloud_id
                )
                cloud_id = organization.default_cloud_id
        if not cloud_id and project_id:
            # See if the project has a cloud ID for us to use.
            project = self.anyscale_api_client.get_project(project_id).result
            cloud_id = project.last_used_cloud_id

        # If no cloud ID in the project, fall back to the oldest cloud.
        # (For full compatibility with other frontends, we should be getting
        # the last used cloud from the user, but our users APIs
        # are far from in good shape for that...)
        if not cloud_id:
            cloud_list = self.api_client.list_clouds_api_v2_clouds_get().results
            if len(cloud_list) == 0:
                # If there is no cloud ID from the user,
                # let them create their project and set up a
                # compute config JSON file later.
                return
            cloud_id = cloud_list[-1].id

        default_config = self.api_client.get_default_compute_config_api_v2_compute_templates_default_cloud_id_get(
            cloud_id=cloud_id
        ).result

        with open(filepath, "w") as f:
            json.dump(default_config.to_dict(), f, indent=2)

    def list(self, name: str, json_format: bool, created_by_user: bool, max_items: int):
        paging_count = 20
        page_query = PageQuery(count=paging_count)
        name_query = None
        creator_query = None

        if created_by_user:
            user_info_response = self.api_client.get_user_info_api_v2_userinfo_get()
            user_id = user_info_response.result.id
            creator_query = TextQuery(equals=user_id)

        if name:
            name_query = TextQuery(equals=name)

        response = self._make_projects_query(name_query, creator_query, page_query)
        prepared_result = self._format_project_results(response, json_format)
        next_paging_token = response.metadata.next_paging_token
        has_more = (next_paging_token is not None) and (
            len(prepared_result) < max_items
        )
        while has_more:
            page_query = PageQuery(count=paging_count, paging_token=next_paging_token)
            response = self._make_projects_query(name_query, creator_query, page_query)
            prepared_result = prepared_result + self._format_project_results(
                response, json_format
            )
            next_paging_token = response.metadata.next_paging_token
            has_more = (next_paging_token is not None) and (
                len(prepared_result) < max_items
            )
        prepared_result = prepared_result[:max_items]

        if json_format:
            print(json.dumps(prepared_result))
        else:
            table = tabulate.tabulate(
                prepared_result,
                headers=["NAME", "ID", "URL", "DESCRIPTION"],
                tablefmt="plain",
            )
            print(f"Projects:\n{table}")

    def _format_project_dict(self, project: Project):
        return {
            "name": project.name,
            "id": project.id,
            "url": get_endpoint(f"/projects/{project.id}"),
            "description": project.description,
        }

    def _format_project_list(self, project: Project):
        return [
            project.name,
            project.id,
            f"{shared_anyscale_conf.ANYSCALE_HOST}/projects/{project.id}",
            project.description,
        ]

    def _format_project_results(self, response: ProjectListResponse, json_format: bool):
        if json_format:
            return [self._format_project_dict(result) for result in response.results]
        else:
            return [self._format_project_list(result) for result in response.results]

    def _make_projects_query(
        self,
        name_query: Optional[TextQuery],
        creator_query: Optional[TextQuery],
        page_query: Optional[PageQuery],
    ):
        project_query = ProjectsQuery(
            name=name_query, creator_id=creator_query, paging=page_query
        )
        return self.anyscale_api_client.search_projects(project_query)
