from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_unexisting_page = '/unexisting_page/'
        cls.user_username_value = 'Тестовый автор'
        cls.user = User.objects.create_user(username=cls.user_username_value)
        cls.user_not_author = User.objects.create_user(
            username='Тестовый гость'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись',
        )
        cls.group_slug_value = 'Test_group'
        cls.group = Group.objects.create(
            title='Тестовая группаэ',
            slug=cls.group_slug_value,
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.guest_client.force_login(self.user_not_author)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.url_names = {
            '/',
            f'/group/{self.group_slug_value}/',
            f'/profile/{self.user_username_value}/',
            f'/posts/{self.post.id}/',
        }

    def test_autorized_urls_access(self):
        """Страницы доступные авторизованным пользователям."""

        for address in self.url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_urls_access(self):
        """Страницы доступные не авторизованному пользователю."""

        for address in self.url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_not_author(self):
        """Редирект при попытке редактирования поста не автором."""

        response = self.guest_client.get(
            f'/posts/{self.post.id}/edit/', follow=True
        )
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_page_not_found(self):
        """Страница не найденна."""

        response = self.client.get(self.url_unexisting_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
