# CreateCluster

Model used to create a new Cluster.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of this Cluster. | 
**project_id** | **str** | Project that this Cluster belongs to. If none, this Cluster will use the default Project. | [optional] 
**cluster_environment_build_id** | **str** | Cluster Environment Build that this Cluster is using. | 
**cluster_compute_id** | **str** | Cluster Compute that this Cluster is using. | [optional] 
**cluster_compute_config** | [**ClusterComputeConfig**](ClusterComputeConfig.md) | One-off cluster compute that this cluster is using. | [optional] 
**idle_timeout_minutes** | **int** | Idle timeout (in minutes), after which the Cluster is terminated. Idle time is defined as the time during which a Cluster is not running a user command (through &#39;anyscale exec&#39; or the Web UI), and does not have an attached driver. Time spent running Jupyter commands, or commands run through ssh, is still considered &#39;idle&#39;. | [optional] [default to 120]
**allow_public_internet_traffic** | **bool** | Whether public internet traffic can access Serve endpoints or if an authentication token is required. | [optional] [default to False]
**user_service_access** | [**UserServiceAccessTypes**](UserServiceAccessTypes.md) | Whether user service can be accessed by public internet traffic. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


