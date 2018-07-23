# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import csv
import datetime
from core.models import Influencer


class Command(BaseCommand):
    help = 'Insert influencer in database from csv file.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file-path', dest='file-path', required=True,
            help='Provide file to insert.',
        )

    def handle(self, *args, **options):
        if options['file-path']:
            file_name = options['file-path']
        else:
            print("Enter file path with command.")
            return
        print("Executing....")
        start_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        print('The script start time: {0}'.format(start_time))

        try:
            with open(file_name, encoding='utf-8', errors='ignore') as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')
                for row in readCSV:
                    if row[0].startswith('https://'):
                        Influencer.objects.create(url=row[0],type=row[1])
                    else:
                        link = "https://"+row[0]
                        Influencer.objects.create(url=link, type=row[1])
        except Exception as e:
            print("Error Occur:")
            raise CommandError(e)

        end_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        total_time = (datetime.datetime.strptime(end_time, '%H:%M:%S') - datetime.datetime.strptime(start_time, '%H:%M:%S'))
        self.stdout.write('The script took {0} second !'.format(total_time))
