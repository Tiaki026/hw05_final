from django.test import Client, TestCase
from typing import List
from posts.models import Post, Group, User
from django.core.cache import cache
ALL_POST = 13
TEN_POSTS = 10
THREE_POSTS = 3


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Paginator тестовая группа',
            slug='urls-group-slug',
            description='Группа для проверки работы URLs',
        )

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='TestUser')
        posts_set: List[Post] = []
        for i in range(ALL_POST):
            posts_set.append(
                Post(
                    text=f'Автоматически сгенерированный пост номер {i}',
                    author=self.user,
                    group=self.group,
                )
            )
        Post.objects.bulk_create(posts_set)
        cache.clear()

    def test_paginator_on_pages(self):
        '''Тестируем paginator с разным количеством постов'''

        group_page = f'/group/{self.group.slug}/'
        main_page = '/'
        second_page = '?page=2'
        profile_page = f'/profile/{self.user.username}/'
        posts_per_page = {
            TEN_POSTS: (
                main_page,
                group_page,
                profile_page,
            ),
            THREE_POSTS: (
                main_page + second_page,
                group_page + second_page,
                profile_page + second_page
            )
        }
        for number_posts, urls in posts_per_page.items():
            for url in urls:
                with self.subTest(url=url):
                    self.assertEqual(
                        len(self.client.get(url).context['page_obj']),
                        number_posts
                    )
