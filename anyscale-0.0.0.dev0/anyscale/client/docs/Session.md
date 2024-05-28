# Session

DEPRECATED: Use DecoratedSession instead which is based on the base-api Session model
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**idle_timeout** | **int** |  | [optional] 
**created_at** | **datetime** |  | 
**snapshots_history** | [**list[AppliedSnapshot]**](AppliedSnapshot.md) |  | 
**metrics_dashboard_url** | **str** |  | [optional] 
**persistent_metrics_url** | **str** |  | [optional] 
**connect_url** | **str** |  | [optional] 
**jupyter_notebook_url** | **str** |  | [optional] 
**service_proxy_url** | **str** |  | [optional] 
**access_token** | **str** |  | 
**ray_dashboard_url** | **str** |  | [optional] 
**webterminal_auth_url** | **str** |  | [optional] 
**tensorboard_available** | **bool** |  | 
**project_id** | **str** |  | 
**host_name** | **str** |  | [optional] 
**head_node_ip** | **str** |  | [optional] 
**state** | [**SessionState**](SessionState.md) |  | 
**pending_state** | [**SessionState**](SessionState.md) | The requsted state when a state change is requested or None if there is no requested state. | [optional] 
**state_data** | [**SessionStateData**](SessionStateData.md) |  | [optional] 
**cloud_id** | **str** |  | [optional] 
**idle_time_remaining_seconds** | **int** | The idle-time remaining in seconds before the session is auto-suspended. | [optional] 
**anyscaled_config** | **str** |  | [optional] 
**anyscaled_config_generated_at** | **datetime** |  | [optional] 
**allow_public_internet_traffic** | **bool** |  | [optional] [default to False]
**user_service_access** | [**UserServiceAccessTypes**](UserServiceAccessTypes.md) |  | [optional] 
**user_service_token** | **str** |  | [optional] 
**user_service_url** | **str** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


