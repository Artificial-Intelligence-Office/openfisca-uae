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
        taxable_income = corporate_tax_rate.calc(person("taxable_income", period))

        # exemption rules
        is_government = person("is_government", period)
        is_person_exempt = person("exempt_person", period)
        is_small_business = (
            person("revenue", period) <= parameters(period).benefits.small_business
        )

        is_exempt = (
            np.logical_not(is_government)
            * np.logical_not(is_person_exempt)
            * np.logical_not(is_small_business)
        )

        return taxable_income * is_exempt


class is_government(Variable):
    value_type = bool
    entity = entities.Person
    definition_period = periods.YEAR
    label = "A government entity"
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"


class taxable_income(Variable):
    value_type = float
    entity = entities.Person
    definition_period = periods.YEAR
    label = (
        "The income that is subject to Corporate Tax under Federal Decree Law No. 47"
    )
    reference = "https://mof.gov.ae/wp-content/uploads/2022/12/Federal-Decree-Law-No.-47-of-2022-EN.pdf"

    # Can add a formula later


class revenue(Variable):
    value_type = float
    entity = entities.Person
    definition_period = periods.YEAR
    label = "The gross amount of income derived"
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


class income_tax(Variable):
    value_type = float
    entity = entities.Person
    definition_period = periods.MONTH
    label = "Income tax"
    reference = (
        "https://law.gov.example/income_tax"  # Always use the most official source
    )

    def formula(person, period, parameters):
        """
        Income tax.

        The formula to compute the income tax for a given person at a given period
        """
        return person("salary", period) * parameters(period).taxes.income_tax_rate


class social_security_contribution(Variable):
    value_type = float
    entity = entities.Person
    definition_period = periods.MONTH
    label = "Progressive contribution paid on salaries to finance social security"
    reference = "https://law.gov.example/social_security_contribution"  # Always use the most official source

    def formula(person, period, parameters):
        """
        Social security contribution.

        The social_security_contribution is computed according to a marginal scale.
        """
        salary = person("salary", period)
        scale = parameters(period).taxes.social_security_contribution

        return scale.calc(salary)


class housing_tax(Variable):
    value_type = float
    entity = entities.Household
    definition_period = periods.YEAR  # This housing tax is defined for a year.
    label = "Tax paid by each household proportionally to the size of its accommodation"
    reference = (
        "https://law.gov.example/housing_tax"  # Always use the most official source
    )

    def formula(household, period, parameters):
        """
        Housing tax.

        The housing tax is defined for a year, but depends on the `accommodation_size` and `housing_occupancy_status` on the first month of the year.
        Here period is a year. We can get the first month of a year with the following shortcut.
        To build different periods, see https://openfisca.org/doc/coding-the-legislation/35_periods.html#calculate-dependencies-for-a-specific-period
        """
        january = period.first_month
        accommodation_size = household("accommodation_size", january)

        tax_params = parameters(period).taxes.housing_tax
        tax_amount = max_(
            accommodation_size * tax_params.rate, tax_params.minimal_amount
        )

        # `housing_occupancy_status` is an Enum variable
        occupancy_status = household("housing_occupancy_status", january)
        HousingOccupancyStatus = (
            occupancy_status.possible_values
        )  # Get the enum associated with the variable
        # To access an enum element, we use the `.` notation.
        tenant = occupancy_status == HousingOccupancyStatus.tenant
        owner = occupancy_status == HousingOccupancyStatus.owner

        # The tax is applied only if the household owns or rents its main residency
        return (owner + tenant) * tax_amount
