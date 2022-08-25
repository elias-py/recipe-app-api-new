"""
Tests for the django admin modification.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Test for django admin."""

    def setUp(self):
        """Create a user and an admin."""
        self.user_admin = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="admin12345"
        )
        self.client.force_login(self.user_admin)
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="mypass12345",
            name="my test name"
        )

    def test_list_user(self):
        """Test that users are listed in admin page."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test that user has new fields."""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that can create user."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
