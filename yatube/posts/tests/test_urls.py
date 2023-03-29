from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Post, Group, get_user_model

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
        cls

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_all_temp_guest_client(self):
        addresses = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/unexisting_page/': False,
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html'
        }
        for address, template in addresses.items():
            with self.subTest(adderss=address):
                if address == '/create/' or (
                        address == f'/posts/{self.post.id}/edit/'):
                    response = self.authorized_client.get(address)
                    self.assertTemplateUsed(response, template)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    response = self.guest_client.get(address)
                    if address == '/unexisting_page/':
                        self.assertEqual(response.status_code,
                                         HTTPStatus.NOT_FOUND)
                    else:
                        self.assertEqual(response.status_code, HTTPStatus.OK)
                        self.assertTemplateUsed(response, template)
