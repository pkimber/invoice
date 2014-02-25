# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from datetime import datetime

from django.test import TestCase

from invoice.models import Invoice
from invoice.service import (
    InvoiceCreateBatch,
)
from crm.tests.scenario import (
    default_scenario_crm,
    get_contact_farm,
)
from invoice.tests.scenario import (
    default_scenario_invoice,
    invoice_settings,
)
from login.tests.scenario import (
    default_scenario_login,
    get_user_staff,
    user_contractor,
)


class TestInvoiceCreateBatch(TestCase):

    def setUp(self):
        user_contractor()
        default_scenario_login()
        default_scenario_crm()
        default_scenario_invoice()

    def test_create_invoices(self):
        """Create an invoice"""
        staff = get_user_staff()
        InvoiceCreateBatch().create(staff, datetime(2012, 9, 30))
        invoices = Invoice.objects.filter(
            contact=get_contact_farm()
        )
        self.assertEquals(1, len(invoices))
        invoice = invoices[0]
        self.assertEquals(2, len(invoice.invoiceline_set.all()))

    def test_create_invoices_only_billable_time(self):
        self.assertEquals(
            1,
            Invoice.objects.filter(contact__slug='smallholding').count()
        )
        # there is some un-billed non-chargeable time.  check it isn't
        # invoiced.
        InvoiceCreateBatch().create(get_user_staff(), datetime(2012, 9, 30))
        self.assertEquals(
            1,
            Invoice.objects.filter(contact__slug='smallholding').count()
        )

    def test_create_invoices_do_not_bill_twice(self):
        """Check we can't include the time records more than once"""
        InvoiceCreateBatch().create(get_user_staff(), datetime(2012, 9, 30))
        self.assertEquals(
            1,
            Invoice.objects.filter(contact=get_contact_farm()).count()
        )
        InvoiceCreateBatch().create(get_user_staff(), datetime(2012, 9, 30))
        self.assertEquals(
            1,
            Invoice.objects.filter(contact=get_contact_farm()).count()
        )
