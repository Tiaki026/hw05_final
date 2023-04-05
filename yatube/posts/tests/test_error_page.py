from django.test import TestCase, Client
from posts.models import User


class ErrorTestClass(TestCase):
    def test_404_page(self):
        '''Проверка использования кастомной страницы ошибки 404.'''

        self.user = User.objects.create_user(username='author')
        self.guest = Client()
        self.guest.force_login(self.user)
        response = self.guest.get('/nonexist-page/')
        self.assertEqual(
            response.status_code,
            404
        )
        self.assertTemplateUsed(
            response,
            template_name='includes/core/404.html'
        )
