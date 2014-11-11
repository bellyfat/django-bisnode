from datetime import datetime

from django.db import models

from money.contrib.django.models.fields import MoneyField

from .constants import (COMPANY_RATING_REPORT, COMPANY_STANDARD_REPORT,
                        RATING_CHOICES, OPERATION_CHOICES, MANAGEMENT_CHOICES,
                        FINANCES_CHOICES, SOLVENCY_CHOICES)
from .bisnode import get_bisnode_company_report


def bisnode_date_to_date(bisnode_date):
    formatted_datetime = datetime.strptime(bisnode_date, "%Y%m%d")
    return formatted_datetime.date()


class BisnodeCompanyReport(models.Model):

    last_updated = models.DateTimeField(auto_now=True)

    # General Company Data
    company_name = models.CharField(max_length=100, blank=True)
    rating = models.CharField(max_length=3, choices=RATING_CHOICES, blank=True)
    date_of_rating = models.DateField(blank=True, null=True)
    registration_date = models.DateField(blank=True, null=True)
    history_and_operation = models.CharField(
        max_length=6, choices=OPERATION_CHOICES, blank=True)
    management = models.CharField(
        max_length=6, choices=MANAGEMENT_CHOICES, blank=True)
    finances = models.CharField(
        max_length=6, choices=FINANCES_CHOICES, blank=True)
    solvency = models.CharField(
        max_length=6, choices=SOLVENCY_CHOICES, blank=True)
    number_of_employees = models.IntegerField(null=True, blank=True)
    share_capital = MoneyField(
        default=0, default_currency="SEK", decimal_places=2, max_digits=14)

    def create_rating_report(self, organization_number):
        rating_report = get_bisnode_company_report(
            report_type=COMPANY_RATING_REPORT,
            organization_number=organization_number)
        self._update_general_company_data(rating_report)
        self.save()

    def create_standard_report(self, organization_number):
        standard_report = get_bisnode_company_report(
            report_type=COMPANY_STANDARD_REPORT,
            organization_number=organization_number)
        self._update_general_company_data(standard_report)
        self.save()

    def _update_general_company_data(self, report):
        company_data = report.generalCompanyData[0]
        self.company_name = company_data.companyName
        self.rating = company_data.ratingCode
        self.date_of_rating = bisnode_date_to_date(company_data.dateOfRating)
        self.registration_date = bisnode_date_to_date(company_data.dateReg)
        self.history_and_operation = company_data.historyCode
        self.management = company_data.shareholdersCode
        self.finances = company_data.financeCode
        self.solvency = company_data.abilityToPay1
        self.number_of_employees = company_data.noOfEmployees1
        self.share_capital.amount = float(company_data.shareCapital)
