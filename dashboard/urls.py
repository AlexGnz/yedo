
from django.urls import path
from dashboard.views import *

urlpatterns = [
    path('', index, name="dashboard_home"),
    path('students/', allStudents, name="dashboard_all_students"),
    path('employeurs/', allEmployeurs, name="dashboard_all_employeurs"),
    path('jobs/', allJobsType, name="dashboard_all_types"),
    path('diplomes/', allDiplomeType, name="dashboard_all_diplomes"),
    path('languages/', allLanguages, name="dashboard_all_languages"),
]