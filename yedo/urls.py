"""yedo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from handleauth import urls as authurls
from students import urls as studentsurls
from entreprises import urls as entreprisesurls
from dashboard import urls as dashboardurls
from yedo.views import *
from django.conf.urls import handler404, handler500, handler400, handler403
from yedo.errors import customerror400, customerror500


urlpatterns = [
    path('yedodashboardadmin/', landing_page),
    path('', landing_page),
    path('auth/', landing_page),
    path('student/', landing_page, name="index_redirect"),
    path('join/', landing_page, name="index_redirect_fb"),
    path('hire/', landing_page, name="employeur_signup_redirect"),
    path('complete/', landing_page, name="index_redirect_mail"),
    path('students/', landing_page),
    path('e/', landing_page),
    path('yedodashboard/', landing_page),
    path('', landing_page, name="main_home"),
    path('new/', landing_page, name="new"),
    path('terms/', landing_page, name='terms_and_conditions'),
    path('privacy/', landing_page, name='privacy'),
    path('sale/', landing_page, name='conditions_vente'),
    path('pricing/', landing_page, name="pricing"),
    path('payment/success/', landing_page, name="payment_success"),
    path('payment/canceled/', landing_page, name="payment_cancel"),
    path('successful-payment/', landing_page, name="webhook"),
    path('demo/', landing_page, name="demo"),
    path('profile/', landing_page, name="employeur_profile"),
    path('profile/infos/', landing_page, name="employeur_profile_infos"),
    path('newsletter/', landing_page, name="newsletter"),
    path('unsubscribe/', landing_page, name="unsubscribe"),
    path('zipencode/', landing_page, name="zip_encode"),
    path('p/<slug:code>/', landing_page, name="parrainage_redirect"),
    path('my-dashboard/', landing_page, name="dashboard_marketer"),
    # path('auth/', include(authurls)),
    # path('student/', index_redirect, name="index_redirect"),
    # path('join/', index_redirect_fb, name="index_redirect_fb"),
    # path('hire/', employeur_signup_redirect, name="employeur_signup_redirect"),
    # path('complete/', index_redirect_mail, name="index_redirect_mail"),
    # path('students/', include(studentsurls)),
    # path('e/', include(entreprisesurls)),
    # path('yedodashboard/', include(dashboardurls)),
    # path('', main_home, name="main_home"),
    # path('new/', new, name="new"),
    # path('terms/', terms, name='terms_and_conditions'),
    # path('privacy/', privacy, name='privacy'),
    # path('sale/', sale, name='conditions_vente'),
    # path('pricing/', pricing, name="pricing"),
    # path('payment/success/', payment_success, name="payment_success"),
    # path('payment/canceled/', payment_cancel, name="payment_cancel"),
    # path('successful-payment/', my_webhook_view, name="webhook"),
    # path('demo/', demo, name="demo"),
    # path('profile/', profile, name="employeur_profile"),
    # path('profile/infos/', profile_infos, name="employeur_profile_infos"),
    # path('newsletter/', newsletter, name="newsletter"),
    # path('unsubscribe/', unsubscribe, name="unsubscribe"),
    # path('zipencode/', zipencode, name="zip_encode"),
    # path('p/<slug:code>/', parrainage, name="parrainage_redirect"),
    # path('my-dashboard/', dashboard_marketer, name="dashboard_marketer"),
]

handler404 = 'yedo.errors.customerror400'
handler403 = 'yedo.errors.customerror400'
handler400 = 'yedo.errors.customerror400'
handler500 = 'yedo.errors.customerror500'