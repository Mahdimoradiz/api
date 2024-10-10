from django.test import TestCase
from .models import Post
from django.urls import reverse
from django.contrib.auth.models import User


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.post = Post.objects.create(
            user=self.user,
            description="Test description",
            file='1'
        )

    def test_post_creation(self):
        self.assertIsInstance(self.post, Post)
        self.assertEqual(self.post.user.username, 'testuser')
        self.assertEqual(self.post.description, 'Test description')
        self.assertEqual(self.post.file, '1')
        
    def test_post_str(self):
        self.assertEqual(str(self.post), self.post.user.username)


class PostViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.post = Post.objects.create(
            user=self.user,
            description="Test description",
            file='1'
        )

    def test_view_url_location(self):
        response = self.client.get('/post/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_name(self):
        response = self.client.get(reverse('post_list_view'))
        self.assertEqual(response.status_code, 200) 
