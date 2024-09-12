from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render

from .forms import LoginForm


# Create your views here.
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
