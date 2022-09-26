from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from .models import News, Category
from .forms import NewsForm, UserRegistrationForm, UserLoginForm, ContactForm
from .utils import MyMixin
from django.contrib.messages.views import SuccessMessageMixin


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect('home')
        else:
            messages.error(request, 'Ошибка регистрации')
    else:
        form = UserRegistrationForm()
    return render(request, 'news/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = UserLoginForm
    return render(request, 'news/login.html', {"form": form})


def user_logout(request):
    logout(request)
    return redirect('login')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['content'] + '\nfrom: ' + form.cleaned_data['mail']
            mail = send_mail(form.cleaned_data['subject'], message, 'testingsmtpdjango1@gmail.com', ['testingsmtpdjango1@gmail.com'])
            if mail:
                messages.success(request, 'Письмо отправлено!')
                return redirect('home')
            else:
                messages.error(request, 'Ошибка отправки')
        else:
            messages.error(request, 'Ошибка проверки')
    else:
        form = ContactForm()
    return render(request, 'news/contact.html', {'form': form})


class HomeNews(MyMixin, ListView):
    model = News
    template_name = 'news/list_of_news.html'
    context_object_name = 'news'
    paginate_by = 4
    mixin_prop = 'News'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mixin makes title in uppercase
        context['title'] = self.get_upper('Главная страница')
        context['mixin_prop'] = self.get_prop()
        return context

    def get_queryset(self):
        return News.objects.filter(is_published=True).select_related('category').order_by('-created_at')


class NewsByCategory(MyMixin, ListView):
    model = News
    template_name = 'news/list_of_news.html'
    context_object_name = 'news'
    paginate_by = 4
    mixin_prop = 'News-Category'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mixin makes title - name of category in uppercase
        context['title'] = self.get_upper(Category.objects.get(pk=self.kwargs['category_id']))
        context['mixin_prop'] = self.get_prop()
        return context

    def get_queryset(self):
        # Filter Newsobjects by category_id and is_published
        # select_related returns a qs that follow foreign-key relations and selecting additional data(category)
        return News.objects.filter(category_id=self.kwargs['category_id'],
                                   is_published=True).select_related('category')


class ViewNews(DetailView):
    model = News
    context_object_name = 'news_item'
    template_name = 'news/single.html'


class CreateNews(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    form_class = NewsForm
    template_name = 'news/add_news.html'
    login_url = '/admin/'
    success_message = 'Спасибо, ваша новость отправлена на модерацию!'
