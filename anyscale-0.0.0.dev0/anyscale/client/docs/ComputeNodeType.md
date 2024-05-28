# ComputeNodeType

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | An arbitrary name for this node type, which will be registered with OSS available_node_types.  | 
**instance_type** | **str** | The cloud provider instance type to use for this node. | 
**resources** | [**Resources**](Resources.md) | Declaration of node resources for Autoscaler. | [optional] 
**aws_advanced_configurations** | [**AWSNodeOptions**](AWSNodeOptions.md) | Additional AWS-specific configurations can be specified per node type and they will override the configuration specified for the whole cloud. | [optional] 
**gcp_advanced_configurations** | [**GCPNodeOptions**](GCPNodeOptions.md) | Additional GCP-specific configurations can be specified per node type and they will override the configuration specified for the whole cloud. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


