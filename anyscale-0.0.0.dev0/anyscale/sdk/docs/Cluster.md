# Cluster

Read model for a Cluster.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of this Cluster. | 
**project_id** | **str** | Project that this Cluster belongs to. If none, this Cluster will use the default Project. | [optional] 
**cluster_environment_build_id** | **str** | Cluster Environment Build that this Cluster is using. | 
**cluster_compute_id** | **str** | Cluster Compute that this Cluster is using. | 
**cluster_compute_config** | [**ClusterComputeConfig**](ClusterComputeConfig.md) | One-off cluster compute that this cluster is using. | [optional] 
**idle_timeout_minutes** | **int** | Idle timeout (in minutes), after which the Cluster is terminated. Idle time is defined as the time during which a Cluster is not running a user command (through &#39;anyscale exec&#39; or the Web UI), and does not have an attached driver. Time spent running Jupyter commands, or commands run through ssh, is still considered &#39;idle&#39;. | [optional] [default to 120]
**allow_public_internet_traffic** | **bool** | Whether public internet traffic can access Serve endpoints or if an authentication token is required. | [optional] [default to False]
**user_service_access** | [**UserServiceAccessTypes**](UserServiceAccessTypes.md) | Whether user service can be accessed by public internet traffic. | [optional] 
**id** | **str** | Server assigned unique identifier. | 
**state** | [**ClusterState**](ClusterState.md) | Current state of the Cluster. | 
**goal_state** | [**ClusterState**](ClusterState.md) | State that this Cluster will eventually transition to. This will not be populated if there are no pending transitions. | [optional] 
**creator_id** | **str** | User who created this Cluster. | 
**created_at** | **datetime** | Time at which this Cluster was created. | 
**access_token** | **str** | Access token for web based services (e.g. jupyter, tensorboard, etc). This field will be populated when the web based services are available after the Cluster finishes starting. | 
**services_urls** | [**ClusterServicesUrls**](ClusterServicesUrls.md) | URLs for additional services running on this Cluster (e.g. Jupyter, Ray Dashboard, etc.). | 
**head_node_info** | [**ClusterHeadNodeInfo**](ClusterHeadNodeInfo.md) | Detailed information about this Cluster&#39;s head node. This will only be populated for Clusters that have finished starting. | [optional] 
**ssh_authorized_keys** | **list[str]** | Serialized SSH Public Keys to be placed in the machine&#39;s authorized_keys. | 
**ssh_private_key** | **str** | SSH Private key that can be used to access the Cluster&#39;s servers. | 
**ray_version** | **str** | The last known ray version running on this cluster. | [optional] 
**ray_version_last_updated_at** | **datetime** | The time in which the ray version of this cluster was updated. | [optional] 
**user_service_token** | **str** | Token used to authenticate user service if it is accessible to public internet. This field will beempty if user service is not publically accessible. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


