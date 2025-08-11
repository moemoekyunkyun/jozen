from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Character, Series, Group, Tag, Image, SiteSetting


class BasicViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test data
        self.series = Series.objects.create(
            name='Test Series',
            description='A test series'
        )
        
        self.group = Group.objects.create(
            name='Test Group',
            description='A test group'
        )
        
        self.tag = Tag.objects.create(
            name='test-tag',
            description='A test tag'
        )
        
        self.character = Character.objects.create(
            name='Test Character',
            description='A test character',
            series=self.series,
            is_2d=True
        )
        self.character.groups.add(self.group)
        self.character.tags.add(self.tag)

    def test_character_list_view(self):
        """Test that character list view loads"""
        response = self.client.get(reverse('character_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Character')

    def test_character_detail_view(self):
        """Test that character detail view loads"""
        response = self.client.get(
            reverse('character_detail', kwargs={'slug': self.character.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Character')

    def test_home_page_redirects_to_character_list(self):
        """Test that home page redirects to character list"""
        response = self.client.get('/')
        self.assertRedirects(response, reverse('character_list'))

    def test_search_functionality(self):
        """Test search functionality"""
        response = self.client.get(reverse('character_list'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Character')

    def test_type_filter(self):
        """Test 2D/3D filter functionality"""
        response = self.client.get(reverse('character_list'), {'type': '2d'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Character')


class ModelsTest(TestCase):
    def test_character_creation(self):
        """Test character model creation"""
        series = Series.objects.create(name='Test Series')
        character = Character.objects.create(
            name='Test Char',
            series=series,
            is_2d=True
        )
        self.assertEqual(character.name, 'Test Char')
        self.assertEqual(character.series, series)
        self.assertTrue(character.is_2d)

    def test_series_str_representation(self):
        """Test series string representation"""
        series = Series.objects.create(name='Test Series')
        self.assertEqual(str(series), 'Test Series')

    def test_group_str_representation(self):
        """Test group string representation"""
        group = Group.objects.create(name='Test Group')
        self.assertEqual(str(group), 'Test Group')

    def test_tag_str_representation(self):
        """Test tag string representation"""
        tag = Tag.objects.create(name='test-tag')
        self.assertEqual(str(tag), 'test-tag')


class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_login_view(self):
        """Test login view"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_view(self):
        """Test register view"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_user_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get(reverse('user_dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('user_dashboard')}")


class AdminTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        self.client.login(username='admin', password='adminpass123')

    def test_admin_panel_access(self):
        """Test that admin panel is accessible to superusers"""
        response = self.client.get(reverse('admin_panel'))
        self.assertEqual(response.status_code, 200)

    def test_admin_users_view(self):
        """Test that admin users view is accessible"""
        response = self.client.get(reverse('admin_users'))
        self.assertEqual(response.status_code, 200)
