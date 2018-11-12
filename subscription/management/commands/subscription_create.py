import logging
from django.core.management.base import BaseCommand, CommandError
import datetime
import time
import csv
from accounts.models import User
import os, hashlib
from accounts.models import EmailAddress
from accounts.serializers import CustomUserCreateSerializer
from subscription.models import SubscriptionPlan

# Get an instance of a logger
logger = logging.getLogger(__name__)


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
                                         email=row[3],
                                         address_1=row[4],
                                         address_2=row[5],
                                         telephone=row[10],
                                         sub_id=row[26],
                                         )
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

        _plan_id = 'plan_DvilNwjmPs3AsK'
        _sub_id = None
        try:
            _sub_id = data['sub_id']
        except Exception as e:
            pass

        if not user.exists():
            random_data = os.urandom(128)
            temp_pwd = hashlib.md5(random_data).hexdigest()[:8]

            user = User.objects.create_user(email=data['email'],password=temp_pwd, **{'_plan_id':_plan_id, '_sub_id': _sub_id})
            user.first_name=data['first_name']
            user.last_name=data['last_name']

            user.address_1=data['address_1']
            user.address_2=data['address_2']
            user.telephone=data['telephone']

            user.save()

            email_address = EmailAddress()
            email_address.user = user
            email_address.verified = True
            email_address.primary = True
            email_address.email = data['email']
            email_address.save()
            return user

        else:
            if _sub_id:
                try:
                    plan = SubscriptionPlan.objects.filter(plan_id=_plan_id).first()
                    user_sub = user.first().subscription.get(is_active=True)
                    if user_sub:
                        user_sub.subscription = _sub_id
                        user_sub.plan = plan
                        user_sub.save()
                    else:
                        logger.error("no active subscription found for -{0}".format(user.email))
                except Exception as e:
                    logger.error("something bad happened -{0} -- {1}".format(user.email, e.args))

            else:
                logger.error("no sub_id found to update info for -{0}".format(user.email))
        return None