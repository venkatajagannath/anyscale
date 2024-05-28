# Project

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**description** | **str** |  | 
**cloud_id** | **str** |  | [optional] 
**initial_cluster_config** | **str** |  | [optional] 
**id** | **str** |  | 
**created_at** | **datetime** |  | 
**creator_id** | **str** |  | [optional] 
**is_owner** | **bool** |  | 
**directory_name** | **str** |  | 
**cloud** | **str** |  | [optional] 
**last_used_cloud_id** | **str** |  | [optional] 
**active_sessions** | **int** | Read only. Number of active sessions for this project. | 
**last_activity_at** | **datetime** | Read only. The most recent activity for this project. This is based on the most recently created sessions | 
**owners** | [**list[MiniUser]**](MiniUser.md) | List of Users who have Owner level permissions for this Project. | [optional] [default to []]
**is_default** | **bool** | True if this project is the default project for the organization. | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


