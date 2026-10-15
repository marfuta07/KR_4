from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from users import views

app_name = 'users'

urlpatterns = [
    # Регистрация / вход / выход
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/toggle/', views.UserToggleActiveView.as_view(), name='user_toggle_active'),

    # Восстановление пароля
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset_form.html',
             email_template_name='users/password_reset_email.html',
             success_url=reverse_lazy('users:password_reset_done'),
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html',
         ),
         name='password_reset_done'),

    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url=reverse_lazy('users:password_reset_complete'),
         ),
         name='password_reset_confirm'),

    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html',
         ),
         name='password_reset_complete'),
]