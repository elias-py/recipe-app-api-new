"""
Test for tags API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core import models
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Return the detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='email@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsAPITests(TestCase):
    """Test unauthenticated api requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticate_request(self):
        """Test that unauthenticated user get unauthorized."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Test authenticated api requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retreiving all tags."""
        models.Tag.objects.create(user=self.user, name='Tag1')
        models.Tag.objects.create(user=self.user, name='Tag2')

        res = self.client.get(TAGS_URL)

        tags = models.Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_for_user(self):
        """Test retreiving tags is limited to authenticated user."""
        user2 = create_user(email="user2@example.com", password="testpass123")
        models.Tag.objects.create(user=user2, name="Tag1")
        tag = models.Tag.objects.create(user=self.user, name="Tag2")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(tag.name, res.data[0]['name'])
        self.assertEqual(tag.id, res.data[0]['id'])

    def test_update_tag(self):
        """Test updating a tag with PATCH."""
        tag = models.Tag.objects.create(name="My tag", user=self.user)

        payload = {"name": "My other tag"}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = models.Tag.objects.create(user=self.user, name="My Tag")

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = models.Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags to those assigned to recipes."""
        tag1 = models.Tag.objects.create(user=self.user, name='Apples')
        tag2 = models.Tag.objects.create(user=self.user, name='Turkey')
        recipe = models.Recipe.objects.create(
            title='Apple Crumble',
            price=Decimal('4.50'),
            time_minutes=5,
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list."""
        tag1 = models.Tag.objects.create(user=self.user, name='Tag1')
        models.Tag.objects.create(user=self.user, name='Tag2')
        recipe = models.Recipe.objects.create(
            user=self.user,
            title='My Recipe',
            time_minutes=4,
            price=Decimal('9.32')
        )
        recipe2 = models.Recipe.objects.create(
            user=self.user,
            title='My Recipe 2',
            time_minutes=3,
            price=Decimal('5.32')
        )
        recipe.tags.add(tag1)
        recipe2.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)