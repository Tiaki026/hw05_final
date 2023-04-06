from django.urls import reverse
from django.test import TestCase
from posts.models import User, Follow
from http import HTTPStatus


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='comment_username')
        cls.author = User.objects.create_user(username='post_author')

    def setUp(self):
        self.client.force_login(self.user)

    def test_authorized_user_follow(self):
        '''Авторизованный пользователь может подписываться на авторов.'''

        follow_count = Follow.objects.count()
        response = self.client.post(
            reverse('posts:profile_follow', args=[self.author.username]))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.author).exists())
        self.assertEqual(follow_count + 1, Follow.objects.count())

    def test_authorized_user_unfollow(self):
        '''Авторизованный пользователь может отписываться от авторов.'''

        Follow.objects.create(user=self.user, author=self.author)
        follow_count = Follow.objects.count()
        response = self.client.post(
            reverse('posts:profile_unfollow', args=[self.author.username]))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.author).exists())
        self.assertEqual(follow_count - 1, Follow.objects.count())
