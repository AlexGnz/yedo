from django.shortcuts import redirect, render
from django.urls import reverse
from yedo.models import *
from django.contrib.auth import authenticate, get_user, login, logout, update_session_auth_hash
from handleauth import views as authviews
from students import views as studentsviews
from dashboard import views as adminviews
from yedo.utils import *
from django.views.decorators.csrf import csrf_exempt
from yedo.settings import PRICE_UNLOCK, DOMAIN, S_T_R_I_P_E_KEY, S_T_R_I_P_E_ENDPOINT, DEBUG
from datetime import datetime, timedelta
import phonenumbers

import stripe
stripe.api_key = S_T_R_I_P_E_KEY

if DEBUG:
    endpoint_secret = 'whsec_yBwzZLYpJPFoPwQdZt9wKKNnCfcZ9n3H'
else:
    endpoint_secret = S_T_R_I_P_E_ENDPOINT

from django.http import HttpResponse


def main_home(request):
    if 'fbclid' in request.GET:
        stat = Stats.objects.all()[0]
        stat.clics_from_fb += 1
        stat.save()

    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        student = None
        employeur = None
        if len(Student.objects.filter(is_deleted=False, user=user)) > 0 or len(Employeur.objects.filter(is_deleted=False, user=user)) > 0:
            if len(Student.objects.filter(is_deleted=False, user=user)) > 0:
                student = Student.objects.get(user=user)
            elif len(Employeur.objects.filter(is_deleted=False, user=user)) > 0:
                employeur = Employeur.objects.get(user=user)
                employeur.checkIfPremium()
            jobs = JobType.objects.filter(is_visible=True)
            dispo_type = DisponilityType.objects.filter(is_visible=True)
            if student:
                if student.signup_step == 1 or student.signup_step == 2 or student.signup_step == 3 or student.default_password:
                    return redirect(new)
                return redirect(studentsviews.profile)
            if employeur:
                students = getAllEligibleStudents(20)

                var = {
                    'students': students,
                    'employeur': employeur,
                    'jobs_type': jobs,
                    'dispos_type': dispo_type
                }
                return render(request, 'index.html', var)
        elif len(StreetMarketer.objects.filter(user=user)) == 1:
            return redirect(dashboard_marketer)
        elif len(AdminUser.objects.filter(user=user)) == 1 and AdminUser.objects.get(user=user).admin:
            return redirect(adminviews.index)
        else:
            return redirect(authviews.logoutviews)
    else:
        return redirect(authviews.loginviews)

def index_redirect(request):

    return redirect(authviews.signup)

def employeur_signup_redirect(request):
    return redirect(reverse('auth_signup_employeur'))


def index_redirect_fb(request):
    return redirect(authviews.signup)

def index_redirect_mail(request):
    return redirect(authviews.loginviews)

def new(request):
    #
    # if 'email' in request.GET and 'hash' in request.GET:
    #     email = request.GET['email'].lower()
    #     hash_from_email = request.GET['hash']
    #     try:
    #         user = User.objects.get(email=email)
    #         if hash(user.password) == hash_from_email:
    #             user_object = authenticate(request, username=user.username, password=user.password)
    #             login(user_object)
    #     except User.DoesNotExist:
    #         return redirect(authviews.loginviews)

    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Student.objects.filter(is_deleted=False, user=user)) == 1 or len(Employeur.objects.filter(is_deleted=False, user=user)) == 1:
            zips = Zip.objects.all().order_by('value')

            if len(Student.objects.filter(is_deleted=False, user=user)) == 1:
                student = Student.objects.get(user=user)
                if student.signup_step == 4 and not student.default_password:
                    return redirect(main_home)
                study_types = StudyType.objects.all().order_by('value_fr')
                study_levels = StudyLevel.objects.all().order_by('value_fr')
                study_domains = StudyDomain.objects.all().order_by('value_fr')
                languages_text = LanguageText.objects.all().order_by('value_fr')
                languages_levels = LanguageLevel.objects.all().order_by('number')
                sent = False
                parrain = False
                if len(StreetMarketerReferral.objects.filter(referred=student)) == 1:
                    parrain = True
                if len(PhoneValidate.objects.filter(student=student)) > 0:
                    sent = len(PhoneValidate.objects.filter(student=student)) > 0
                jobs_wanted = student.jobs_wanted.all()
                jobs = JobType.objects.filter(is_visible=True)
                verification = False
                error_zip = False
                error_prenom = False
                error_nom = False
                error_phone = False
                error_description = False
                error_wrong_phone = False
                error_phone_used = False
                error_exp = False
                error_photo = False
                to_experience = False
                error_wrong_sms_code = False
                error_sms_code = False
                error_code_sent = False
                template = 1
                disponibility_types = DisponilityType.objects.filter(is_visible=True)

                if 'removeLang' in request.POST and request.POST['removeLang'] != "true" and len(request.POST['removeLang']):
                    obj = LanguageStudent.objects.get(id=int(request.POST['removeLang']))
                    student.languages.remove(obj)

                if 'password' in request.POST:
                    student.user.set_password(request.POST['password'])
                    update_session_auth_hash(request, user)
                    student.user.save()
                    student.default_password = False
                    student.save()
                    return redirect(main_home)

                if 'step1_form' in request.POST and 'added_experience' in request.POST and request.POST['added_experience'] == 'false':
                    if 'prenom' in request.POST:
                        student.prenom = request.POST['prenom']
                    if 'nom' in request.POST:
                        student.nom = request.POST['nom']
                    if student.prenom and student.nom:
                        student.name = student.prenom + ' ' + student.nom
                    if 'phone' in request.POST:
                        phone = '+32' + request.POST['phone']
                        if student.phone == phone and len(Student.objects.filter(phone=phone)) > 1:
                            error_phone_used = True
                        elif student.phone != phone and len(Student.objects.filter(phone=phone)) > 0:
                            error_phone_used = True
                        elif len(PhoneValidate.objects.filter(phone=phone, sent=True)) > 0:
                            error_code_sent = True
                        else:
                            try:
                                x = phonenumbers.parse(phone)
                                if phonenumbers.is_valid_number(x):
                                    student.phone = phone
                                    sendSMS(getRandomSMSCode(), student, phone)
                                else:
                                    error_wrong_phone = True
                            except:
                                error_wrong_phone = True
                    elif not sent:
                        error_phone = True
                    if 'zip' in request.POST and len(request.POST['zip']) > 0:
                        if len(Zip.objects.filter(id=request.POST['zip'])) > 0:
                            student.zip_obj = Zip.objects.get(id=request.POST['zip'])
                    if 'salary' in request.POST and len(request.POST['salary']) > 0:
                        try:
                            student.salary = float(request.POST['salary'].replace(',', '.'))
                        except:
                            student.salary = float(10.0)
                    else:
                        student.salary = float(10.0)
                    if 'permis' in request.POST:
                        if request.POST['permis'] == 'oui':
                            student.permis = True
                        if request.POST['permis'] == 'non':
                            student.permis = False
                    if ('employeur' in request.POST and len(request.POST['employeur']) > 0) or (
                            'contact' in request.POST and len(request.POST['contact']) > 0) or (
                            'job_type' in request.POST and len(request.POST['job_type']) > 0) or (
                            'nb_semaines' in request.POST and len(request.POST['nb_semaines']) > 0 and int(
                            request.POST['nb_semaines'])):
                        experience = Experience()
                        if 'employeur' in request.POST and len(request.POST['employeur']) > 0:
                            experience.employeur = request.POST['employeur']
                        if 'contact' in request.POST and len(request.POST['contact']) > 0:
                            experience.contact = request.POST['contact']
                        if 'job_type' in request.POST and len(request.POST['job_type']) > 0:
                            experience.fonction = request.POST['job_type']
                        if 'nb_semaines' in request.POST and len(request.POST['nb_semaines']) > 0 and int(
                                request.POST['nb_semaines']):
                            experience.duree = int(request.POST['nb_semaines'])
                        experience.save()
                        student.experiences.add(experience)
                        student.updateExperience()

                    if not student.prenom:
                        error_prenom = True
                    if not student.nom:
                        error_nom = True
                    if not student.zip_obj:
                        error_zip = True
                    error_with_phone = error_phone or error_wrong_phone or error_phone_used or error_code_sent
                    if not error_with_phone and not error_nom and not error_prenom and not error_zip:
                        student.signup_step = 2
                    student.save()

                if 'added_experience' in request.POST and request.POST['added_experience'] == 'true':
                    to_experience = True
                    if 'prenom' in request.POST:
                        student.prenom = request.POST['prenom']
                    if 'nom' in request.POST:
                        student.nom = request.POST['nom']
                    if 'phone' in request.POST:
                        phone = '+32' + request.POST['phone']
                        try:
                            if student.phone == phone and len(Student.objects.filter(phone=phone)) > 1:
                                error_phone_used = True
                            elif student.phone != phone and len(Student.objects.filter(phone=phone)) > 0:
                                error_phone_used = True
                            elif len(PhoneValidate.objects.filter(phone=phone, sent=True)) > 0:
                                error_code_sent = True
                            else:
                                x = phonenumbers.parse(phone)
                                if phonenumbers.is_valid_number(x):
                                    student.phone = phone
                                    sendSMS(getRandomSMSCode(), student, phone)
                                else:
                                    error_wrong_phone = True
                        except:
                            error_wrong_phone = True
                    elif not sent:
                        error_phone = True
                    if 'zip' in request.POST and len(request.POST['zip']) > 0:
                        if len(Zip.objects.filter(id=request.POST['zip'])) > 0:
                            student.zip_obj = Zip.objects.get(id=request.POST['zip'])
                    if 'salary' in request.POST and len(request.POST['salary']) > 0:
                        try:
                            student.salary = float(request.POST['salary'].replace(',', '.'))
                        except:
                            student.salary = float(10.0)
                    if 'permis' in request.POST:
                        if request.POST['permis'] == 'oui':
                            student.permis = True
                        if request.POST['permis'] == 'non':
                            student.permis = False
                    if ('employeur' in request.POST and len(request.POST['employeur']) > 0) or ('contact' in request.POST and len(request.POST['contact']) > 0) or ('job_type' in request.POST and len(request.POST['job_type']) > 0) or ('nb_semaines' in request.POST and len(request.POST['nb_semaines']) > 0 and int(request.POST['nb_semaines'])):
                        experience = Experience()
                        if 'employeur' in request.POST and len(request.POST['employeur']) > 0:
                            experience.employeur = request.POST['employeur']
                        if 'contact' in request.POST and len(request.POST['contact']) > 0:
                            experience.contact = request.POST['contact']
                        if 'job_type' in request.POST and len(request.POST['job_type']) > 0:
                            experience.fonction = request.POST['job_type']
                        if 'nb_semaines' in request.POST and len(request.POST['nb_semaines']) > 0 and int(request.POST['nb_semaines']):
                            experience.duree = int(request.POST['nb_semaines'])
                        experience.save()
                        student.experiences.add(experience)
                        student.updateExperience()
                    student.save()

                if 'step2_form' in request.POST:

                    if 'study_type' in request.POST and len(request.POST['study_type']) > 0:
                        student.study_type = StudyType.objects.get(id=int(request.POST['study_type']))
                    if 'study_level' in request.POST and len(request.POST['study_level']) > 0:
                        student.study_level = StudyLevel.objects.get(id=int(request.POST['study_level']))
                    if 'study_domain' in request.POST and len(request.POST['study_domain']) > 0:
                        student.study_domain = StudyDomain.objects.get(id=int(request.POST['study_domain']))

                    if 'age' in request.POST:
                        student.age = int(request.POST['age'])

                    for j in jobs:
                        if 'job_' + str(j.id) in request.POST and request.POST['job_' + str(j.id)]:
                            student.jobs_wanted.add(j)
                        else:
                            student.jobs_wanted.remove(j)

                    if not student.dispos_set and request.POST['added_language'] == "false":
                        dispo_type = request.POST['dispo_type'] if 'dispo_type' in request.POST else None
                        dispo = DisponilityType.objects.get(intern_id=dispo_type) if len(DisponilityType.objects.filter(intern_id=dispo_type)) > 0 else None
                        student.dispo_type = dispo
                        if 'journee' in request.POST:
                            student.soiree = False if request.POST['journee'] == 1 else True
                        if 'stage_remunere' in request.POST:
                            student.stage_remunere = False if request.POST['stage_remunere'] == 0 else True
                        if 'days' in request.POST:
                            student.nb_jours_dispos = int(request.POST['days'])
                        if 'description_dispo' in request.POST:
                            student.dispo_explications = request.POST['description_dispo']
                        student.dispos_set = True
                    if 'dates' in request.POST:
                        dates = request.POST.getlist('dates')
                        dates = dates[0].replace('\'', '')
                        if len(dates) > 0:
                            dates = dates.split(', ')
                            student.jours_dispo.clear()
                            for d in dates:
                                d = str(d)
                                if len(d) > 0:
                                    d = d.replace('/', '')
                                    date = datetime.strptime(d, '%d%m%Y')
                                    if len(JourDispo.objects.filter(date=date)) == 0:
                                        student.jours_dispo.create(date=date)
                                    else:
                                        student.jours_dispo.add(JourDispo.objects.get(date=date))
                    if 'added_language' in request.POST and request.POST['added_language'] == "false":
                        student.signup_step = 3
                    elif 'added_language' in request.POST and request.POST['added_language'] == 'true':
                        if 'language_level' in request.POST and len(request.POST['language_level']) > 0 and 'language_text' in request.POST and len(request.POST['language_text']) > 0:
                            level_id = int(request.POST['language_level'])
                            text_id = int(request.POST['language_text'])
                            already_added = False
                            for i in student.languages.all():
                                if i.language == LanguageText.objects.get(id=text_id):
                                    already_added = True
                                    if i.level != LanguageLevel.objects.get(id=level_id):
                                        i.level = LanguageLevel.objects.get(id=level_id)
                                        i.save()
                            if not already_added:
                                student_lang = LanguageStudent(level=LanguageLevel.objects.get(id=level_id), language=LanguageText.objects.get(id=text_id))
                                student_lang.save()
                                student.languages.add(student_lang)
                    student.save()
                if 'step3_form' in request.POST:
                    if 'file' in request.FILES:
                        student.photo = request.FILES['file']
                        student.save()
                    if 'smscode' in request.POST:
                        if len(PhoneValidate.objects.filter(student=student, code=request.POST['smscode'])) == 1:
                            student.phone_validated = True
                        else:
                            error_wrong_sms_code = True
                    else:
                        error_sms_code = True

                    if 'code' in request.POST:
                        code = request.POST['code'].lower()
                        try:
                            parrain = StreetMarketer.objects.get(code=code)
                            ref = StreetMarketerReferral(referrer=parrain, referred=student, confirmed=True)
                            ref.save()
                        except StreetMarketer.DoesNotExist:
                            pass
                    if len(Referral.objects.filter(referred=student)) == 1:
                        ref = Referral.objects.get(referred=student)
                        ref.confirmed = True
                        ref.save()
                    if len(StreetMarketerReferral.objects.filter(referred=student)) == 1:
                        ref = StreetMarketerReferral.objects.get(referred=student)
                        ref.confirmed = True
                        ref.save()
                    if not error_wrong_sms_code and not error_sms_code:
                        student.signup_step = 4
                    student.save()

                template = student.signup_step
                if 'back' in request.POST and student.signup_step > 1:
                    student.signup_step -= 1
                    template -= 1
                    student.save()
                if student.signup_step == 1:
                    if student.messenger_id:
                        verification = True

                var = {
                    'student': student,
                    'verification': verification,
                    'jobs': jobs,
                    'jobs_wanted': jobs_wanted,
                    'disponibility_types': disponibility_types,
                    'zips': zips,
                    'study_types': study_types,
                    'study_domains': study_domains,
                    'study_levels': study_levels,
                    'error_zip': error_zip,
                    'error_nom': error_nom,
                    'error_phone': error_phone,
                    'error_prenom': error_prenom,
                    'error_description': error_description,
                    'error_exp': error_exp,
                    'error_wrong_phone': error_wrong_phone,
                    'error_phone_used': error_phone_used,
                    'error_photo': error_photo,
                    'to_experience': to_experience,
                    'languages_levels': languages_levels,
                    'languages_text': languages_text,
                    'sent': sent,
                    'parrain': parrain,
                    'error_wrong_sms_code': error_wrong_sms_code,
                    'error_sms_code': error_sms_code,
                    'error_code_sent': error_code_sent

                }

                if student.default_password and student.signup_step == 4:
                    return render(request, 'student-sign-up-steps/define_password.html', var)
                print(template)
                return render(request, 'student-sign-up-steps/step' + str(template) + '.html', var)

            elif len(Employeur.objects.filter(is_deleted=False, user=user)) == 1:
                employeur = Employeur.objects.get(user=user)
                error_same_password = False
                error_password = False
                error_name = False
                error_phone = False
                error_wrong_phone = False
                error_phone_used = False
                error_code_sent = False
                error_adresse = False
                error_code_promo = False
                code_promo_success = ''
                error_zip = False
                sent = False
                student_to_unlock = ''
                redirect_from_demande = False
                if employeur.signup_step == 1 and not employeur.default_password and employeur.phone_validated:
                    return redirect(main_home)

                if 'demande_redirect' in request.session:
                    redirect_from_demande = True
                    del request.session['demande_redirect']
                if 'student_demande' in request.session:
                    student_to_unlock = Student.objects.get(id=int(request.session['student_demande']))
                    del request.session['student_demande']

                if 'step1_form' in request.POST:
                    if 'code_promo' in request.POST and len(request.POST['code_promo']) > 0:
                        print(request.POST['code_promo'])
                        if len(CodePromo.objects.filter(code=request.POST['code_promo'].lower())) == 1:
                            code_promo = CodePromo.objects.get(code=request.POST['code_promo'].lower())
                            achat = Achat(amount=code_promo.amount, employeur=employeur,achat_type='Code promo' + code_promo.code, code_promo=code_promo)
                            achat.save()
                            employeur.credits += code_promo.amount
                            employeur.code_used_at_signup = True
                            employeur.code_used_at_signup_ref = code_promo.code
                            employeur.save()
                            code_promo_success = str(code_promo.amount) + ' euros de crédit ont été ajoutés à votre compte.'
                        else:
                            error_code_promo = True


                    if 'addAdresseInput' in request.POST and request.POST['addAdresseInput'] == 'false':
                        if 'name' in request.POST and len(request.POST['name']) > 0:
                            employeur.name = request.POST['name']

                        if 'phone' in request.POST and len(request.POST['phone']) > 0:
                            phone = '+32' + request.POST['phone']
                            try:
                                if employeur.phone == phone and len(Employeur.objects.filter(phone=phone)) > 1:
                                    error_phone_used = True
                                elif employeur.phone != phone and len(Employeur.objects.filter(phone=phone)) > 0:
                                    error_phone_used = True
                                elif len(PhoneValidate.objects.filter(phone=phone, sent=True)) > 0:
                                    error_code_sent = True
                                else:
                                    x = phonenumbers.parse(phone)
                                    if phonenumbers.is_valid_number(x):
                                        employeur.phone = phone
                                        employeur.save()
                                        sendSMSEmployeur(getRandomSMSCode(), employeur, phone)
                                    else:
                                        error_wrong_phone = True
                            except:
                                error_wrong_phone = True
                        elif not employeur.phone:
                            error_phone = True
                        if 'street' in request.POST and len(
                                request.POST['street']) > 1 and 'numero' in request.POST and len(
                                request.POST['numero']) > 0 and 'zip' in request.POST and len(request.POST['zip']) > 0:
                            adresse = Adresse(rue=request.POST['street'], numero=request.POST['numero'],
                                              zip=Zip.objects.get(id=int(request.POST['zip'])))
                            if 'adresse_name' in request.POST and len(request.POST['adresse_name']) > 0:
                                adresse.nom = request.POST['adresse_name']
                            adresse.save()
                            employeur.adresses.add(adresse)

                        if len(employeur.adresses.all()) == 0:
                            error_adresse = True

                        if not employeur.name:
                            error_name = True
                        error_with_phone = error_phone or error_wrong_phone or error_phone_used or error_code_sent
                        if not error_name and not error_with_phone and not error_adresse:
                            employeur.signup_step = 1
                            employeur.save()
                    elif 'addAdresseInput' in request.POST and request.POST['addAdresseInput'] == 'true':
                        if 'name' in request.POST and len(request.POST['name']) > 0:
                            employeur.name = request.POST['name']

                        if 'street' in request.POST and len(request.POST['street']) > 1 and 'numero' in request.POST and len(request.POST['numero']) > 0 and 'zip' in request.POST and len(request.POST['zip']) > 0:
                            adresse = Adresse(rue=request.POST['street'], numero=request.POST['numero'], zip=Zip.objects.get(id=int(request.POST['zip'])))
                            if 'adresse_name' in request.POST and len(request.POST['adresse_name']) > 0:
                                adresse.nom = request.POST['adresse_name']
                            adresse.save()
                            employeur.adresses.add(adresse)
                    employeur.save()

                if 'pass_reset_form' in request.POST and 'password' in request.POST:
                    employeur.user.set_password(request.POST['password'])
                    update_session_auth_hash(request, user)
                    employeur.user.save()
                    employeur.default_password = False
                    employeur.save()
                    return redirect(main_home)
                error_code = False
                if 'phone_confirm_code' in request.POST:
                    if 'code' in request.POST and len(request.POST['code']) == 4:
                        code = request.POST['code']
                        try:
                            phonevalidate = PhoneValidate.objects.get(employeur=employeur, code=code)
                            employeur.phone_validated = True
                            employeur.save()
                        except:
                            error_code = True
                if len(PhoneValidate.objects.filter(employeur=employeur)) > 0:
                    sent = len(PhoneValidate.objects.filter(employeur=employeur)) > 0

                var = {
                    'employeur': employeur,
                    'zips': zips,
                    'error_same_password': error_same_password,
                    'error_password': error_password,
                    'error_phone': error_phone,
                    'error_adresse': error_adresse,
                    'error_zip': error_zip,
                    'error_name': error_name,
                    'sent': sent,
                    'error_wrong_phone': error_wrong_phone,
                    'error_phone_used': error_phone_used,
                    'error_code_sent': error_code_sent,
                    'redirect_from_demande': redirect_from_demande,
                    'student_to_unlock': student_to_unlock,
                    'error_code_promo': error_code_promo,
                    'code_promo_success': code_promo_success
                }

                if employeur.default_password and employeur.signup_step == 1:
                    return render(request, 'student-sign-up-steps/define_password.html', var)
                if not employeur.phone_validated and employeur.signup_step == 1:
                    return render(request, 'employeur/phone_validate.html', {'employeur': employeur, 'error_code': error_code})
                if not employeur.default_password and employeur.phone_validated and employeur.signup_step == 1:
                    if 'student_to_unlock' in request.POST and len(request.POST['student_to_unlock']) > 0:
                        return redirect(reverse('demande', kwargs={"id": int(request.POST['student_to_unlock'])}))

                    return redirect(main_home)

                return render(request, 'employeur/sign-up.html', var)
        else:
            return redirect(main_home)
    else:
        return redirect(authviews.loginviews)


def search(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        return redirect(studentsviews.search)
    else:
        return redirect(authviews.loginviews)


def terms(request):
    student = None
    employeur = None
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Student.objects.filter(is_deleted=False, user=user)) == 1:
            student = Student.objects.get(user=user)
        elif len(Employeur.objects.filter(is_deleted=False, user=user)) == 1:
            employeur = Employeur.objects.get(user=user)
    var = {
        'employeur': employeur,
        'student': student
    }
    return render(request, 'legal/terms.html', var)


def privacy(request):
    student = None
    employeur = None
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Student.objects.filter(is_deleted=False, user=user)) == 1:
            student = Student.objects.get(user=user)
        elif len(Employeur.objects.filter(is_deleted=False, user=user)) == 1:
            employeur = Employeur.objects.get(user=user)
    var = {
        'employeur': employeur,
        'student': student
    }
    return render(request, 'legal/privacy.html', var)


def sale(request):
    student = None
    employeur = None
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Student.objects.filter(is_deleted=False, user=user)) == 1:
            student = Student.objects.get(user=user)
        elif len(Employeur.objects.filter(is_deleted=False, user=user)) == 1:
            employeur = Employeur.objects.get(user=user)
    var = {
        'employeur': employeur,
        'student': student
    }
    return render(request, 'legal/sale.html', var)


def pricing(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Employeur.objects.filter(is_deleted=False, user=user)) == 1:
            employeur = Employeur.objects.get(user=user)
        else:
            return render(request, 'pricingnologin.html')

        var = {
            'pricing': True,
            'payment': True,
            'employeur': employeur
        }
        return render(request, 'pricing.html', var)
    else:
        return render(request, 'pricingnologin.html')


def payment_success(request):
    return render(request, 'payments/success.html')


def payment_cancel(request):
    return render(request, 'payments/cancel.html')


@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        payment_intent = stripe.PaymentIntent.retrieve(session['payment_intent'])
        employeur = Employeur.objects.get(id=int(payment_intent['metadata']['employeur_id']))
        amount = float(session['display_items'][0]['amount']/100)

        if payment_intent['metadata']['type'] == "credits":
            employeur.credits += amount
            sendEmailCredits(mailjettemplates['achat_credits'], "Votre achat a bien été effectué", employeur.user.email, amount)
        if payment_intent['metadata']['type'] == "subscription":
            days = int(payment_intent['metadata']['days'])
            if len(Premium.objects.filter(employeur=employeur, end_date__gte= datetime.today())) > 0:
                last = Premium.objects.filter(employeur=employeur, end_date__gte=datetime.today()).order_by('end_date')[0]
                premium = Premium(employeur=employeur, begin_date=last.end_date, end_date= last.end_date + timedelta(days=days))
                premium.save()
                employeur.is_premium = True
            else:
                premium = Premium(employeur=employeur, end_date= datetime.today() + timedelta(days=days))
                premium.save()
                employeur.is_premium = True
            sendEmail(mailjettemplates['achat_premium'], "Votre abonnement Premium a bien été activé", employeur.user.email)
        employeur.save()

        achat = Achat(employeur=employeur,amount=amount,payment_id=session['id'], type=payment_intent['metadata']['type'] )
        achat.save()

    return HttpResponse(status=200)


def demo(request):
    return render(request, 'employeur/demo.html')


def profile(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        print(user)
        if len(Employeur.objects.filter(is_deleted=False, user=user)) == 1:
            employeur = Employeur.objects.get(user=user)
            print(employeur)
            jobs = JobType.objects.filter(is_visible=True)
            dispo_type = DisponilityType.objects.filter(is_visible=True)
            if employeur.signup_step == 0:
                return redirect(new)
            print('677')
            if 'unlock' in request.POST:
                if employeur.credits >= PRICE_UNLOCK:
                    d = Demande.objects.get(id=request.POST['unlock'])
                    d.is_paid = True
                    d.amount_paid = PRICE_UNLOCK
                    employeur.credits -= PRICE_UNLOCK
                    employeur.save()
                    d.save()
            if 'pay' in request.POST:
                return redirect(studentsviews.payment)
            print('688')
            if 'cancel' in request.POST:
                demande = Demande.objects.get(id=request.POST['cancel'])
                if demande.is_paid and not employeur.is_premium:
                    demande.employeur.credits += PRICE_UNLOCK
                demande.is_deleted = True
                demande.save()
            sort = '-date'
            print('696')
            if 'sort' in request.POST:
                sort = request.POST['sort']
            demandes = Demande.objects.filter(employeur=employeur).order_by(sort)
            employeur = Employeur.objects.get(id=employeur.id)
            var = {
                'employeur': employeur,
                'jobs_type': jobs,
                'dispos_type': dispo_type,
                'demandes': demandes,
                'sort': sort
            }
            print('708')
            return render(request, 'common/common-profile.html', var)
        else:
            return redirect(main_home)

    else:
        return redirect(authviews.loginviews)


def newsletter(request):
    if 'email' in request.POST:
        news = NewsLetter(email=request.POST['email'])
        news.save()
        return render(request, 'newsletter_success.html')
    return redirect(main_home)


def profile_infos(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Employeur.objects.filter(is_deleted=False, user=user)) == 1:
            employeur = Employeur.objects.get(user=user)
            zips = Zip.objects.all().order_by('value')
            error_remove_adresse = False
            if 'employeur_profile' in request.POST:
                if 'name' in request.POST:
                    employeur.name = request.POST['name']
                if 'phone' in request.POST:
                    employeur.phone = request.POST['phone']
                if 'street' in request.POST:
                    employeur.adresse = request.POST['street']
                if 'zip' in request.POST:
                    zip = Zip.objects.get(id=int(request.POST['zip']))
                    employeur.zip = zip
                if 'file' in request.FILES:
                    employeur.photo = request.FILES['file']
                if 'added_adresse' in request.POST:
                    if 'street' in request.POST and len(
                            request.POST['street']) > 1 and 'numero' in request.POST and len(
                            request.POST['numero']) > 0 and 'zip' in request.POST and len(request.POST['zip']) > 0:
                        adresse = Adresse(rue=request.POST['street'], numero=request.POST['numero'],
                                          zip=Zip.objects.get(id=int(request.POST['zip'])))
                        if 'adresse_name' in request.POST and len(request.POST['adresse_name']) > 0:
                            adresse.nom = request.POST['adresse_name']
                        adresse.save()
                        employeur.adresses.add(adresse)
                employeur.save()
                if 'added_adresse' in request.POST and request.POST['added_adresse'] == 'false':
                    return redirect(main_home)
            if 'delete_adresse' in request.POST:
                if 'adresse_id' in request.POST and int(request.POST['adresse_id']) > 0:
                    if len(employeur.adresses.all()) > 1:
                        adresse = Adresse.objects.get(id=int(request.POST['adresse_id']))
                        employeur.adresses.remove(adresse)
                        employeur.save()
                    else:
                        error_remove_adresse = True

            var = {
                'employeur': employeur,
                'zips': zips,
                'error_remove_adresse':error_remove_adresse
            }
            return render(request, 'common/profile_infos.html', var)
        elif len(Student.objects.filter(is_deleted=False, user=user)) == 1:
            return redirect(studentsviews.profile_infos)
        else:
            return redirect(authviews.loginviews)
    else:
        return redirect(authviews.loginviews)


def unsubscribe(request):
    if 'email' in request.GET and 'hash' in request.GET:
        email = request.GET['email'].lower()
        hash_from_email = request.GET['hash']
        try:
            user = User.objects.get(email=email)
            student = Student.objects.get(user=user)

            if hash(user.password) == hash_from_email:
                student.unsubscribed = True
                student.save()
        except User.DoesNotExist:
            return redirect(authviews.loginviews)


def zipencode(request):
    if 'key' in request.GET and request.GET['key'] == "mysecretkey":
        return HttpResponse("Good try")
        # if 'zip' in request.GET and len(Zip.objects.filter(value=int(request.GET['zip']))) == 0:
        #     zip = Zip(value=int(request.GET['zip']), name_fr=request.GET['name_fr'], name_nl=request.GET['name_nl'])
        #     zip.save()
        #     return HttpResponse("Added")
        # elif 'zip' in request.GET:
        #     if len(Zip.objects.filter(value=int(request.GET['zip']))) == 1:
        #         zip = Zip.objects.get(value=int(request.GET['zip']))
        #         zip.name_fr = request.GET['name_fr']
        #         zip.name_nl = request.GET['name_nl']
        #         zip.save()
        #         return HttpResponse("Edited")
    else:
        return HttpResponse("Not correct key")


def parrainage(request, code):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(StreetMarketer.objects.filter(user=user)) == 1:
            return redirect(dashboard_marketer)

    if len(StreetMarketer.objects.filter(code=code.lower())) == 1:
        parrain = StreetMarketer.objects.get(code=code.lower())
        parrain.nb_parrainage += 1
        parrain.save()
        request.session['parrain'] = parrain.id

    return redirect(authviews.signup)


def dashboard_marketer(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(StreetMarketer.objects.filter(user=user)) == 1:
            parrain = StreetMarketer.objects.get(user=user)
            nb_full_inscrits = len(StreetMarketerReferral.objects.filter(referrer=parrain, confirmed=True)) if len(StreetMarketerReferral.objects.filter(referrer=parrain, confirmed=True)) > 0 else 0
            nb_non_full_inscrits = len(StreetMarketerReferral.objects.filter(referrer=parrain, confirmed=False)) if len(StreetMarketerReferral.objects.filter(referrer=parrain, confirmed=False)) > 0 else 0
            var = {
                'parrain': parrain,
                'inscrits': nb_full_inscrits,
                'nb_inscrits_pas_termine': nb_non_full_inscrits
            }
            return render(request, 'streetmarketer.html', var)
        else:
            return redirect(main_home)
    else:
        return redirect(authviews.loginviews)

def landing_page(request):
    return render(request, 'landing-page.html')




