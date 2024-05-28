# UpdateCluster

Model used to update a Cluster. A field will not be updated if its value is absent.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of this Cluster. | [optional] 
**idle_timeout_minutes** | **int** | Idle timeout in minutes. | [optional] 
**cluster_environment_build_id** | **str** | Cluster Environment Build that this Cluster is using. This property may only be changed if the Cluster is in the Terminated state.Use the Start Cluster operation if you wish to change this for a non-Terminated Cluster. | [optional] 
**cluster_compute_id** | **str** | Cluster Compute that this Cluster is using. This property may only be changed if the Cluster is in the Terminated state. Use the Start Cluster operation if you wish to change this for a non-Terminated Cluster. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


