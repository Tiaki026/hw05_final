from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post, User


class CommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestAuthor')
        cls.group = Group.objects.create(
            title='Comments тестовая группа',
            slug='slug',
            description='Группа',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group
        )
        cls.comment_view_url = reverse('posts:add_comment', args=['1'])

    def setUp(self):
        self.guest = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user)

    def test_authorized_client_comment(self):
        '''Проверка комментирования для авторизированного пользователя'''

        test_comment = (
            'Проверяем комментарии к посту для '
            'авторизованного пользователя'
        )
        self.authorized_author.post(
            self.comment_view_url,
            data={'text': test_comment}
        )
        comment = Comment.objects.filter(
            post=self.post
        ).last()
        check_fields = {}
        check_fields['text'] = (
            comment.text,
            test_comment
        )
        check_fields['author'] = (
            comment.author,
            self.user
        )
        check_fields['post'] = (
            comment.post,
            self.post
        )
        for name, compared_values in check_fields.items():
            with self.subTest(name=name):
                self.assertEqual(
                    compared_values[0],
                    compared_values[1]
                )

    def test_guest_client_comment_redirect_login(self):
        '''Проверка комментария на странице поста'''

        num_comments = Comment.objects.count()
        self.guest.post(self.comment_view_url)
        self.assertEqual(num_comments, Comment.objects.count())
