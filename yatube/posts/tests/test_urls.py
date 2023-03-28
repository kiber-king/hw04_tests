from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test',
            slug='group_1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_all_temp(self):
        adresses = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/unexisting_page/': False,
        }
        for adress, template in adresses.items():
            with self.subTest(aderss=adress):
                response = self.guest_client.get(adress)
                if adress == '/unexisting_page/':
                    self.assertEqual(response.status_code, 404)
                else:
                    self.assertEqual(response.status_code, 200)
                    self.assertTemplateUsed(response, template)

    def test_auth(self):
        adresses = {
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit': 'posts/create_post.html',
        }
        for adress, template in adresses.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template)
