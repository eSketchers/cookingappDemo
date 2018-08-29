from django.core.management.base import BaseCommand, CommandError
import datetime
import time
import csv
from accounts.models import User
import os, hashlib
from accounts.models import EmailAddress
from accounts.serializers import CustomUserCreateSerializer


class Command(BaseCommand):
    help = 'Create User with temporary password and send reset link in email.'

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
            return 0
        print("Executing....")
        start_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        print('The script start time: {0}'.format(start_time))

        try:
            with open(file_name, encoding='utf-8', errors='ignore') as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')
                headers = next(readCSV)
                try:
                    for row in readCSV:
                        data = dict(email=row[3])
                        user_data = dict(first_name=row[1],
                                         last_name=row[2],
                                         email=row[3])
                        user = self.create_temp_user(user_data)
                        if user is not None:
                            serializer = CustomUserCreateSerializer(data=data)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            # Return the success message
                            print(data['email'] + ' ' + "account created Successfully.")
                            continue
                        else:
                            print(data['email']+' '+"Already Exists.")
                            continue
                except IndexError:
                    print("Warning: Get Empty row in csv so its list index is out of range.")
                    pass
        except Exception as e:
            print("Error Occur:"+str(e))
            raise CommandError(e)

        end_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        total_time = (datetime.datetime.strptime(end_time, '%H:%M:%S') - datetime.datetime.strptime(start_time, '%H:%M:%S'))
        self.stdout.write('The script took {0} second !'.format(total_time))

    def create_temp_user(self, data):
        user = User.objects.filter(email=data['email'])
        if user.exists() is False:
            random_data = os.urandom(128)
            temp_pwd = hashlib.md5(random_data).hexdigest()[:8]
            user = User.objects.create_user(email=data['email'],password=temp_pwd)
            user.first_name=data['first_name']
            user.last_name=data['last_name']
            user.save()

            email_address = EmailAddress()
            email_address.user = user
            email_address.verified = True
            email_address.primary = True
            email_address.email = data['email']
            email_address.save()
            return user
        return None