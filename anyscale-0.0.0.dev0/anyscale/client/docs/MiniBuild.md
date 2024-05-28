# MiniBuild

The greatest common factor data about a build that is used by most endpoints
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Server assigned unique identifier. | 
**revision** | **int** | Auto incrementing version number for this Build | 
**status** | [**BuildStatus**](BuildStatus.md) |      Status of the Build.      &#x60;pending&#x60; - Build operation is queued and has not started yet.     &#x60;in_progress&#x60; - Build operation is in progress.     &#x60;succeeded&#x60; - Build operation completed successfully.     &#x60;failed&#x60; - Build operation completed unsuccessfully.     &#x60;pending_cancellation&#x60; - Build operation is marked for cancellation.     &#x60;cancelled&#x60; - Build operation was cancelled before it completed.      | 
**application_template_name** | **str** | The name of the cluster environment this build belongs to | 
**application_template_id** | **str** | The id of the cluster environment this build belongs to | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


