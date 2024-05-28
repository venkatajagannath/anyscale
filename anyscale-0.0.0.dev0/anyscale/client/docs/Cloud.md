# Cloud

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
**id** | **str** | Server assigned unique identifier. | 
**type** | [**CloudTypes**](CloudTypes.md) |  | 
**creator_id** | **str** | ID of the User who created this Cloud. | 
**created_at** | **datetime** | Time when this Cloud was created. | 
**status** | [**CloudStatus**](CloudStatus.md) | The status of this cloud. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


