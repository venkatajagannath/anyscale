# WriteCloud

Model used to create a Cloud.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of this Cloud. | 
**provider** | [**CloudProviders**](CloudProviders.md) | Provider of this Cloud (e.g. AWS). | 
**region** | **str** | Region this Cloud is operating in. This value needs to be supported by this Cloud&#39;s provider. (e.g. us-west-2) | 
**credentials** | **str** | Credentials needed to interact with this Cloud. | 
**config** | [**CloudConfig**](CloudConfig.md) | Additional configurable properties of this Cloud. | [optional] 
**is_k8s** | **bool** | Whether this cloud is managed via K8s | [optional] [default to False]
**is_aioa** | **bool** | Whether this cloud is an AIOA cloud. | [optional] [default to False]
**creator_id** | **str** | DEPRECATED. This is now optional and does not need to be passed in. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


