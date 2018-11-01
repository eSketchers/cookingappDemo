from rest_framework import serializers

from accounts.serializers import CustomUserDetailsSerializer
from .models import *


class SubscriptionSerializer(serializers.ModelSerializer):
    # user = CustomUserDetailsSerializer(read_only=True)

    class Meta:
        model = Subscription
        depth = 1
        # fields = '__all__'
        exclude = ('user', )