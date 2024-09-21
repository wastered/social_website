from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.transaction import commit
from django.http import HttpResponse
from django.shortcuts import render

from .forms import LoginForm, UserRegistrationForm


@login_required()
def dashboard(request):
    return render(request,
                  'account/dashboard.html',
                  context={
                      'section': 'dashboard'
                  }
                  )


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # Проверяем учетные данные пользователя
            user = authenticate(request=request, username=cd['username'], password=cd['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)  # Задаем пользователя в текущем сеансе
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled user')

            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()

    return render(request, 'account/login.html',
                  context={
                      'form': form
                  })


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Создать новый объект пользователя,
            # но пока не сохранять его
            new_user = user_form.save(commit=False)
            # Установить выбранный пароль
            new_user.set_password(user_form.cleaned_data['password'])
            # Сохранить объект User
            new_user.save()
            return render(request,
                          'account/register_done.html',
                          context={
                              'new_user': new_user,
                          })
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  context={
                      'user_form': user_form,
                  })