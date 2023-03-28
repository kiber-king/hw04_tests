import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test',
            slug='group_1',
            description='Тестовое описание', )
        cls.post = Post.objects.create(
            text='testText',
            author=cls.user,
            group=cls.group
        )
        cls.form = PostForm()
        cls.forms_data = {
            'text': cls.post.text,
            'group': cls.post.group,
            'author': cls.post.author,
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = 0
        form_data = self.forms_data
        response = self.authorized_client.post(reverse('posts:create_post'),
                                               data=form_data, follow=True)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user.username}))
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                group=self.post.group,
                author=self.post.author,
            ).exists()
        )

    def test_edit_post(self):
        posts_count = Post.objects.count()
        form_data = self.forms_data
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)), data=form_data,
            follow=True)
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                group=self.post.group,
                author=self.post.author,
            ).exists()
        )
