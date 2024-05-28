# coding: utf-8

"""
    Managed Ray API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from openapi_client.configuration import Configuration


class ServiceUsage(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'product_type': 'ProductType',
        'credit_card_information': 'CreditCardInformation',
        'bank_account_information': 'BankAccountInformation',
        'current_billing_period_start': 'datetime',
        'current_billing_period_end': 'datetime',
        'unpaid_balance': 'int',
        'available_credits': 'int',
        'current_period_usage': 'int',
        'projected_balance_due': 'int'
    }

    attribute_map = {
        'product_type': 'product_type',
        'credit_card_information': 'credit_card_information',
        'bank_account_information': 'bank_account_information',
        'current_billing_period_start': 'current_billing_period_start',
        'current_billing_period_end': 'current_billing_period_end',
        'unpaid_balance': 'unpaid_balance',
        'available_credits': 'available_credits',
        'current_period_usage': 'current_period_usage',
        'projected_balance_due': 'projected_balance_due'
    }

    def __init__(self, product_type=None, credit_card_information=None, bank_account_information=None, current_billing_period_start=None, current_billing_period_end=None, unpaid_balance=None, available_credits=None, current_period_usage=None, projected_balance_due=None, local_vars_configuration=None):  # noqa: E501
        """ServiceUsage - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._product_type = None
        self._credit_card_information = None
        self._bank_account_information = None
        self._current_billing_period_start = None
        self._current_billing_period_end = None
        self._unpaid_balance = None
        self._available_credits = None
        self._current_period_usage = None
        self._projected_balance_due = None
        self.discriminator = None

        self.product_type = product_type
        if credit_card_information is not None:
            self.credit_card_information = credit_card_information
        if bank_account_information is not None:
            self.bank_account_information = bank_account_information
        self.current_billing_period_start = current_billing_period_start
        self.current_billing_period_end = current_billing_period_end
        self.unpaid_balance = unpaid_balance
        self.available_credits = available_credits
        self.current_period_usage = current_period_usage
        self.projected_balance_due = projected_balance_due

    @property
    def product_type(self):
        """Gets the product_type of this ServiceUsage.  # noqa: E501

        Type of product subscription this information is about.  # noqa: E501

        :return: The product_type of this ServiceUsage.  # noqa: E501
        :rtype: ProductType
        """
        return self._product_type

    @product_type.setter
    def product_type(self, product_type):
        """Sets the product_type of this ServiceUsage.

        Type of product subscription this information is about.  # noqa: E501

        :param product_type: The product_type of this ServiceUsage.  # noqa: E501
        :type: ProductType
        """
        if self.local_vars_configuration.client_side_validation and product_type is None:  # noqa: E501
            raise ValueError("Invalid value for `product_type`, must not be `None`")  # noqa: E501

        self._product_type = product_type

    @property
    def credit_card_information(self):
        """Gets the credit_card_information of this ServiceUsage.  # noqa: E501

        Payment information if payment type is credit card.  # noqa: E501

        :return: The credit_card_information of this ServiceUsage.  # noqa: E501
        :rtype: CreditCardInformation
        """
        return self._credit_card_information

    @credit_card_information.setter
    def credit_card_information(self, credit_card_information):
        """Sets the credit_card_information of this ServiceUsage.

        Payment information if payment type is credit card.  # noqa: E501

        :param credit_card_information: The credit_card_information of this ServiceUsage.  # noqa: E501
        :type: CreditCardInformation
        """

        self._credit_card_information = credit_card_information

    @property
    def bank_account_information(self):
        """Gets the bank_account_information of this ServiceUsage.  # noqa: E501

        Payment information if payment type is bank account.  # noqa: E501

        :return: The bank_account_information of this ServiceUsage.  # noqa: E501
        :rtype: BankAccountInformation
        """
        return self._bank_account_information

    @bank_account_information.setter
    def bank_account_information(self, bank_account_information):
        """Sets the bank_account_information of this ServiceUsage.

        Payment information if payment type is bank account.  # noqa: E501

        :param bank_account_information: The bank_account_information of this ServiceUsage.  # noqa: E501
        :type: BankAccountInformation
        """

        self._bank_account_information = bank_account_information

    @property
    def current_billing_period_start(self):
        """Gets the current_billing_period_start of this ServiceUsage.  # noqa: E501

        Start date for current billing period.  # noqa: E501

        :return: The current_billing_period_start of this ServiceUsage.  # noqa: E501
        :rtype: datetime
        """
        return self._current_billing_period_start

    @current_billing_period_start.setter
    def current_billing_period_start(self, current_billing_period_start):
        """Sets the current_billing_period_start of this ServiceUsage.

        Start date for current billing period.  # noqa: E501

        :param current_billing_period_start: The current_billing_period_start of this ServiceUsage.  # noqa: E501
        :type: datetime
        """
        if self.local_vars_configuration.client_side_validation and current_billing_period_start is None:  # noqa: E501
            raise ValueError("Invalid value for `current_billing_period_start`, must not be `None`")  # noqa: E501

        self._current_billing_period_start = current_billing_period_start

    @property
    def current_billing_period_end(self):
        """Gets the current_billing_period_end of this ServiceUsage.  # noqa: E501

        End date for current billing period.  # noqa: E501

        :return: The current_billing_period_end of this ServiceUsage.  # noqa: E501
        :rtype: datetime
        """
        return self._current_billing_period_end

    @current_billing_period_end.setter
    def current_billing_period_end(self, current_billing_period_end):
        """Sets the current_billing_period_end of this ServiceUsage.

        End date for current billing period.  # noqa: E501

        :param current_billing_period_end: The current_billing_period_end of this ServiceUsage.  # noqa: E501
        :type: datetime
        """
        if self.local_vars_configuration.client_side_validation and current_billing_period_end is None:  # noqa: E501
            raise ValueError("Invalid value for `current_billing_period_end`, must not be `None`")  # noqa: E501

        self._current_billing_period_end = current_billing_period_end

    @property
    def unpaid_balance(self):
        """Gets the unpaid_balance of this ServiceUsage.  # noqa: E501

        Accumulated unpaid balances from previous billing periods in cents.  # noqa: E501

        :return: The unpaid_balance of this ServiceUsage.  # noqa: E501
        :rtype: int
        """
        return self._unpaid_balance

    @unpaid_balance.setter
    def unpaid_balance(self, unpaid_balance):
        """Sets the unpaid_balance of this ServiceUsage.

        Accumulated unpaid balances from previous billing periods in cents.  # noqa: E501

        :param unpaid_balance: The unpaid_balance of this ServiceUsage.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and unpaid_balance is None:  # noqa: E501
            raise ValueError("Invalid value for `unpaid_balance`, must not be `None`")  # noqa: E501

        self._unpaid_balance = unpaid_balance

    @property
    def available_credits(self):
        """Gets the available_credits of this ServiceUsage.  # noqa: E501

        Available free and prepaid credits (in cents) at start of current billing cycle (not projected).  # noqa: E501

        :return: The available_credits of this ServiceUsage.  # noqa: E501
        :rtype: int
        """
        return self._available_credits

    @available_credits.setter
    def available_credits(self, available_credits):
        """Sets the available_credits of this ServiceUsage.

        Available free and prepaid credits (in cents) at start of current billing cycle (not projected).  # noqa: E501

        :param available_credits: The available_credits of this ServiceUsage.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and available_credits is None:  # noqa: E501
            raise ValueError("Invalid value for `available_credits`, must not be `None`")  # noqa: E501

        self._available_credits = available_credits

    @property
    def current_period_usage(self):
        """Gets the current_period_usage of this ServiceUsage.  # noqa: E501

        Cost of usage in current billing period (in cents).  # noqa: E501

        :return: The current_period_usage of this ServiceUsage.  # noqa: E501
        :rtype: int
        """
        return self._current_period_usage

    @current_period_usage.setter
    def current_period_usage(self, current_period_usage):
        """Sets the current_period_usage of this ServiceUsage.

        Cost of usage in current billing period (in cents).  # noqa: E501

        :param current_period_usage: The current_period_usage of this ServiceUsage.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and current_period_usage is None:  # noqa: E501
            raise ValueError("Invalid value for `current_period_usage`, must not be `None`")  # noqa: E501

        self._current_period_usage = current_period_usage

    @property
    def projected_balance_due(self):
        """Gets the projected_balance_due of this ServiceUsage.  # noqa: E501

        Projected balance due at end of billing period (for only current billing period).  # noqa: E501

        :return: The projected_balance_due of this ServiceUsage.  # noqa: E501
        :rtype: int
        """
        return self._projected_balance_due

    @projected_balance_due.setter
    def projected_balance_due(self, projected_balance_due):
        """Sets the projected_balance_due of this ServiceUsage.

        Projected balance due at end of billing period (for only current billing period).  # noqa: E501

        :param projected_balance_due: The projected_balance_due of this ServiceUsage.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and projected_balance_due is None:  # noqa: E501
            raise ValueError("Invalid value for `projected_balance_due`, must not be `None`")  # noqa: E501

        self._projected_balance_due = projected_balance_due

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ServiceUsage):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ServiceUsage):
            return True

        return self.to_dict() != other.to_dict()
