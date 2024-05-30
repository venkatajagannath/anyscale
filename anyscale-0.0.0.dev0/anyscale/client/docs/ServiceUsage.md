# ServiceUsage

Model used to read usage information of Anyscale subscription from Chargify.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_type** | [**ProductType**](ProductType.md) | Type of product subscription this information is about. | 
**credit_card_information** | [**CreditCardInformation**](CreditCardInformation.md) | Payment information if payment type is credit card. | [optional] 
**bank_account_information** | [**BankAccountInformation**](BankAccountInformation.md) | Payment information if payment type is bank account. | [optional] 
**current_billing_period_start** | **datetime** | Start date for current billing period. | 
**current_billing_period_end** | **datetime** | End date for current billing period. | 
**unpaid_balance** | **int** | Accumulated unpaid balances from previous billing periods in cents. | 
**available_credits** | **int** | Available free and prepaid credits (in cents) at start of current billing cycle (not projected). | 
**current_period_usage** | **int** | Cost of usage in current billing period (in cents). | 
**projected_balance_due** | **int** | Projected balance due at end of billing period (for only current billing period). | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


