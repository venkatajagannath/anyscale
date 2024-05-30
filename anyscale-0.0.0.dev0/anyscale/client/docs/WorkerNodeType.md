# WorkerNodeType

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | An arbitrary name for this node type, which will be registered with OSS available_node_types.  | 
**instance_type** | **str** | The cloud provider instance type to use for this node. | 
**resources** | [**Resources**](Resources.md) | Declaration of node resources for Autoscaler. | [optional] 
**aws_advanced_configurations** | [**AWSNodeOptions**](AWSNodeOptions.md) | Additional AWS-specific configurations can be specified per node type and they will override the configuration specified for the whole cloud. | [optional] 
**gcp_advanced_configurations** | [**GCPNodeOptions**](GCPNodeOptions.md) | Additional GCP-specific configurations can be specified per node type and they will override the configuration specified for the whole cloud. | [optional] 
**min_workers** | **int** | The minimum number of nodes of this type that Anyscale should spin up. | [optional] 
**max_workers** | **int** | The maximum number of nodes of this type that Anyscale should spin up. | [optional] 
**use_spot** | **bool** | Whether or not to use spot instances for this node type. | [optional] [default to False]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


