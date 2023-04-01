import tempfile

from django import forms
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, get_user_model
from ..utils import LATEST_POSTS_COUNT

User = get_user_model()
COUNT_POSTS = 13
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        cls.INDEX = reverse('posts:index')
        cls.GROUP_LIST = reverse('posts:group_list',
                                 kwargs={'slug': 'group_1'})
        cls.PROFILE = reverse('posts:profile',
                              kwargs={'username': 'auth'})
        cls.POST_DETAIL = reverse('posts:post_detail',
                                  kwargs={
                                      'post_id': f'{cls.post.id}'})
        cls.POST_EDIT = reverse('posts:post_edit',
                                kwargs={
                                    'post_id': f'{cls.post.id}'})
        cls.POST_CREATE = reverse('posts:create_post')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    def test_namespace(self):
        templates = {
            self.INDEX:
                'posts/index.html',
            self.GROUP_LIST:
                'posts/group_list.html',
            self.PROFILE:
                'posts/profile.html',
            self.POST_DETAIL:
                'posts/post_detail.html',
            self.POST_EDIT:
                'posts/create_post.html',
            self.POST_CREATE: 'posts/create_post.html',

        }
        for namespace, template in templates.items():
            with self.subTest(namespace=namespace):
                response = self.authorized_client.get(namespace)
                self.assertTemplateUsed(response, template)

    def check_context_without_form(self):
        pages = [self.INDEX,
                 self.GROUP_LIST,
                 self.PROFILE,
                 self.POST_DETAIL]
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
        pages = [self.POST_CREATE,
                 self.POST_EDIT]
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
        reverses = [self.INDEX, self.GROUP_LIST,
                    self.PROFILE]
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
        posts = [Post(text=f'Test post {i}', group=cls.group, author=cls.user)
                 for i in range(COUNT_POSTS)]
        Post.objects.bulk_create(posts)
        cls.INDEX = reverse('posts:index')
        cls.GROUP_LIST = reverse('posts:group_list', args=(cls.group.slug,))
        cls.PROFILE = reverse('posts:profile', args=(cls.user.username,))

    def count_of_pages(self):
        pages = [self.INDEX,
                 self.GROUP_LIST,
                 self.PROFILE]
        for page in pages:
            response = self.authorized_client.get(page)
            self.assertEqual(len(response.conext['page_obj']),
                             LATEST_POSTS_COUNT)
