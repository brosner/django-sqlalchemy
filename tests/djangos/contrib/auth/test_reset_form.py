from django_sqlalchemy.test import *

from django.core import mail
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm

class TestPasswordResetForm(object):
    def test_valid_user(self):
        data = {
            'email': 'nonexistent@example.com',
        }
        form = PasswordResetForm(data)
        assert_equal(form.is_valid(), False)
        assert_equal(form["email"].errors, [u"That e-mail address doesn't have an associated user account. Are you sure you've registered?"])
    
    def test_email(self):
        # TODO: remove my email address from the test ;)
        User.objects.create_user('atestuser', 'atestuser@example.com', 'test789')
        data = {
            'email': 'atestuser@example.com',
        }
        form = PasswordResetForm(data)
        assert_equal(form.is_valid(), True)
        # TODO: look at why using contrib.sites breaks other tests
        form.save(domain_override="example.com")
        assert_equal(len(mail.outbox), 1)
        assert_equal(mail.outbox[0].subject, u'Password reset on example.com')
        # TODO: test mail body. need to figure out a way to get the password in plain text
        # self.assertEqual(mail.outbox[0].body, '')
