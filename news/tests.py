from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from captcha.models import CaptchaStore


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






