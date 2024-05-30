# Build

Model used to create a Build.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**application_template_id** | **str** | ID of the App Config this Build belongs to. | 
**config_json** | [**AppConfigConfigSchema**](AppConfigConfigSchema.md) | Config JSON used to create this Build. | 
**id** | **str** | Server assigned unique identifier. | 
**revision** | **int** | Auto incrementing version number for this Build | 
**creator_id** | **str** | ID of the user who created this Build. | 
**docker_image_name** | **str** | The name of the docker image for this build. | [optional] 
**error_message** | **str** | Detailed error message. This will only be populated if the Build operation failed. | [optional] 
**status** | [**BuildStatus**](BuildStatus.md) |      Status of the Build.      &#x60;pending&#x60; - Build operation is queued and has not started yet.     &#x60;in_progress&#x60; - Build operation is in progress.     &#x60;succeeded&#x60; - Build operation completed successfully.     &#x60;failed&#x60; - Build operation completed unsuccessfully.     &#x60;pending_cancellation&#x60; - Build operation is marked for cancellation.     &#x60;cancelled&#x60; - Build operation was cancelled before it completed.      | 
**created_at** | **datetime** | Timestamp of when this Build was created. | 
**last_modified_at** | **datetime** | Timestamp of when this Build was last updated. | 
**deleted_at** | **datetime** | Timestamp of when this Build was deleted. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


