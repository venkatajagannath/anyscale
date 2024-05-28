# UserInfo

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**email** | **str** |  | 
**name** | **str** |  | 
**lastname** | **str** | The user&#39;s last name. | [optional] 
**username** | **str** |  | 
**verified** | **bool** |  | 
**organization_permission_level** | [**OrganizationPermissionLevel**](OrganizationPermissionLevel.md) | User&#39;s permission level in the organization. This value is absent if the user does not have a permission level assigned. | 
**organization_ids** | **list[str]** | Deprecated: use organization -- List of organizations that the logged in user is a part of. | 
**organizations** | [**list[Organization]**](Organization.md) | List of organizations that the logged in user is a part of. | 
**has_setup_cloud** | **bool** | True if the user has clouds setup in their organization. | [optional] 
**ld_hash** | **str** | Server generated secure hash of the user info that should be sent to LaunchDarkly along with the user data. | 
**ld_hash_fields** | **list[str]** | List of fields in the userInfo used to generate the secure hash. Clients should send those fields to LaunchDarkly as the user data. These fields should be used in addition to the \&quot;key\&quot; field which is based off the user&#39;s id. | 
**is_support_user** | **bool** |  | [optional] [default to False]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


