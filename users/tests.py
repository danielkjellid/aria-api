from django.test import TestCase
from django.contrib.auth import get_user_model


class UsersManagersTest(TestCase):

    def test_create_user(self):
        """
        Test creating a normal user.
        """
        User = get_user_model()
        user = User.objects.create_user(email='leonardo@davinci.com', password='supersecretpassword')

        self.assertEqual(user.email, 'leonardo@davinci.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        try:
            # test that we've overridden the default user model
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email='')
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='supersecretpassword')

    def test_create_superuser(self):
        """
        Test creating a superuser.
        """
        User = get_user_model()
        superuser = User.objects.create_superuser(email='claude@monet.com', password='supersecretpassword')

        self.assertEqual(superuser.email, 'claude@monet.com')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

        try:
            self.assertIsNone(superuser.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='claude@monet.com', password='supersecretpassword', is_superuser=False)