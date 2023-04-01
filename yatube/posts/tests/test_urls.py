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
        addresses = [
            ['/', 'posts/index.html', self.guest_client, HTTPStatus.OK],
            [f'/group/{self.group.slug}/', 'posts/group_list.html',
             self.guest_client, HTTPStatus.OK],
            [f'/profile/{self.user.username}/', 'posts/profile.html',
             self.guest_client,
             HTTPStatus.OK],
            [f'/posts/{self.post.id}/', 'posts/post_detail.html',
             self.guest_client, HTTPStatus.OK],
            ['/unexisting_page/', 'core/404.html', self.guest_client,
             HTTPStatus.NOT_FOUND],
            ['/create/', 'posts/create_post.html', self.authorized_client,
             HTTPStatus.OK],
            [f'/posts/{self.post.id}/edit/', 'posts/create_post.html',
             self.authorized_client, HTTPStatus.OK]]
        for address, template, client, status_code in addresses:
            with self.subTest(address=address, client=client):
                response = client.get(address)
                self.assertEqual(response.status_code, status_code)
                self.assertTemplateUsed(response, template)
