# ExperimentalWorkspace

Model used to expose the Workspace object to the client
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the workspace to be created. | 
**description** | **str** | Description of Workspace. | [optional] 
**cloud_id** | **str** | The cloud id for the workspace | 
**compute_config_id** | **str** | The compute config id for the workspace | 
**base_snapshot** | **str** | Metadata on base snapshot | [optional] 
**id** | **str** | Server assigned unique identifier of the workspace. | 
**created_at** | **datetime** | Time at which Workspace was created. | 
**creator_id** | **str** | Identifier of user who created the Workspace. | [optional] 
**organization_id** | **str** | Organization that the workspace is associated with. | 
**is_deleted** | **bool** | Is the workspace deleted | [optional] 
**cluster_id** | **str** | ID of the Cluster. | 
**project_id** | **str** | ID of the Project. | 
**environment_id** | **str** | ID of the environment. | [optional] 
**last_used_cloud_id** | **str** | ID of the last cloud used in this workspace, or by the user if this is a new workspace.  | [optional] 
**runtime_env_json** | **str** | Identifier of user who created the Workspace. | [optional] 
**current_state** | **str** | The workspace current state. | [optional] 
**state** | [**SessionState**](SessionState.md) | The workspace current state enum. | [optional] 
**is_owner** | **bool** | Is the user the owner of the workspace. | [optional] 
**owners** | [**list[MiniUser]**](MiniUser.md) | List of Users who have Owner level permissions for this workspace. | [optional] [default to []]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


