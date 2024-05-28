# CreateExperimentalWorkspace

Model used to create a Workspace.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the workspace to be created. | 
**description** | **str** | Description of Workspace. | [optional] 
**cloud_id** | **str** | The cloud id for the workspace | 
**compute_config_id** | **str** | The compute config id for the workspace | 
**base_snapshot** | **str** | Metadata on base snapshot | [optional] 
**cluster_environment_build_id** | **str** | The cluster environment build id for the cluster used by the workspace | 
**idle_timeout_minutes** | **int** | Idle timeout (in minutes), after which the Cluster is terminated. Idle time is defined as the time during which a Cluster is not running a user command (through &#39;anyscale exec&#39; or the Web UI), and does not have an attached driver. Time spent running Jupyter commands, or commands run through ssh, is still considered &#39;idle&#39;. | [optional] [default to 120]
**cloned_job_id** | **str** | Id of the associated job. | [optional] 
**cloned_workspace_id** | **str** | Id of the cloned workspace. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


