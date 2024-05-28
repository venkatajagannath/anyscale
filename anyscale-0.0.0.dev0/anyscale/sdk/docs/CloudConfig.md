# CloudConfig

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**max_stopped_instances** | **int** | Maximum number of instances that can be retained for reuse after a Cluster has terminated. This may help Clusters start up faster, but stopped instances will accrue some costs. Defaults to 0, which means no instances will be retained for reuse. A value of -1 means all instances will be retained. | [optional] [default to 0]
**vpc_peering_ip_range** | **str** | VPC IP range for this Cloud. | [optional] 
**vpc_peering_target_project_id** | **str** | Project ID of the VPC to peer with. | [optional] 
**vpc_peering_target_vpc_id** | **str** | ID of the VPC to peer with. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


