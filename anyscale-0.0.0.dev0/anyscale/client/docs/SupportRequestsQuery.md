# SupportRequestsQuery

Query model used to filter Support Requests.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_name** | [**TextQuery**](TextQuery.md) | Filters support requests by organization_name. If this field is absent no filtering is done. | [optional] 
**is_active** | **bool** | Filters support requests to currently active requests. Defaults to true. | [optional] [default to True]
**paging** | [**PageQuery**](PageQuery.md) | Pagination information. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


