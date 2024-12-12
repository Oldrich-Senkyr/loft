from django.urls import path
from .views import index, my_logout, signup, switch_language, swl

from django.contrib.auth import views as auth_views #login  importuje views z danga
from .forms import LoginForm                        #login

app_name = 'core'

urlpatterns = [
    path('', index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html',authentication_form=LoginForm), name='login'),
    path('logout/', my_logout, name='logout'),
    path('signup/', signup, name='signup'),
    path('switch_language/<str:language_code>/', switch_language, name='switch_language'),
    path('swl', swl, name='swl'),  # Domovská stránka
    ]

