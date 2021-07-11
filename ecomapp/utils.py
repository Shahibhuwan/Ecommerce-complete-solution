from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


class MyPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp)
        )


password_reset_token = MyPasswordResetTokenGenerator()

#tokengenerator is used to generate unique tokens for password reset for by django