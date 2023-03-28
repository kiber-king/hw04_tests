from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test',
            slug='group_1',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='test2',
            slug='group_2',
            description='TEst2'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test',
            group=cls.group,
        )
        post_array = []
        for i in range(10):
            cls.post1 = Post.objects.create(
                author=cls.user,
                text='test',
                group=cls.group,
            )
            post_array.append(cls.post1)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    def test_namespace(self):
        templates = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'group_1'}):
                'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'auth'}):
                'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={
                        'post_id': f'{self.post.id}'}):
                'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': f'{self.post.id}'}):
                'posts/create_post.html',
            reverse('posts:create_post'): 'posts/create_post.html',

        }
        for namespace, template in templates.items():
            with self.subTest(namespace=namespace):
                response = self.authorized_client.get(namespace)
                self.assertTemplateUsed(response, template)

    def test_index(self):
        response = self.authorized_client.get(reverse('posts:index'))
        new_page_obj = response.context['page_obj'][0]
        self.assertEqual(new_page_obj.text, self.post.text)
        self.assertEqual(new_page_obj.author, self.post.author)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        group = response.context['group']
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.description, self.group.description)
        first_obj = response.context['page_obj'][0]
        self.assertEqual(first_obj.text, self.post.text)
        self.assertEqual(first_obj.author, self.user)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile(self):
        response = self.authorized_client.get(reverse('posts:profile', kwargs={
            'username': self.user.username}))
        profile = response.context['author']
        self.assertEqual(profile.username, self.user.username)
        obj = response.context['page_obj'][0]
        self.assertEqual(obj.text, self.post.text)
        self.assertEqual(obj.author, self.user)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_post_create(self):
        response = self.authorized_client.get(
            reverse('posts:create_post'))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_deatail(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post = response.context['post']
        self.assertEqual(post.id, self.post.id)

    def test_post_edit(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        post = response.context['post']
        self.assertEqual(post.id, self.post.id)
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_after_creation(self):
        reverses = [reverse('posts:index'), reverse('posts:group_list',
                                                    kwargs={
                                                        'slug':
                                                            self.group.slug
                                                    }),
                    reverse('posts:profile',
                            kwargs={'username': self.post.author})]
        for reverse_name in reverses:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post = response.context['page_obj'][0]
                self.assertEqual(post.author, self.post.author)
        response_2 = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group2.slug}))
        list_obj = response_2.context['page_obj']
        self.assertEqual(len(list_obj), 0)
