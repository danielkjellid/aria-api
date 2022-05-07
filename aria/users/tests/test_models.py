import pytest


class TestUsersModels:
    def test_create_user(self, django_user_model):
        """
        Test creation of users and check that all fields are
        set correctly.
        """

        user = django_user_model.objects.create_user(
            email="leonardo@davinci.com", password="supersecretpassword"
        )

        assert user.email == "leonardo@davinci.com"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

        with pytest.raises(TypeError):
            django_user_model.objects.create_user()
            django_user_model.objects.create_user(email="")

        with pytest.raises(ValueError):
            django_user_model.objects.create_user(
                email="", password="supersecretpassword"
            )

    def test_create_superuser(self, django_user_model):
        """
        Test creation of superusers and check that all fields are
        set correctly.
        """

        superuser = django_user_model.objects.create_superuser(
            email="leonardo@davinci.com", password="supersecretpassword"
        )

        assert superuser.email == "leonardo@davinci.com"
        assert superuser.is_active is True
        assert superuser.is_staff is True
        assert superuser.is_superuser is True

        with pytest.raises(TypeError):
            django_user_model.objects.create_superuser()
            django_user_model.objects.create_superuser(email="")

        with pytest.raises(ValueError):
            django_user_model.objects.create_superuser(
                email="", password="supersecretpassword"
            )
            django_user_model.objects.create_superuser(
                email="leonardo@davinci.com",
                password="supersecretpassword",
                is_staff=False,
                is_superuser=False,
            )
            django_user_model.objects.create_superuser(
                email="leonardo@davinci.com",
                password="supersecretpassword",
                is_staff=True,
                is_superuser=False,
            )
