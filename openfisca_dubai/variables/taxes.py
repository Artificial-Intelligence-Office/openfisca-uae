"""
This file defines variables for the modelled legislation.

A variable is a property of an Entity such as a Person, a Household…

See https://openfisca.org/doc/key-concepts/variables.html
"""

# Import from numpy the operations you need to apply on OpenFisca's population vectors
# Import from openfisca-core the Python objects used to code the legislation in OpenFisca
from numpy import maximum as max_
from openfisca_core.variables import Variable

# Import the Entities specifically defined for this tax and benefit system
from openfisca_core import holders, periods, variables
from openfisca_dubai import entities

import numpy as np


class corporate_tax(Variable):
    value_type = float
    entity = entities.Person
    definition_period = periods.YEAR
    label = "Corporate tax"
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"

    def formula(person, period, parameters):
        """˘
        Income tax.

        The formula to compute the income tax for a given person at a given period
        """
        # corporate tax rate always applies on the taxable income
        corporate_tax_rate = parameters(period).taxes.corporate_tax_rate
        taxable_income = person("taxable_income", period)

        # exemption rules
        is_pension_fund = person("is_pension_fund", period)
        is_government = person("is_government", period)
        is_person_exempt = person("exempt_person", period)
        is_small_business = (
            person("revenue", period) <= parameters(period).benefits.small_business
        )

        try:
            tax_credits = person("tax_credits", period)
        except:
            tax_credits = 0

        max_tax_credits = parameters(period).taxes.max_tax_credits * taxable_income
        actual_tax_credits = min(tax_credits, max_tax_credits)
        taxable_income -= actual_tax_credits

        is_exempt = (
            np.logical_not(is_government)
            * np.logical_not(is_person_exempt)
            * np.logical_not(is_small_business)
            * np.logical_not(is_pension_fund)
        )

        tax_payable = corporate_tax_rate.calc(taxable_income)

        return tax_payable * is_exempt


class taxable_income(Variable):
    value_type = float
    entity = entities.Person
    definition_period = periods.YEAR
    label = (
        "The income that is subject to Corporate Tax under Federal Decree Law No. 47"
    )
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"

    # Can add a formula later
    def formula(person, period, parameters):
        tax_credits = person("tax_credits", period)
        interest_expense = person("interest_expense", period)
        interest_income = person("interest_income", period)
        depreciation = person("depreciation", period)
        ebitda = person("EBITDA", period)
        amortization = person("amortization", period)
        carry_forward_interest = person("carry_forward_interest", period)

        net_interest = interest_expense - interest_income
        max_interest_deduction = max(0.3 * ebitda, 12000000)
        net_interest = min(net_interest, max_interest_deduction)
        carry_forward_interest = min(
            carry_forward_interest, 0.3 * ebitda - net_interest
        )
        net_interest += carry_forward_interest

        taxable_income = ebitda - net_interest
        taxable_income -= depreciation
        taxable_income -= amortization

        max_tax_credits = 0.75 * taxable_income
        actual_tax_credits = min(tax_credits, max_tax_credits)
        taxable_income -= actual_tax_credits

        return taxable_income


class tax_credits(Variable):
    value_type = float
    entity = entities.Person
    definition_period = periods.YEAR
    label = "Tax Credits"
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"


class is_government(Variable):
    value_type = bool
    entity = entities.Person
    definition_period = periods.YEAR
    label = "A government entity"
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"


class is_pension_fund(Variable):
    value_type = bool
    entity = entities.Person
    definition_period = periods.YEAR
    label = "A pension fund"
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"


class interest_expense(Variable):
    value_type = float
    entity = entities.Person
    definition_period = periods.YEAR
    label = """
    Interest Expense
    """
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"


class interest_income(Variable):
    value_type = float
    entity = entities.Person
    definition_period = periods.YEAR
    label = """
    Interest Expense
    """
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"


class EBITDA(Variable):
    value_type = float
    entity = entities.Person
    definition_period = periods.YEAR
    label = """
    Interest Expense
    """
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"


class depreciation(Variable):
    value_type = float
    entity = entities.Person
    definition_period = periods.YEAR
    label = """
    Interest Expense
    """
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"


class amortization(Variable):
    value_type = float
    entity = entities.Person
    definition_period = periods.YEAR
    label = """
    Interest Expense
    """
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"


class carry_forward_interest(Variable):
    value_type = float
    entity = entities.Person
    definition_period = periods.YEAR
    label = """
    A Taxable Person can carry forward interest expense and offset them against Taxable
    Income in subsequent Tax Periods
    """
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"


class revenue(Variable):
    value_type = float
    entity = entities.Person
    definition_period = periods.YEAR
    label = "The gross amount of income derived during a Tax Period"
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"

    # Can add a formula later


class exempt_person(Variable):
    value_type = bool
    entity = entities.Person
    definition_period = periods.YEAR
    label = "A Person exempt from Corporate Tax under Article 4 of Federal Decree Law No. 47"
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"  # Always use the most official source


class exempt_entity(Variable):
    value_type = bool
    entity = entities.Person
    definition_period = periods.YEAR
    label = "An entity exempt from Corporate Tax under Article 4 of Federal Decree Law No. 47"
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"  # Always use the most official source

    def formula(person, period, parameters):
        """
        Exempt businesses.

        Tax exempt entities include government entities, qualifying public benefit entities, pension funds, and certain free zone businesses for activities/income specifically exempted
        """

        return business.has_role(entities.Business.GOVERNMENT) or business.has_role(
            entities.Business.PENSION_FUND
        )
