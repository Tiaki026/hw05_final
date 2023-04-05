from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from posts.models import Post, Group, User
from django.core.cache import cache


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

    def test_index_page_sends_proper_context(self):
        '''Проверка контекста test_index.'''
        response = self.authorized_author.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_group_posts_page_sends_proper_context(self):
        '''Проверка контекста test_group_posts'''
        response = self.authorized_author.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_profile_page_sends_proper_context(self):
        '''Проверка контекста test_profile'''
        response = self.authorized_author.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_post_detail_page_sends_proper_context(self):
        '''Проверка контекста test_post_detail.'''
        response = self.authorized_author.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        post = response.context['posts']
        self.check_post(post)

    def test_post_create_page_sends_proper_context(self):
        '''Проверка контекста test_post_create.'''
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
        '''Проверка контекста test_post_edit.'''
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
