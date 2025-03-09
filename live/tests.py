from django.test import TestCase
from django.contrib.auth.models import User
from .models import Stream, Message, Like, Comment
from rest_framework.test import APIClient
from rest_framework import status
import uuid

class StreamModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.stream = Stream.objects.create(
            user=self.user,
            stream_key=str(uuid.uuid4()),
            stream_title='Test Stream',
            is_active=True
        )

    def test_stream_creation(self):
        self.assertEqual(self.stream.stream_title, 'Test Stream')
        self.assertTrue(self.stream.is_active)

    def test_activate_stream(self):
        self.stream.deactivate()
        self.assertFalse(self.stream.is_active)
        self.stream.activate()
        self.assertTrue(self.stream.is_active)

    def test_increment_view_count(self):
        initial_count = self.stream.view_count
        self.stream.increment_view_count()
        self.assertEqual(self.stream.view_count, initial_count + 1)

    def test_decrement_view_count(self):
        self.stream.increment_view_count()
        initial_count = self.stream.view_count
        self.stream.decrement_view_count()
        self.assertEqual(self.stream.view_count, initial_count - 1)


class StreamAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.stream = Stream.objects.create(
            user=self.user,
            stream_key=str(uuid.uuid4()),
            stream_title='Test Stream',
            is_active=True
        )

    def test_start_stream(self):
        response = self.client.post('/live/start/', {'stream_title': 'New Stream'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['stream_title'], 'New Stream')

    def test_stop_stream(self):
        response = self.client.post(f'/live/stop/{self.stream.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.stream.refresh_from_db()
        self.assertFalse(self.stream.is_active)

    def test_list_streams(self):
        response = self.client.get('/live/streams/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['stream_title'], 'Test Stream')


class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.stream = Stream.objects.create(
            user=self.user,
            stream_key=str(uuid.uuid4()),
            stream_title='Test Stream',
            is_active=True
        )
        self.message = Message.objects.create(
            stream=self.stream,
            user=self.user,
            content='Test Message'
        )

    def test_message_creation(self):
        self.assertEqual(self.message.content, 'Test Message')
        self.assertEqual(self.message.stream, self.stream)
        self.assertEqual(self.message.user, self.user)


class LikeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.stream = Stream.objects.create(
            user=self.user,
            stream_key=str(uuid.uuid4()),
            stream_title='Test Stream',
            is_active=True
        )
        self.like = Like.objects.create(
            stream=self.stream,
            user=self.user
        )

    def test_like_creation(self):
        self.assertEqual(self.like.stream, self.stream)
        self.assertEqual(self.like.user, self.user)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.stream = Stream.objects.create(
            user=self.user,
            stream_key=str(uuid.uuid4()),
            stream_title='Test Stream',
            is_active=True
        )
        self.comment = Comment.objects.create(
            stream=self.stream,
            user=self.user,
            content='Test Comment'
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.content, 'Test Comment')
        self.assertEqual(self.comment.stream, self.stream)
        self.assertEqual(self.comment.user, self.user)