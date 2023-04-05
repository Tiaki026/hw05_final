import tempfile
import shutil
from django.urls import reverse
from django.test import Client, TestCase, override_settings
from django.conf import settings
from posts.models import Post, User, Group
from django.core.cache import cache


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CacheIndexTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group-slug',
            description='Тестовое описание',
        )
        cls.user = User.objects.create_user(
            username='author'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(
            TEMP_MEDIA_ROOT,
            ignore_errors=True
        )

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user)
        cache.clear()

    def test_cache_index(self):
        '''Проверка кэша для index.'''

        response = self.authorized_author.get(reverse('posts:index'))
        Post.objects.all().delete()
        response_2 = self.authorized_author.get(reverse('posts:index'))
        self.assertEqual(response.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_author.get(reverse('posts:index'))
        self.assertNotEqual(response_2.content, response_3.content)
