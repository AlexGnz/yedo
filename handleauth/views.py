from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, get_user, login, logout,update_session_auth_hash
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
from yedo.utils import *
from yedo.settings import mailjettemplates


import datetime
from django.utils import timezone
from yedo.models import *
from yedo.views import *
from dashboard.views import *

def home(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        return redirect(main_home)
    else:
        return redirect(loginviews)

def isEmailAvailable(email):
    return len(User.objects.all().filter(email=email.lower())) == 0

def hire(request):
    referral = None
    parrain = None
    if 'fbclid' in request.GET:
        stat = Stats.objects.all()[0]
        stat.clics_from_fb += 1
        stat.save()
    if 'e' in request.POST or 'e' in request.GET:
        if 'email_sent' in request.GET:
            if request.user and request.user.is_authenticated:
                logout(request)
            if 'username' in request.session:
                del request.session['username']
            if 'email' in request.GET and isEmailAvailable(request.GET['email']):
                p = getRandomPassword()
                username = getRandomUsername(request.GET['email'])
                user = User.objects.create_user(email=request.GET['email'].lower(), password=p,
                                                username=username)
                user.save()
                sendEmail(mailjettemplates['new_account_employeur'], "Bienvenue sur Yedo.", user.email)
                employeur = Employeur(user=user)
                employeur.save()
                login(request, user)
                update_session_auth_hash(request, user)
                request.session['username'] = user.username
                request.session['email'] = user.email
                return redirect(main_home)
            else:
                errors = []
                if 'email' in request.GET and not isEmailAvailable(request.GET['email']):
                    request.session['email_already_used'] = True
                    request.session['email'] = request.GET['email']
                    return redirect(loginviews)
                if not 'email' in request.GET:
                    errors.append("Email non renseignée")
                if len(errors) == 0:
                    errors.append("Erreur inconnue. N'hésitez pas à nous contacter")
                var = {
                    'errors': errors
                }
                return render(request, 'auth/hire.html', var)
        else:
            if 'email' in request.POST and 'password' in request.POST and 'password2' in request.POST and isEmailAvailable(
                    request.POST['email']) and request.POST['password'] == request.POST['password2']:
                username = getRandomUsername(request.POST['email'])
                user = User.objects.create_user(email=request.POST['email'].lower(), password=request.POST['password'],
                                                username=username)
                user.save()
                sendEmail(mailjettemplates['new_account_employeur'], "Bienvenue sur Yedo.", user.email)
                employeur = Employeur(user=user, default_password=False)
                employeur.save()
                login(request, user)
                update_session_auth_hash(request, user)
                request.session['username'] = user.username
                request.session['email'] = user.email
                return redirect(main_home)
            else:
                errors = []
                if 'email' in request.POST and isEmailAvailable(request.POST['email']):
                    request.session['email'] = request.POST['email']
                if 'email' in request.POST and not isEmailAvailable(request.POST['email']):
                    errors.append("Adresse email déjà utilisée")
                    if 'email' in request.session:
                        del request.session['email']
                if 'password' in request.POST and 'password2' in request.POST and request.POST['password'] != request.POST['password2']:
                    errors.append("Confirmation de mot de passe incorrecte")
                if not 'password' in request.POST:
                    errors.append("Mot de passe non renseigné")
                if not 'password2' in request.POST:
                    errors.append("Confirmation de mot de passe non renseignée")
                if not 'email' in request.POST:
                    errors.append("Email non renseignée")
                if len(errors) == 0:
                    errors.append("Erreur inconnue. N'hésitez pas à nous contacter")
                email_user = ''
                if 'email' in request.session:
                    email_user = request.session['email']
                var = {
                    'errors': errors,
                    'email_user': email_user
                }
                return render(request, 'auth/hire.html', var)

    else:
        if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
            return redirect(main_home)
        email_user = ''
        if 'email' in request.session:
            email_user = request.session['email']
        return render(request, 'auth/hire.html', {'email_user': email_user})

def signup(request):
    referral = None
    parrain = None
    if 'parrain' in request.session:
        parrain = StreetMarketer.objects.get(id=request.session['parrain'])
    elif 'best_friend' in request.GET:
        email = request.GET['best_friend']
        if len(Student.objects.filter(user__email=email)) == 1:
            referral = Student.objects.get(user__email=email)
    if 'fbclid' in request.GET:
        stat = Stats.objects.all()[0]
        stat.clics_from_fb += 1
        stat.save()

    if 'student' in request.GET or 'student' in request.POST:
        if 'facebook' in request.GET:
            if request.user.is_authenticated:
                logout(request)
            if 'username' in request.session:
                del request.session['username']
            if 'email' in request.GET and isEmailAvailable(request.GET['email']) and 'exp' in request.GET and 'prenom' in request.GET and 'nom' in request.GET and 'gender' in request.GET and 'picture' in request.GET and 'language' in request.GET and 'messengerid' in request.GET:
                p = getRandomPassword()
                username = getRandomUsername(request.GET['email'])
                user = User.objects.create_user(email=request.GET['email'].lower(), password=p,
                                                username=username)
                user.save()
                sendEmail(mailjettemplates['new_account_student'], "Bienvenue sur Yedo.", user.email)
                student = Student(user=user,
                                  exp=request.GET['exp'],
                                  prenom=request.GET['prenom'],
                                  nom=request.GET['nom'],
                                  phone=request.GET['phone'],
                                  gender=request.GET['gender'],
                                  fb_pic=request.GET['picture'],
                                  language=request.GET['language'],
                                  messenger_id=request.GET['messengerid'],
                                  name="" + request.GET['prenom'] + " " + request.GET['nom'] + "")
                student.save()
                login(request, user)
                request.session['username'] = user.username
                request.session['email'] = user.email
                return redirect(main_home)
            else:
                errors = []
                if 'email' in request.GET and not isEmailAvailable(request.GET['email']):
                    errors.append("Adresse email déjà utilisée")
                if not 'email' in request.GET:
                    errors.append("Email non renseignée")
                if len(errors) == 0:
                    errors.append("Erreur inconnue. N'hésitez pas à nous contacter")

                var = {
                    'errors': errors
                }
                return render(request, 'auth/signup.html', var)
        else:
            if 'email' in request.POST and 'password' in request.POST and isEmailAvailable(request.POST['email']) and 'password2' in request.POST and request.POST['password'] == request.POST['password2']:
                username = getRandomUsername(request.POST['email'])
                user = User.objects.create_user(email=request.POST['email'].lower(), password=request.POST['password'],
                                                username=username)
                user.save()
                sendEmail(mailjettemplates['new_account_student'], "Bienvenue sur Yedo.", user.email)
                student = Student(user=user, default_password=False)
                student.save()
                if 'referral' in request.POST:
                    referral = Student.objects.get(id=int(request.POST['referral']))
                    ref = Referral(referred=student, referrer=referral)
                    ref.save()
                if 'parrain' in request.POST:
                    parrain = StreetMarketer.objects.get(id=int(request.POST['parrain']))
                    ref = StreetMarketerReferral(referrer=parrain, referred=student)
                    ref.save()
                login(request, user)
                request.session['username'] = user.username
                request.session['email'] = user.email
                return redirect(main_home)
            else:
                errors = []
                if 'referral' in request.POST:
                    referral = Student.objects.get(id=int(request.POST['referral']))
                if 'email' in request.POST and isEmailAvailable(request.POST['email']):
                    request.session['email'] = request.POST['email']
                if 'email' in request.POST and not isEmailAvailable(request.POST['email']):
                    errors.append("Adresse email déjà utilisée")
                if not 'password' in request.POST:
                    errors.append("Mot de passe non renseigné")
                if not 'password2' in request.POST:
                    errors.append("Confirmation du mot de passe non renseignée")
                if not 'email' in request.POST:
                    errors.append("Email non renseignée")
                if 'password' in request.POST and 'password2' in request.POST and request.POST['password'] != request.POST['password2']:
                    errors.append("Les mots de passe sont différents")
                if len(errors) == 0:
                    errors.append("Erreur inconnue. N'hésitez pas à nous contacter")
                email_user = ''
                if 'email' in request.session:
                    email_user = request.session['email']
                var = {
                    'errors': errors,
                    'referral': referral,
                    'email_user': email_user
                }
                return render(request, 'auth/signup.html', var)
    elif 'e' in request.POST or 'e' in request.GET:
        if 'email_sent' in request.GET:
            if request.user and request.user.is_authenticated:
                logout(request)
            if 'username' in request.session:
                del request.session['username']
            if 'email' in request.GET and isEmailAvailable(request.GET['email']):
                p = getRandomPassword()
                username = getRandomUsername(request.GET['email'])
                user = User.objects.create_user(email=request.GET['email'].lower(), password=p,
                                                username=username)
                user.save()
                sendEmail(mailjettemplates['new_account_employeur'], "Bienvenue sur Yedo.", user.email)
                employeur = Employeur(user=user)
                employeur.save()
                login(request, user)
                update_session_auth_hash(request, user)
                request.session['username'] = user.username
                request.session['email'] = user.email
                return redirect(main_home)
            else:
                errors = []
                if 'email' in request.GET and not isEmailAvailable(request.GET['email']):
                    request.session['email_already_used'] = True
                    request.session['email'] = request.GET['email']
                    return redirect(loginviews)
                if not 'email' in request.GET:
                    errors.append("Email non renseignée")
                if len(errors) == 0:
                    errors.append("Erreur inconnue. N'hésitez pas à nous contacter")
                var = {
                    'errors': errors
                }
                return render(request, 'auth/signup.html', var)
        else:
            if 'email' in request.POST and 'password' in request.POST and 'password_two' in request.POST and isEmailAvailable(
                    request.POST['email']) and request.POST['password'] == request.POST['password_two']:
                username = getRandomUsername(request.POST['email'])
                user = User.objects.create_user(email=request.POST['email'].lower(), password=request.POST['password'],
                                                username=username)
                user.save()
                sendEmail(mailjettemplates['new_account_employeur'], "Bienvenue sur Yedo.", user.email)
                employeur = Employeur(user=user, default_password=False)
                employeur.save()
                login(request, user)
                update_session_auth_hash(request, user)
                request.session['username'] = user.username
                request.session['email'] = user.email
                return redirect(main_home)
            else:
                errors = []
                if 'email' in request.POST and not isEmailAvailable(request.POST['email']):
                    errors.append("Adresse email déjà utilisée")
                    if 'email' in request.session:
                        del request.session['email']
                if not 'password' in request.POST:
                    errors.append("Mot de passe non renseigné")
                if not 'password_two' in request.POST:
                    errors.append("Confirmation de mot de passe non renseignée")
                if not 'email' in request.POST:
                    errors.append("Email non renseignée")
                if len(errors) == 0:
                    errors.append("Erreur inconnue. N'hésitez pas à nous contacter")
                var = {
                    'errors': errors
                }
                return render(request, 'auth/signup.html', var)

    else:
        if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
            return redirect(main_home)
        email_user = ''
        if 'email' in request.session:
            email_user = request.session['email']
        var = {'referral': referral, 'parrain': parrain, 'email_user': email_user}
        return render(request, 'auth/signup.html', var)


def loginviews(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        return redirect(main_home)
    errors = []
    if 'email' in request.session:
        email_user = request.session['email']
    else:
        email_user = ''
    email_sent = False
    if 'email_sent' in request.session:
        email_sent = True
        del request.session['email_sent']
    if 'sign_in' in request.POST:
        if 'email' in request.POST and 'password' in request.POST:
            email = request.POST['email'].lower()
            request.session['email'] = email
            try:
                user_object = User.objects.get(email=email)
                user = authenticate(request, username=user_object.username, password=request.POST['password'])
                if user is not None:
                    if len(Student.objects.filter(user=user_object, is_deleted=False)) > 0 or len(Employeur.objects.filter(user=user_object, is_deleted=False)) > 0:
                        login(request, user)
                        update_session_auth_hash(request, user)
                        request.session['username'] = user_object.username
                        return redirect(main_home)
                    elif len(AdminUser.objects.filter(user=user_object)) == 1 and AdminUser.objects.get(user=user_object).admin:
                        login(request, user)
                        update_session_auth_hash(request, user)
                        request.session['username'] = user_object.username
                        return redirect(index)
                    elif len(StreetMarketer.objects.filter(user=user_object)) == 1:
                        login(request, user)
                        update_session_auth_hash(request, user)
                        request.session['username'] = user_object.username
                        return redirect(dashboard_marketer)
                else:
                    errors.append("Les identifiants sont incorrects")
            except User.DoesNotExist:
                errors.append('Adresse email inconnue')
                if 'email' in request.session:
                    del request.session['email']
        else:
            if not 'email' in request.POST:
                errors.append("Email non renseignée")
            if not 'password' in request.POST:
                errors.append("Mot de passe non renseigné")
            if isEmailAvailable(request.POST['email']):
                errors.append("Aucun compte lié à cette adresse mail")

    if 'email' in request.session:
        email_user = request.session['email']
    if 'email_already_used' in request.session:
        errors.append("Vous avez déjà cliqué sur le lien. Connectez vous ci-dessous avec votre email : " + str(request.session['email']) + '.')
        del request.session['email_already_used']
    var = {
        'errors': errors,
        'email_sent': email_sent,
        'email_user': email_user
    }
    return render(request, 'auth/login.html', var)


def logoutviews(request):
    if 'username' in request.session:
        del request.session['username']
    if 'email' in request.session:
        del request.session['email']
    if request.user and request.user.is_authenticated:
        logout(request)
    return redirect(loginviews)

def password(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        return redirect(main_home)
    errors = []
    if 'email' in request.POST and len(request.POST['email']) > 3:
        email = request.POST['email']
        if len(User.objects.filter(email=email)) == 1:
            user = User.objects.get(email=email)
            employeur = None
            student = None
            if len(Employeur.objects.filter(user=user)) == 1:
                employeur = Employeur.objects.get(user=user)
            elif len(Student.objects.filter(user=user)) == 1:
                student = Student.objects.get(user=user)
            p = getRandomPassword()
            if student:
                student.user.set_password(p)
                student.user.save()
                student.default_password = True
                student.save()
                request.session['email_sent'] = True
                mailjetResetPassword(student.user.email, student.name, p)
            if employeur:
                employeur.user.set_password(p)
                employeur.user.save()
                employeur.default_password = True
                employeur.save()
                request.session['email_sent'] = True
                mailjetResetPassword(employeur.user.email, employeur.name, p)
            return redirect(authviews.loginviews)
        else:
            errors.append("Aucun compte Yedo lié à cette adresse mail.")
    var = {
        'errors': errors
    }
    return render(request, 'auth/pass_reset.html', var)





