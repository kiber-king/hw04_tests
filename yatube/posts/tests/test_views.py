from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, get_user_model
from ..utils import LATEST_POSTS_COUNT

User = get_user_model()
COUNT_POSTS = 13


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

    def check_context_without_form(self):
        pages = [reverse('posts:index'),
                 reverse('posts:group_list', args=(self.group.slug,)),
                 reverse('posts:profile', args=(self.user.username,)),
                 reverse('posts:post_detail', args=(self.post.id,))]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                new_page_obj = response.context['page_obj'][0]
                self.assertEqual(new_page_obj.text, self.post.text)
                self.assertEqual(new_page_obj.author, self.post.author)
                if page == pages[1]:
                    group = response.context['group']
                    self.assertEqual(group.title, self.group.title)
                elif page == pages[2]:
                    profile = response.context['author']
                    self.assertEqual(profile.username, self.user.username)
                elif page == pages[3]:
                    post = response.context['post']
                    self.assertEqual(post.id, self.post.id)

    def test_context_forms(self):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        pages = [reverse('posts:create_post'),
                 reverse('posts:post_edit', args=(self.post.id,))]
        for page in pages:
            response = self.authorized_client.get(page)
            if page == pages[1]:
                post = response.context['post']
                self.assertEqual(post.id, self.post.id)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_added_correctly(self):
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
                self.assertEqual(post, self.post)
                self.assertEqual(post, self.post)
                self.assertEqual(post, self.post)
        response_2 = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group2.slug}))
        list_obj = response_2.context['page_obj']
        self.assertEqual(len(list_obj), 0)


class PaginatorView(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user('auth')
        cls.touple_of_posts = []
        cls.group = Group.objects.create(
            title='Test',
            slug='group',
            description='Test group'
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        for i in range(COUNT_POSTS):
            cls.touple_of_posts.append(Post(
                text=f'Test post number {i}',
                group=cls.group,
                author=cls.user
            ))
        Post.objects.bulk_create(cls.touple_of_posts)

    def count_of_pages(self):
        pages = [reverse('posts:index'),
                 reverse('posts:group_list', args=(self.group.slug,)),
                 reverse('posts:profile', args=(self.user.username,))]
        for page in pages:
            response = self.authorized_client.get(page)
            self.assertEqual(len(response.conext['page_obj']),
                             LATEST_POSTS_COUNT)
