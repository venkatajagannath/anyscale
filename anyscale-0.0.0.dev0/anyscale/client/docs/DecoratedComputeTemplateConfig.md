# DecoratedComputeTemplateConfig

Configuration of compute resources to use for launching a session.     
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cloud_id** | **str** | The ID of the Anyscale cloud to use for launching sessions. | 
**max_workers** | **int** | Desired limit on total running workers for this session. | [optional] 
**region** | **str** | The region to launch sessions in, e.g. \&quot;us-west-2\&quot;. | 
**allowed_azs** | **list[str]** | The availability zones that sessions are allowed to be launched in, e.g. \&quot;us-west-2a\&quot;. If not specified, any AZ may be used. | [optional] 
**head_node_type** | [**ComputeNodeType**](ComputeNodeType.md) | Node configuration to use for the head node.  | 
**worker_node_types** | [**list[WorkerNodeType]**](WorkerNodeType.md) | A list of node types to use for worker nodes.  | 
**aws** | [**AWSNodeOptions**](AWSNodeOptions.md) | Fields specific to AWS node types. | [optional] 
**gcp** | [**GCPNodeOptions**](GCPNodeOptions.md) | Fields specific to GCP node types. | [optional] 
**azure** | **object** | Fields specific to Azure node types. | [optional] 
**maximum_uptime_minutes** | **int** | If set to a positive number, Anyscale will terminate the cluster this many minutes after cluster start. | [optional] 
**cloud** | [**MiniCloud**](MiniCloud.md) | The decorated cloud_id | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


