from django.test import TestCase
from profiles.models import Profile
from user.models import User
from .serializers import ProfileSerializer


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.profile = Profile.objects.create(
            user=self.user,
            username="testprofile",
            bio="This is a test bio",
        )

    def test_profile_creation(self):
        self.assertIsInstance(self.profile, Profile)
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.username, 'testprofile')
        self.assertEqual(self.profile.slug, 'testprofile')
        self.assertEqual(self.profile.bio, 'This is a test bio')
        self.assertEqual(self.profile.followers, 0)
        self.assertEqual(self.profile.following, 0)
        
    def test_profile_str(self):
        self.assertEqual(str(self.profile), self.profile.user.username)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.profile = Profile.objects.create(
            user=self.user,
            username="testprofile",
            bio="This is a test bio",
        )

    def test_view_url_location(self):
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 404)
        
        

class ProfileSerializerTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

        self.profile1 = Profile.objects.create(user=self.user1)
        self.profile2 = Profile.objects.create(user=self.user2)

        self.profile1.followers.add(self.user2)
        self.profile2.following.add(self.user1)

    def test_followers_count(self):
        serializer = ProfileSerializer(self.profile1)
        self.assertEqual(serializer.data['followers_count'], '1.0K') 

    def test_following_count(self):
        serializer = ProfileSerializer(self.profile2)
        self.assertEqual(serializer.data['following_count'], '1.0K')  
