# CreateClusterComputeConfig

Configuration of compute resources to use for launching a Cluster.     
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cloud_id** | **str** | The ID of the Anyscale cloud to use for launching Clusters. | 
**max_workers** | **int** | Desired limit on total running workers for this Cluster. | [optional] 
**region** | **str** | Deprecated! When creating a cluster compute, a region does not have to be provided. Instead we will use the value from the cloud. | [optional] [default to 'USE_CLOUD']
**allowed_azs** | **list[str]** | The availability zones that clusters are allowed to be launched in, e.g. \&quot;us-west-2a\&quot;. If not specified, any AZ may be used. | [optional] 
**head_node_type** | [**ComputeNodeType**](ComputeNodeType.md) | Node configuration to use for the head node.  | 
**worker_node_types** | [**list[WorkerNodeType]**](WorkerNodeType.md) | A list of node types to use for worker nodes.  | 
**aws** | [**AWSNodeOptions**](AWSNodeOptions.md) | Fields specific to AWS node types. | [optional] 
**gcp** | [**GCPNodeOptions**](GCPNodeOptions.md) | Fields specific to GCP node types. | [optional] 
**azure** | **object** | Fields specific to Azure node types. | [optional] 
**maximum_uptime_minutes** | **int** | If set to a positive number, Anyscale will terminate the cluster this many minutes after cluster start. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


