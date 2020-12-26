from django.urls import path
from handleauth.views import *

urlpatterns = [
    path('', home),
    path('login/', loginviews, name="auth_login"),
    path('signup/', signup, name="auth_signup"),
    path('logout/', logoutviews, name="auth_logout"),
    path('password/reset/', password, name="auth_password"),
    path('hire/', hire, name="auth_signup_employeur")
]