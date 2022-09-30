from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from captcha.models import CaptchaStore
from news.models import News


class UserTestCase(TestCase):
    fixtures = [
        'test_user.json'
    ]

    def setUp(self):
        # simulate user logging for auth.system
        user_logged = get_user_model().objects.first()
        self.client.force_login(user_logged)

    def test_log_in_out(self):
        # check response status, template
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='news/login.html')
        # check login with true login&pass
        register_user = {'username': 'test',
                    'email: testmail@gmail.com'
                    'password1': '123456test1',
                    'password2': '123456test1'}
        self.client.post(reverse('register'), register_user)
        response = self.client.post(reverse('login'), {'username': 'test', 'password': '123456test1'})
        self.assertEqual(response.status_code, 200)
        # check login with false login&pass
        response = self.client.post(reverse('login'), {'username': 'test2', 'password': '123458test'})
        self.assertEqual(response.status_code, 200)
        # check logout
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_register_user(self):
        # check response status, template
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='news/register.html')
        # check add user
        register_user = {'username': 'test',
                    'email': 'testmail@gmail.com',
                    'password1': '123456test1',
                    'password2': '123456test1'}

        response = self.client.post(reverse('register'), register_user)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        # check user added in database
        user = get_user_model().objects.get(username=register_user['username'])
        self.assertEqual(user.username, 'test')
        self.assertEqual(get_user_model().objects.count(), 2)
        # check add user with same username
        response = self.client.post(reverse('register'), register_user)
        self.assertFormError(response, 'form', 'username', 'Пользователь с таким именем уже существует.')
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), 'Ошибка регистрации')


class ContactTestCase(TestCase):
    fixtures = [
        'test_user.json'
    ]

    def setUp(self):
        # simulate user logging for auth.system
        user_logged = get_user_model().objects.first()
        self.client.force_login(user_logged)

    def test_contact(self):
        # check response status, template
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='news/contact.html')

        # check valid contact form is correct
        # check captcha is loaded
        captcha_count = CaptchaStore.objects.count()
        self.failUnlessEqual(captcha_count, 1)
        # get captcha data from CaptchaStore
        captcha = CaptchaStore.objects.all()[0]
        # fill contact form, captcha_0 - captcha task, captcha_1 - captcha solution
        contact = {
            'subject': 'test_subject',
            'content': 'test_content',
            'mail': 'testmail@gmail.com',
            'captcha_0': captcha.hashkey,
            'captcha_1': captcha.response,
        }
        response = self.client.post(reverse('contact'), contact)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

        # check invalid contact form
        contact_invalid = {
            'subject': '',
            'content': 'test_content',
            'mail': 'testmail@gmail.com',
            'captcha_0': captcha.hashkey,
            'captcha_1': captcha.response,
        }
        response = self.client.post(reverse('contact'), contact_invalid)
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), 'Ошибка проверки')


class NewsTestCase(TestCase):
    fixtures = [
        'test_user.json',
        'test_category.json'
    ]

    def setUp(self):
        # simulate user logging for auth.system
        user_logged = get_user_model().objects.first()
        self.client.force_login(user_logged)

    def test_news_add(self):
        # check response status, template
        response = self.client.get(reverse('add_news'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='news/add_news.html')

        # check add news
        news1 = {
            'title': 'test_news1',
            'content': 'test_content1',
            'category': 1
        }
        response = self.client.post(reverse('add_news'), news1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/news/1/')
        # check news added in database
        news = News.objects.get(title=news1['title'])
        self.assertEqual(news.title, 'test_news1')
        self.assertEqual(get_user_model().objects.count(), 1)
        # check validation
        news2 = {
            'title': '2test_news',
            'content': 'test_content2',
            'category': 1
        }
        response = self.client.post(reverse('add_news'), news2)
        self.assertFormError(response, 'form', 'title', 'Название не должно начинаться с цифры')

    def test_news_category(self):
        # add news by categories
        news1 = {
            'title': 'test_news1',
            'content': 'test_content1',
            'category': 1
        }
        news2 = {
            'title': 'test_news2',
            'content': 'test_content2',
            'category': 2
        }
        news3 = {
            'title': 'test_news3',
            'content': 'test_content3',
            'category': 2
        }
        self.client.post(reverse('add_news'), news1)
        self.client.post(reverse('add_news'), news2)
        self.client.post(reverse('add_news'), news3)
        # check status code and template of categories
        response = self.client.get('/category/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='news/list_of_news.html')
        # check news added correctly by categories in db
        self.assertEqual(len(News.objects.filter(category_id=1)), 1)
        self.assertEqual(len(News.objects.filter(category_id=2)), 2)
