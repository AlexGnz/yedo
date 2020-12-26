from django.shortcuts import redirect, render
from yedo import views as yedoviews

def customerror400(request, exception):
    return redirect(yedoviews.main_home)

def customerror500(request):
    return redirect(yedoviews.main_home)


