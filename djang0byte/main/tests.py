"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import json
from django.contrib.auth.models import User
from django.test import TestCase
from main.forms import CreateBlogForm, CreatePostForm, CreateAnswerForm, EditPostForm
from main.models import Profile, Post, Answer, BlogType, Blog, UserInBlog
from django.conf import settings


class PostTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test')
        Profile.objects.create(user=self.user)

    def test_create_blog(self):
        BlogType.objects.create(name=settings.DEFAULT_BLOG_TYPE)
        form = CreateBlogForm(self.user, {
            'name': 'okok',
            'description': 'test blog'
        })
        self.assertTrue(form.is_valid(), msg='blog form not work')
        blog = form.save()
        self.assertIsNotNone(blog.id, msg='blog saving not work')
        self.assertEqual(blog.name, 'okok', msg='blog data broken')

    def test_create_simple_post(self):
        form = CreatePostForm(self.user, {
            'type': Post.TYPE_POST,
            'title': 'OKOK!',
            'text': 'good',
            'raw_tags': 'op, ko, lot',
        })
        self.assertTrue(form.is_valid(), msg='simple post without blog validation failed')
        form.is_valid()
        post = form.save()
        self.assertIsNotNone(post.id, msg='simple post saving not work')
        self.assertEqual('OKOK!', post.title, msg='post data broken')
        self.assertEqual(Post.TYPE_POST, post.type, msg='post data broken')

    def test_create_link_post(self):
        form = CreatePostForm(self.user, {
            'type': Post.TYPE_LINK,
            'title': 'okok',
            'text': 'ok',
            'addition': 'http://welinux.ru',
        })
        self.assertTrue(form.is_valid(), msg='link post validation failed')
        form.is_valid()
        post = form.save()
        self.assertIsNotNone(post.id, msg='link post saving not work')
        self.assertEqual(post.addition, 'http://welinux.ru', msg='post data broken')

    def test_create_trans_post(self):
        form = CreatePostForm(self.user, {
            'type': Post.TYPE_TRANSLATE,
            'title': 'okok',
            'text': 'ok',
            'addition': 'http://welinux.ru',
        })
        self.assertTrue(form.is_valid(), msg='trans post validation failed')
        post = form.save()
        self.assertIsNotNone(post.id, msg='trans post saving not work')
        self.assertEqual(post.addition, 'http://welinux.ru', msg='trans post data broken')

    def test_create_answer_post(self):
        form = CreateAnswerForm(self.user, {
            'type': Post.TYPE_ANSWER,
            'title': 'okok',
            'answers': json.dumps(['ok', 'no', 'five']),
        })
        self.assertTrue(form.is_valid(), msg='answer validation failed')
        post = form.save()
        self.assertIsNotNone(post.id, msg='answer post saving not work')
        self.assertEqual(
            Answer.objects.filter(post=post).count(), 3,
            msg='answer creation failed'
        )

    def test_create_post_with_blog(self):
        BlogType.objects.create(name=settings.DEFAULT_BLOG_TYPE)
        blog = Blog.objects.create(name='okok', owner=self.user)
        UserInBlog.objects.create(blog=blog, user=self.user)
        form = CreatePostForm(self.user, {
            'type': Post.TYPE_POST,
            'title': 'okok',
            'text': 'okokok',
            'blog': blog.id,
        })
        self.assertTrue(form.is_valid(), msg='post with blog validation failed')
        post = form.save()
        self.assertIsNotNone(post.id, msg='post with blog saving not work')
        self.assertEqual(post.blog, blog, msg='blog not assigned')

    def test_edit_post(self):
        post = Post.objects.create(
            type=Post.TYPE_POST,
            title='okok',
            text='okokok',
            author=self.user,
        )
        form = EditPostForm(self.user, {
            'title': 'eeee',
            'text': '232323',
        }, instance=post)
        self.assertTrue(form.is_valid(), msg='edit post validation failed')
        changed_post = form.save()
        self.assertEqual(post.id, changed_post.id, msg='new post created')
        self.assertEqual(changed_post.title, 'eeee', msg='edit failed')
