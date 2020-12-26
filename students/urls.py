
from django.urls import path
from students.views import *

urlpatterns = [
    path('details/<slug:id>/', details, name="student_details"),
    path('searchjob/<slug:id>/', search_by_job_type, name="search_by_job_type"),
    path('search/', search, name="search_students"),
    path('profile/', profile, name="student_profile"),
    path('profile/infos/', profile_infos, name="student_profile_infos"),
    path('profile/settings/', settings, name="student_settings"),
    path('unlock/<slug:id>/', unlock, name="unlock"),
    path('payment/', payment, name="payment"),
    path('checkout/', recap, name="recap"),
    path('demande/<slug:id>/', demande, name="demande"),
    path('refer/', refer, name="refer"),
    path('video/', video, name="student_video"),
    path('photo/', photo, name="student_photo"),
    path('preview/', mypreview, name="student_preview"),
    path('', index),
]