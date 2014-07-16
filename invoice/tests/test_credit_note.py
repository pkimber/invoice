# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from .factories import (
    InvoiceFactory,
    InvoiceLineFactory,
    InvoiceSettingsFactory,
)
from invoice.service import InvoiceCreate


class TestCreditNote(TestCase):

    def _create_credit_note(self):
        credit_note = InvoiceFactory()
        credit_note.full_clean()
        line = InvoiceLineFactory(
            invoice=credit_note,
            price=Decimal('1.01'),
            quantity=Decimal('-1'),
        )
        line.full_clean()
        return credit_note

    def test_factory(self):
        """ Create a simple credit note."""
        credit_note = InvoiceFactory()
        credit_note.full_clean()
        InvoiceLineFactory(invoice=credit_note, price=Decimal('10.01'))
        line = InvoiceLineFactory(invoice=credit_note, price=Decimal('0.99'))
        line.full_clean()
        self.assertEqual(Decimal('11.00'), credit_note.net)

    def test_no_negative_price(self):
        invoice = InvoiceFactory()
        line = InvoiceLineFactory(invoice=invoice, price=Decimal('-10.01'))
        self.assertRaises(
            ValidationError,
            line.full_clean,
        )

    def test_allow_negative_quantity(self):
        credit_note = self._create_credit_note()
        self.assertEqual(Decimal('-1.01'), credit_note.net)

    def test_description(self):
        credit_note = self._create_credit_note()
        self.assertEqual('Credit note', credit_note.description)

    def test_credit_note(self):
        InvoiceSettingsFactory()
        credit = self._create_credit_note()
        InvoiceCreate().create(credit.user, credit.contact, date.today())
