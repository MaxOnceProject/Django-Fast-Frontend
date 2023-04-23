from django.urls import path
from . import views

urlpatterns = [
    path('', views.FrontendModelView.as_view(), name='frontend'),
    path('favicon.ico', views.favicon_view, name='favicon'),
]

urlpatterns += [
    path('<str:app_name>/', views.FrontendModelView.as_view(), name='frontend'),
    path('<str:app_name>/<str:model_name>/', views.FrontendModelView.as_view(), name='frontend'),
    path('<str:app_name>/<str:model_name>/<str:action>', views.FrontendModelView.as_view(), name='frontend'),
    path('<str:app_name>/<str:model_name>/<str:action>/<str:id>', views.FrontendModelView.as_view(), name='frontend'),
]

urlpatterns_account = [
    path('login/', views.FrontendLoginView.as_view(template_name='accounts/form.html'), name='account_login'),
    path('signup/', views.FrontendSignUpView.as_view(template_name='accounts/form.html'), name='account_signup'),
    path('logout/', views.FrontendLogoutView.as_view(), name='account_logout'),
    path('password_change/', views.FrontendPasswordChangeView.as_view(template_name='accounts/form.html'), name='account_password_change'),
    path('password_change/done/', views.FrontendPasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='account_password_change_done'),
    path('password_reset/', views.FrontendPasswordResetView.as_view(template_name='accounts/password_reset.html'), name='account_password_reset'),
    path('password_reset/done/', views.FrontendPasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='account_password_reset_done'),
    path('reset/<uidb64>/<token>/', views.FrontendPasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='account_password_reset_confirm'),
    path('reset/done/', views.FrontendPasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='account_password_reset_complete'),
]