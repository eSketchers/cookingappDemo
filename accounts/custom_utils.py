from django.conf import settings

front_end_config = {
    'debug': {
        'FRONT_END_DOMAIN': 'http://localhost:4200/',
        'FRONT_END_CONFIRMATION_URL': 'email-verification?access',
    },
    'live': {
        'FRONT_END_DOMAIN': 'http://dropshipdynamo.com/',
        'FRONT_END_CONFIRMATION_URL': 'email-verification?access',
    }
}


class CustomUtils:
    current_config = front_end_config.get('debug' if settings.DEBUG else 'live')

    def get_frontend_base(self):
        return self.current_config.get('FRONT_END_DOMAIN')

    def get_confirmation_url(self, key):
        return self.get_frontend_base() + self.current_config.get('FRONT_END_CONFIRMATION_URL') + '=' + key


IMAGE_EXT = ['image/png', 'image/jpeg' ]