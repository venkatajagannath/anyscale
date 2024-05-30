# StartEmptySessionResponse

Response of /start_empty_session product endpoint  Attributes:     session_id: Session ID of the created session. If called on existing session,         this is the session id of that session.     second_update_required: Indicates whether /setup_and_initialize_session should be called         at the end of `anyscale up`. This is true if the file mounts are not empty         or if the command is called on an existing session.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_id** | **str** |  | 
**second_update_required** | **bool** |  | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


