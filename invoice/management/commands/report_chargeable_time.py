# -*- encoding: utf-8 -*-
import collections
import csv

from datetime import date
from dateutil.relativedelta import relativedelta, MO
from django.core.management.base import BaseCommand
from django.utils import timezone

from invoice.models import TimeRecord


class Command(BaseCommand):

    help = "Chargeable time by week"

    def handle(self, *args, **options):
        count = 0
        data = collections.OrderedDict()
        user_names = set()
        qs = TimeRecord.objects.filter(billable=True).order_by('created')
        for item in qs:
            user_names.add(item.user.username)
            monday = item.date_started + relativedelta(weekday=MO(-1))
            if count % 1000:
                self.stdout.write(item.date_started.strftime('%d/%m/%Y'))
            if not monday in data:
                data[monday] = {}
            row = data[monday]
            if not item.user.username in row:
                row[item.user.username] = 0
            row[item.user.username] = row[item.user.username] + item.minutes
            count = count + 1
        user_names = list(user_names)
        user_names.sort()
        file_name = 'chargeable_time_{}.csv'.format(
            timezone.now().strftime('%Y-%m-%d_%H-%M-%S')
        )
        with open(file_name, 'w', newline='') as out:
            csv_writer = csv.writer(out, dialect='excel-tab')
            heading = ['Date']
            for user_name in user_names:
                heading.append(user_name)
            csv_writer.writerow(heading)
            for d, item in data.items():
                row = [d.strftime('%d/%m/%Y')]
                for user_name in user_names:
                    row.append(int(item.get(user_name, 0)))
                csv_writer.writerow(row)
        self.stdout.write("Report written to '{}'...".format(file_name))
