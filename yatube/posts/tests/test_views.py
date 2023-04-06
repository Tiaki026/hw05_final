from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from posts.models import Post, Group, User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='TestAuthor'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='urls-group-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.user,
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group_empty = Group.objects.create(
            title='Тестовая пустая группа',
            slug='empty-group-slug',
        )

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(PostsViewsTests.user)
        cache.clear()

    def test_views_use_correct_template(self):
        '''Проверка правильности html-шаблонов.'''

        templates_url_names = {
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:index'): 'posts/index.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_post(self, compared_post):
        self.assertEqual(compared_post.text, self.post.text)
        self.assertEqual(compared_post.group.title, self.group.title)
        self.assertEqual(compared_post.author, self.user)
        self.assertEqual(compared_post.image, self.post.image)

    def test_index_page_sends_proper_context(self):
        '''Проверка контекста главной страницы.'''

        form_data = {
            'text': 'Тестовый текст под картинкой',
            'image': self.uploaded,
        }
        response = self.authorized_author.get(
            reverse('posts:index'),
            data=form_data,
            follow=True
            )
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_group_posts_page_sends_proper_context(self):
        '''Проверка контекста страницы группы'''

        form_data = {
            'text': 'Тестовый текст под картинкой',
            'image': self.uploaded,
        }
        response = self.authorized_author.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            data=form_data,
            follow=True
        )
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_profile_page_sends_proper_context(self):
        '''Проверка контекста страницы профиля'''

        form_data = {
            'text': 'Тестовый текст под картинкой',
            'image': self.uploaded,
        }
        response = self.authorized_author.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
            data=form_data,
            follow=True
        )
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_post_detail_page_sends_proper_context(self):
        '''Проверка контекста страницы поста.'''

        form_data = {
            'text': 'Тестовый текст под картинкой',
            'image': self.uploaded,
        }
        response = self.authorized_author.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        post = response.context['posts']
        self.check_post(post)

    def test_post_create_page_sends_proper_context(self):
        '''Проверка контекста создания поста.'''

        fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        response = self.authorized_author.get(
            reverse('posts:post_create')
        )
        self.assertIn(
            'is_edit',
            response.context
        )
        self.assertFalse(
            response.context['is_edit']
        )
        for value, contr_value in fields.items():
            with self.subTest(value=value):
                self.assertIsInstance(
                    response.context.get('form').fields.get(value),
                    contr_value
                )

    def test_post_edit_page_sends_proper_context(self):
        '''Проверка контекста редактирования поста.'''

        fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        response = self.authorized_author.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        group = response.context.get('form')['group'].value()
        text = response.context.get('form')['text'].value()
        self.assertIn(
            'is_edit',
            response.context
        )
        self.assertTrue(
            response.context['is_edit']
        )
        self.assertEqual(
            text,
            self.post.text
        )
        self.assertEqual(
            group,
            self.post.group.id
        )
        for value, contr_value in fields.items():
            with self.subTest(value=value):
                self.assertIsInstance(
                    response.context.get('form').fields.get(value),
                    contr_value
                )

    def test_one_post_other_group(self):
        '''Проверка поста в другой группе.'''

        response = self.authorized_author.get(
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': self.group_empty.slug
                }
            )
        )
        self.assertNotIn(
            self.post,
            response.context['page_obj']
        )

    def test_one_post_on_group(self):
        '''Проверка поста в группе.'''

        pages = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.post.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
        )
        for page in pages:
            self.assertIn(
                self.post,
                self.authorized_author.get(page).context['page_obj']
            )
