from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, get_user_model

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group_1 = Group.objects.create(
            title='test',
            slug='group_1',
            description='Тестовое описание группы 1', )
        cls.group_2 = Group.objects.create(
            title='test_2',
            slug='group_2',
            description='Новое тестовое описание группы 2'
        )
        cls.CREATE_POST = reverse('posts:create_post')
        cls.post = Post.objects.create(
            text='Old text',
            author=cls.user,
            group=cls.group_1
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст нового поста',
            'group': self.group_1.id
        }
        response = self.authorized_client.post(self.CREATE_POST,
                                               data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('id')
        form_to_post = {
            form_data['text']: post.text,
            form_data['group']: post.group.id
        }
        for form_value, post_value in form_to_post.items():
            with self.subTest(form_value=form_value):
                self.assertEqual(form_value, post_value)
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст старого поста',
            'group': self.group_2.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)), data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)
        post = Post.objects.latest('id')
        form_to_post = {
            form_data['text']: post.text,
            form_data['group']: post.group.id
        }
        for form_value, post_value in form_to_post.items():
            with self.subTest(form_value=form_value):
                self.assertEqual(form_value, post_value)
