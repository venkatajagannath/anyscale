# ComputeTemplateQuery

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**orgwide** | **bool** |  | [optional] [default to False]
**project_id** | **str** |  | [optional] 
**creator_id** | **str** | Filters Compute Templates by creator. This is only supported when &#x60;orgwide&#x60; is True. | [optional] 
**name** | [**TextQuery**](TextQuery.md) | Filters ComputeTemplates by name. If this field is absent, no filtering is done. For now, only equals match is supported when &#x60;orgwide&#x60; is False. | [optional] 
**include_anonymous** | **bool** | Whether to include anonymous compute templates in the search. Anonymous compute templates are usually not shown in list views. | [optional] [default to False]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


