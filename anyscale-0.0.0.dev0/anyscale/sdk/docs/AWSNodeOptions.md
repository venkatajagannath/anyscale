# AWSNodeOptions

The specific subset of AWS API options we want to support.  See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.ServiceResource.create_instances
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**block_device_mappings** | [**list[BlockDeviceMapping]**](BlockDeviceMapping.md) |  | [optional] 
**iam_instance_profile** | [**IamInstanceProfileSpecification**](IamInstanceProfileSpecification.md) |  | [optional] 
**security_group_ids** | **list[str]** |  | [optional] 
**subnet_id** | **str** |  | [optional] 
**tag_specifications** | [**list[AWSTagSpecification]**](AWSTagSpecification.md) |  | [optional] 
**network_interfaces** | [**list[NetworkInterface]**](NetworkInterface.md) | The network interfaces to associate with the instance. If you specify a network interface, you must specify any security groups and subnets as part of the network interface. | [optional] 
**placement** | [**object**](.md) |  | [optional] 
**launch_template** | [**object**](.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


