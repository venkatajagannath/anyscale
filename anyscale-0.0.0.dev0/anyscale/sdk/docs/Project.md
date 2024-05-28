# Project

Model used to read a Project.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the Project to be created. | 
**cluster_config** | **str** | Cluster config associated with the Project. This can later be used to start a Session. | 
**description** | **str** | Description of Project. | [optional] 
**id** | **str** | Server assigned unique identifier of the Project. | 
**creator_id** | **str** | Identifier of user who created the Project. | [optional] 
**created_at** | **datetime** | Time at which Project was created. | 
**organization_id** | **str** | Organization that the Project is associated with. | 
**active_sessions** | **int** | Read only. Number of active sessions for this project. | 
**last_activity_at** | **datetime** | Read only. The most recent activity for this project. This is based on the most recently created sessions | 
**last_used_cloud_id** | **str** | ID of the last cloud used in this project, or by the user if this is a new project.  | [optional] 
**is_default** | **bool** | True if this project is the default project for the organization. | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


