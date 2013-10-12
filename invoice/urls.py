
from django.conf.urls import (
    patterns, url
)

from .views import (
    ContactInvoiceListView,
    ContactTimeRecordListView,
    invoice_download,
    InvoiceDetailView,
    InvoiceDraftCreateView,
    InvoiceLineCreateView,
    InvoiceLineUpdateView,
    InvoiceListView,
    InvoicePdfUpdateView,
    InvoiceTimeCreateView,
    InvoiceUpdateView,
    TicketTimeRecordListView,
    TimeRecordCreateView,
    TimeRecordListView,
    TimeRecordUpdateView,
)


urlpatterns = patterns(
    '',
    url(regex=r'^contact/(?P<slug>[-\w\d]+)/invoice/$',
        view=ContactInvoiceListView.as_view(),
        name='invoice.contact.list'
        ),
    url(regex=r'^contact/(?P<slug>[-\w\d]+)/time/$',
        view=ContactTimeRecordListView.as_view(),
        name='invoice.time.contact.list'
        ),
    url(regex=r'^create/(?P<slug>[-\w\d]+)/draft/$',
        view=InvoiceDraftCreateView.as_view(),
        name='invoice.create.draft'
        ),
    url(regex=r'^create/(?P<slug>[-\w\d]+)/time/$',
        view=InvoiceTimeCreateView.as_view(),
        name='invoice.create.time'
        ),
    url(regex=r'^$',
        view=InvoiceListView.as_view(),
        name='invoice.list'
        ),
    url(regex=r'^download/(?P<pk>\d+)/$',
        view=invoice_download,
        name='invoice.download'
        ),
    url(regex=r'^invoice/(?P<pk>\d+)/$',
        view=InvoiceDetailView.as_view(),
        name='invoice.detail'
        ),
    url(regex=r'^invoice/(?P<pk>\d+)/line/add/$',
        view=InvoiceLineCreateView.as_view(),
        name='invoice.line.create'
        ),
    url(regex=r'^invoice/(?P<pk>\d+)/line/edit/$',
        view=InvoiceLineUpdateView.as_view(),
        name='invoice.line.update'
        ),
    url(regex=r'^invoice/(?P<pk>\d+)/pdf/$',
        view=InvoicePdfUpdateView.as_view(),
        name='invoice.create.pdf'
        ),
    url(regex=r'^invoice/(?P<pk>\d+)/edit/$',
        view=InvoiceUpdateView.as_view(),
        name='invoice.update'
        ),
    url(regex=r'^ticket/(?P<pk>\d+)/time/$',
        view=TicketTimeRecordListView.as_view(),
        name='invoice.time.ticket.list'
        ),
    url(regex=r'^ticket/(?P<pk>\d+)/time/add/$',
        view=TimeRecordCreateView.as_view(),
        name='invoice.time.create'
        ),
    url(regex=r'^time/$',
        view=TimeRecordListView.as_view(),
        name='invoice.time'
        ),
    url(regex=r'^time/(?P<pk>\d+)/edit/$',
        view=TimeRecordUpdateView.as_view(),
        name='invoice.time.update'
        ),
)
