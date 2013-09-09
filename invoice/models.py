from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.timesince import timeuntil

import reversion

from base.model_utils import TimeStampedModel
from base.singleton import SingletonModel
from crm.models import (
    Contact,
    Ticket,
)

# We want attachments to be stored in a private location and NOT available to
# the world at a public URL.  The idea for this came from:
# http://nemesisdesign.net/blog/coding/django-private-file-upload-and-serving/
# and
# https://github.com/johnsensible/django-sendfile
fs = FileSystemStorage(location=settings.SENDFILE_ROOT)


class Invoice(TimeStampedModel):
    """
    From Notice 700 The VAT Guide, 16.3.1 General

    VAT invoices must show:
    - an identifying number, which is from a series that is unique and
      sequential;
    - your name, address and VAT registration number;
    - the time of supply (tax point);
    - date of issue (if different to the time of supply);
    - your customer's name (or trading name) and address;
    - a description which identifies the goods or services supplied; and
    - the unit price (see paragraph 16.3.2).

    For each description, you must show the:
    - quantity of goods or extent of the services;
    - charge made, excluding VAT;
    - rate of VAT;
    - total charge made, excluding VAT;
    - rate of any cash discount offered; and
    - total amount of VAT charged, shown in sterling.
    """
    date_created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name='Created'
    )
    invoice_date = models.DateField()
    contact = models.ForeignKey(Contact)
    pdf = models.FileField(
        upload_to='invoice/%Y/%m/%d', storage=fs, blank=True
    )

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'

    def get_absolute_url(self):
        return reverse('crm.invoice.detail', args=[self.pk])

    def _gross(self):
        totals = self.invoiceline_set.aggregate(
            models.Sum('net'), models.Sum('vat')
        )
        return (totals['net__sum'] or Decimal()) + (totals['vat__sum'] or Decimal())
    gross = property(_gross)

    def _invoice_number(self):
        return '{:06d}'.format(self.pk)
    invoice_number = property(_invoice_number)

    def _net(self):
        totals = self.invoiceline_set.aggregate(models.Sum('net'))
        return totals['net__sum'] or Decimal()
    net = property(_net)

reversion.register(Invoice)


class InvoiceSettings(SingletonModel):
    vat_rate = models.DecimalField(
        max_digits=8, decimal_places=2,
        help_text="e.g. 0.175 to charge VAT at 17.5 percent",
    )
    vat_number = models.CharField(max_length=12, blank=True)
    name_and_address = models.TextField()
    phone_number = models.CharField(max_length=100)
    footer = models.TextField()

    class Meta:
        verbose_name = 'Invoice print settings'

    def __unicode__(self):
        return unicode("{}, Phone {}, VAT {}".format(
            ' '.join(self.name_and_address.split('\n')),
            self.phone_number,
            self.vat_rate,
        ))

reversion.register(InvoiceSettings)


class InvoiceLine(TimeStampedModel):
    """
    Invoice line.
    Line numbers for each invoice increment from 1
    Line total can be calculated by adding the net and vat amounts
    """
    invoice = models.ForeignKey(Invoice)
    line_number = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=6, decimal_places=2)
    units = models.CharField(max_length=5)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    net = models.DecimalField(max_digits=8, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=3)
    vat = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'Invoice line'
        verbose_name_plural = 'Invoice lines'
        unique_together = ('invoice', 'line_number')

    def save(self, *args, **kwargs):
        self.net = self.price * self.quantity
        self.vat = self.price * self.quantity * self.vat_rate
        # Call the "real" save() method.
        super(InvoiceLine, self).save(*args, **kwargs)

    def _gross(self):
        return self.net + self.vat
    gross = property(_gross)

    def _has_time_record(self):
        try:
            self.timerecord
            return True
        except TimeRecord.DoesNotExist:
            return False
    has_time_record = property(_has_time_record)

reversion.register(InvoiceLine)


class TimeRecord(TimeStampedModel):
    """Simple time recording"""
    ticket = models.ForeignKey(Ticket)
    user = models.ForeignKey(User)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date_started = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    billable = models.BooleanField()
    invoice_line = models.OneToOneField(InvoiceLine, blank=True, null=True)

    class Meta:
        ordering = ['date_started', 'start_time']
        verbose_name = 'Time record'
        verbose_name_plural = 'Time records'

    def __unicode__(self):
        return unicode("{}: {}: {}: {}".format(
            self.title,
            self.date_started,
            self.start_time,
            self.end_time
        ))

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('End time must be after the start time')

    def delta(self):
        return self._end_date_time() - self._date_started_time()

    def delta_as_string(self):
        return timeuntil(self._end_date_time(), self._date_started_time())

    def get_absolute_url(self):
        return reverse('invoice.time.ticket.list', args=[self.ticket.pk])

    def _end_date_time(self):
        return datetime.combine(self.date_started, self.end_time)

    def _invoice_quantity(self):
        """
        Convert the time in minutes into hours expressed as a decimal
        e.g. 1 hour, 30 minutes = 1.5.  This figure will be used on invoices.
        """
        return Decimal(self._timedelta_minutes()) / Decimal('60')
    invoice_quantity = property(_invoice_quantity)

    def _date_started_time(self):
        return datetime.combine(self.date_started, self.start_time)

    def _timedelta_minutes(self):
        """ Convert the time difference into minutes """
        td = self.delta()
        return td.days * 1440 + td.seconds / 60

reversion.register(TimeRecord)
