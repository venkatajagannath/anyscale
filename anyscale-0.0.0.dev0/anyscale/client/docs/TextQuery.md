# TextQuery

Query model to filter results based on Text properties (e.g. name, description).  Exactly one field should be populated.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**equals** | **str** | Property is an exact match of this value. | [optional] 
**not_equal** | **str** | Property does not match of this value. | [optional] 
**contains** | **str** | Property contains this value as a substring. The value should not have opening and closing wildcard characters. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


