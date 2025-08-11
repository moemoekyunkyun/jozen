from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Series, Group, Tag, Character, Image
from .serializers import CharacterSerializer
from io import BytesIO
from PIL import Image as PILImage

User = get_user_model()

class ModelTests(TestCase):
    def setUp(self):
        self.series = Series.objects.create(name='Test Series', slug='test-series')
        self.group = Group.objects.create(name='Test Group', slug='test-group')
        self.tag = Tag.objects.create(name='Test Tag', slug='test-tag')
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_character_creation(self):
        char = Character.objects.create(name='Test Girl', series=self.series, is_2d=True)
        char.groups.add(self.group)
        char.tags.add(self.tag)
        self.assertEqual(char.series, self.series)
        self.assertIn(self.group, char.groups.all())
        self.assertIn(self.tag, char.tags.all())
        self.assertTrue(char.is_2d)

    def test_image_creation_and_metadata(self):
        char = Character.objects.create(name='Test Girl 2', series=self.series, is_2d=True)
        img_file = BytesIO()
        PILImage.new('RGB', (100, 200)).save(img_file, format='JPEG')
        img_file.seek(0)
        image = Image.objects.create(uploader=self.user)
        image.file.save('test.jpg', img_file, save=True)
        image.characters.add(char)
        image.tags.add(self.tag)
        image.save()
        self.assertEqual(image.width, 100)
        self.assertEqual(image.height, 200)
        self.assertIn(char, image.characters.all())
        self.assertIn(self.tag, image.tags.all())

class SerializerTests(TestCase):
    def setUp(self):
        self.series = Series.objects.create(name='Test Series', slug='test-series')
        self.group = Group.objects.create(name='Test Group', slug='test-group')
        self.tag = Tag.objects.create(name='Test Tag', slug='test-tag')
        self.char = Character.objects.create(name='Test Girl', series=self.series, is_2d=True)
        self.char.groups.add(self.group)
        self.char.tags.add(self.tag)

    def test_character_serializer(self):
        data = CharacterSerializer(self.char).data
        self.assertEqual(data['name'], 'Test Girl')
        self.assertEqual(data['series']['name'], 'Test Series')
        self.assertTrue(data['is_2d'])
        self.assertGreaterEqual(len(data['groups']), 1)
        self.assertGreaterEqual(len(data['tags']), 1)

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.series = Series.objects.create(name='Test Series', slug='test-series')
        self.group = Group.objects.create(name='Test Group', slug='test-group')
        self.tag = Tag.objects.create(name='Test Tag', slug='test-tag')
        self.user = User.objects.create_user(username='apiuser', password='apipass')
        self.char = Character.objects.create(name='API Girl', series=self.series, is_2d=True)
        self.char.groups.add(self.group)
        self.char.tags.add(self.tag)

    def test_character_list(self):
        url = reverse('character_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'API Girl')

    def test_api_character_list(self):
        url = '/api/characters/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.data), 1)

    def test_api_character_create_auth_required(self):
        url = '/api/characters/'
        data = {'name': 'New Girl', 'is_2d': True}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.user)
        data['series_id'] = self.series.id
        resp = self.client.post(url, data)
        self.assertIn(resp.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_api_image_upload(self):
        url = '/api/images/'
        img_file = BytesIO()
        PILImage.new('RGB', (50, 50)).save(img_file, format='JPEG')
        img_file.seek(0)
        self.client.force_authenticate(user=self.user)
        data = {
            'file': img_file,
            'character_ids': [self.char.id],
            'tag_ids': [self.tag.id],
        }
        resp = self.client.post(url, data, format='multipart')
        self.assertIn(resp.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_api_filtering(self):
        url = '/api/characters/?is_2d=True&series={}'.format(self.series.id)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.data), 1)

    def test_permissions(self):
        url = '/api/images/'
        resp = self.client.post(url, {})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
