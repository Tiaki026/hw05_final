from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post
User = get_user_model()
TST_SMBL = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """
        Проверяем, что у моделей корректно работает __str__.
        """
        post = PostModelTest.post
        expected_text = post.text[:TST_SMBL]
        self.assertEqual(str(post), expected_text)

        group = PostModelTest.group
        expected_title = group.title
        self.assertEqual(str(group), expected_title)
