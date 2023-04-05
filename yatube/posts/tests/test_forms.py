import shutil
import tempfile
from django.conf import settings
from django.urls import reverse
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.models import Post, Group, User, Comment
from posts.forms import PostForm

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
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
        cls.form = PostForm()

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

    def test_create_new_post(self):
        '''Тест создания новой записи в БД'''

        form_data = {
            'text': 'Текст нового поста',
            'group': self.group.id,
        }
        self.authorized_author.post(
            reverse(
                'posts:post_create',
            ),
            data=form_data,
            follow=True
        )
        create_post = Post.objects.exclude().first()
        self.assertEqual(
            create_post.text,
            form_data['text']
        )
        self.assertEqual(
            create_post.group.id,
            form_data['group']
        )

    def test_post_edit(self):
        '''Тест редактирования записи в БД'''
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
        }
        self.authorized_author.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        edit_post = Post.objects.get(id=self.post.id)
        self.assertEqual(
            edit_post.text,
            form_data['text']
        )
        self.assertEqual(
            edit_post.group.id,
            form_data['group']
        )

    def test_create_post_with_img(self):
        '''Тест создания записи с картинкой в БД'''

        small_gif_two = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_two = SimpleUploadedFile(
            name='small.gif',
            content=small_gif_two,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст под картинкой',
            'image': uploaded_two,
        }
        self.authorized_author.post(
            reverse(
                'posts:post_create',
            ),
            data=form_data,
            follow=True
        )
        create_post = Post.objects.exclude(id=self.post.id).first()
        self.assertEqual(
            create_post.image,
            f'posts/{uploaded_two}'
        )

    def test_context_post_with_img_index(self):
        '''Тест поста с картинкой передается в контексте на главную страницу'''

        form_data = {
            'text': 'Тестовый текст под картинкой',
            'image': self.uploaded,
        }
        response = self.authorized_author.get(
            reverse('posts:index'),
            data=form_data,
            follow=True
        )
        post = response.context['page_obj'][0].image
        self.assertEqual(self.post.image, post)

    def test_context_post_with_img_profile(self):
        '''Тест поста с картинкой передается в контексте на страницу профиля'''

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
        post = response.context['page_obj'][0].image
        self.assertEqual(self.post.image, post)

    def test_context_post_with_img_group_list(self):
        '''Тест поста с картинкой передается в контексте на страницу группы'''

        form_data = {
            'text': 'Тестовый текст под картинкой',
            'image': self.uploaded,
            'group': self.group.id,
        }
        response = self.authorized_author.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            data=form_data,
            follow=True
        )
        post = response.context['page_obj'][0].image
        self.assertEqual(self.post.image, post)

    def test_context_post_with_img_post_detail(self):
        '''Тест поста с картинкой передается в контексте на страницу поста'''

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
        post = response.context['posts'].image
        self.assertEqual(self.post.image, post)

    def test_create_commets_can_user(self):
        '''Проверка создания комментария только пользователям'''

        form_data = {
            'text': 'Тестовый коммент',
            'autor': self.user,
            'post': self.post
        }
        self.authorized_author.post(
            reverse('posts:add_comment', args={self.post.id}),
            fata=form_data,
        )
        self.assertFalse(
            Comment.objects.filter(
                post=self.post,
                text=form_data['text'],
            ).exists()
        )
