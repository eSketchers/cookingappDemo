from django.core.management.base import BaseCommand, CommandError
import datetime
from core.models import CustomProduct
from datetime import date


class Command(BaseCommand):
    help = 'Show hot products on their released date.'

    def handle(self, *args, **options):
        print("Executing....")
        start_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        print('Task start time: {0} '.format(start_time))
        today = date.today()
        products = CustomProduct.objects.filter(is_active=False,released_date__year=today.year, released_date__month=today.month, released_date__day=today.day)
        for prod in products:
            prod.is_active = True
            print(prod.title + ' ' + " is released on " + prod.released_date)
            print(prod.title+' '+" is released succesfully. "+today)
            prod.save()
        end_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        total_time = (datetime.datetime.strptime(end_time, '%H:%M:%S') - datetime.datetime.strptime(start_time, '%H:%M:%S'))
        self.stdout.write('The task took {0} second !'.format(total_time))