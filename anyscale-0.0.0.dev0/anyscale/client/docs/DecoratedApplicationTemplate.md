# DecoratedApplicationTemplate

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Server assigned unique identifier. | 
**name** | **str** | Name of the App Config. | 
**project_id** | **str** | ID of the Project this App Config is for. | [optional] 
**organization_id** | **str** | ID of the Organization this App Config was created in. | 
**creator_id** | **str** | ID of the User that created this record. | 
**created_at** | **datetime** | Timestamp of when this record was created. | 
**last_modified_at** | **datetime** | Timestamp of when this record was last updated. | 
**deleted_at** | **datetime** | Timestamp of when this record was deleted. | [optional] 
**is_default** | **bool** | True if this App Config is created and managed by anyscale | [optional] [default to False]
**creator** | [**MiniUser**](MiniUser.md) | Read-only field. Information about the creator. | 
**latest_build** | [**MiniBuild**](MiniBuild.md) | Read-only field. Data about the most recent build  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


