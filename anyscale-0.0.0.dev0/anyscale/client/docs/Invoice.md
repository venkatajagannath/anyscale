# Invoice

Model used to read an Invoice.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID of invoice from Chargify. | 
**payment_url** | **str** | URL to pay invoice. | 
**pdf_url** | **str** | URL to view pdf of invoice. | 
**due_date** | **datetime** | Date invoice is due. | 
**status** | [**InvoiceStatus**](InvoiceStatus.md) | Status of invoice payment. | 
**show_payment_link** | **bool** | Show link to pay invoice if invoice is open and payment information is already provided. | 
**outstanding_due_amount** | **int** | Amount that still needs to be paid on the invoice in cents. | 
**total_amount** | **int** | Original invoice total amount due in cents. | 
**product_type** | [**ProductType**](ProductType.md) | Type of product this invoice is for. | 
**period_start_date** | **datetime** | Start date for the invoice. | 
**period_end_date** | **datetime** | End date for the invoice. | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


