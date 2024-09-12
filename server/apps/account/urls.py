from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = 'account'

urlpatterns = [
    # предыдущий url входа
    # path('login/', views.user_login, name='login'),

    # url-адреса входа и выхода
    path('login/',
         auth_views.LoginView.as_view(template_name='account/registration/login.html'), name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(template_name='account/registration/logged_out.html'),
         name='logout'),

    # url-адреса смены пароля
    path('password-change/',
         auth_views.PasswordChangeView.as_view(template_name='account/registration/password_change_form.html',
                                               success_url=reverse_lazy('account:password_change_done')),
         name='password_change'),
    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='account/registration/password_change_done.html'),
         name='password_change_done'),

    path('', views.dashboard, name='dashboard')
]
