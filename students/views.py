from django.shortcuts import render, redirect
from django.urls import reverse
from yedo.models import *
from django.http import Http404
from yedo.utils import *
from handleauth import views as authviews
from yedo import views as yedoviews

from yedo.payments import newPayment
from yedo.settings import PRICE_UNLOCK

from random import randint
from yedo.spreadsheet import sendNotif
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    return redirect(search)

def details(request, id):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        background_picture = "https://yedo.s3.eu-west-3.amazonaws.com/static/tus/img/photo/restaurant-1515164783716-8e6920f3e77c.jpg"
        if len(Employeur.objects.filter(is_deleted=False, user=user)) == 1:
            employeur = Employeur.objects.get(user=user)
            employeur.checkIfPremium()
            try:
                student_to_load = Student.objects.get(id=id)
                if not student_to_load.is_visible or student_to_load.is_deleted or student_to_load.signup_step != 4:
                    return redirect(search)
            except Student.DoesNotExist:
                return redirect(search)

            jobs_type = student_to_load.jobs_wanted.all()
            if len(jobs_type) > 0:
                rand = randint(0, len(jobs_type) - 1)
                background_picture = jobs_type[rand].picture_url
            if 'favori' in request.POST:
                employeur.favoris.add(student_to_load)
            if 'del_favori' in request.POST:
                employeur.favoris.remove(student_to_load)
            students = Student.objects.filter(signup_step=4, is_deleted=False, nom__isnull=False, prenom__isnull=False,
                                              zip__isnull=False,
                                              last_updated__gte=datetime.today() - timedelta(days=60),
                                              jobs_wanted__in=student_to_load.jobs_wanted.all()).exclude(
                id=student_to_load.id).distinct().order_by('last_updated')[:20]
            unlocked = False
            if len(Demande.objects.filter(employeur=employeur, student=student_to_load, student_accepted=True,
                                          is_paid=True)) > 0:
                unlocked = True

            var = {
                'student_details': student_to_load,
                'employeur': employeur,
                'students': students,
                'background_picture': background_picture,
                'unlocked': unlocked
            }
            return render(request, 'students/student_details.html', var)
        else:
            return redirect(authviews.loginviews)
    else:
        return redirect(authviews.loginviews)

def search(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Employeur.objects.filter(is_deleted=False, user=user)) == 1:
            employeur = Employeur.objects.get(user=user)
            employeur.checkIfPremium()
            students = []
            jobs_selected = None
            zips_selected = None
            dispos_selected = None
            jours_selected = None
            jobs_type = getJobTypes()
            sort = '-last_updated'
            limit = 200
            filter = False
            zips = Zip.objects.all().order_by('value')
            dispos_type = DisponilityType.objects.all()
            dispo_journee = False
            dispo_soiree = False
            if 'cancelFilter' not in request.POST:
                if 'filter' in request.POST:
                    filter = True
                if 'sort_type' in request.POST:
                    sort = request.POST['sort_type']
                if 'limit' in request.POST:
                    limit = request.POST['limit']
                if 'dates' in request.POST:
                    dates = request.POST.getlist('dates')
                    dates = dates[0].replace('\'', '')
                    if len(dates) > 0:
                        dates = dates.split(', ')
                        formatted_dates = []
                        for d in dates:
                            d = str(d)
                            if len(d) > 0:
                                d = d.replace('/', '')
                                date = datetime.strptime(d, '%d%m%Y')
                                formatted_dates.append(date)
                        jours_selected = formatted_dates
                        if 'favoris' in request.POST:
                            students = employeur.favoris.filter(jours_dispo__date__in=formatted_dates, is_visible= True, is_deleted= False,
                                                                last_updated__gte=datetime.today() - timedelta(
                                                                    days=60)).order_by(sort).distinct()
                        else:
                            students = Student.objects.filter(jours_dispo__date__in=formatted_dates,is_visible= True, is_deleted= False,
                                                              last_updated__gte=datetime.today() - timedelta(days=60),
                                                              signup_step=4).order_by(sort).distinct()
                    else:
                        if 'favoris' in request.POST:
                            students = employeur.favoris.filter(
                                last_updated__gte=datetime.today() - timedelta(days=60),is_visible= True, is_deleted= False).order_by(sort)
                        else:
                            students = getAllEligibleStudents(sort=sort)
                else:
                    if 'favoris' in request.POST:
                        students = employeur.favoris.filter(is_visible= True, is_deleted= False,
                            last_updated__gte=datetime.today() - timedelta(days=60)).order_by(sort)
                    else:
                        students = getAllEligibleStudents(sort=sort)
                if 'jobs' in request.POST:
                    jobs_selected = JobType.objects.filter(pk__in=request.POST.getlist('jobs'))
                    students = students.filter(jobs_wanted__in=request.POST.getlist('jobs')).distinct()

                if 'dispos' in request.POST:
                    id = request.POST['dispos']
                    if id == '10':
                        students = students.filter(dispo_type__intern_id=2, soiree=False)
                        dispo_journee = True
                    elif id == '20':
                        dispo_soiree = True
                        students = students.filter(dispo_type__intern_id=2, soiree=True)
                    else:
                        dispos_selected = DisponilityType.objects.filter(intern_id=int(id))
                        students = students.filter(dispo_type__intern_id=int(id))

                if 'zips' in request.POST:
                    zips_selected = Zip.objects.filter(pk__in=request.POST.getlist('zips'))
                    students = students.filter(zip_obj__in=request.POST.getlist('zips')).distinct()

                if 'pricefrom' in request.POST and 'priceto' in request.POST:
                    students = students.filter(salary__gte=float(request.POST['pricefrom']),
                                               salary__lte=float(request.POST['priceto']))
                elif 'pricefrom' in request.POST:
                    students = students.filter(salary__gte=float(request.POST['pricefrom']))
                elif 'priceto' in request.POST:
                    students.filter(salary__lte=float(request.POST['priceto']))

            else:
                students = getAllEligibleStudents(sort=sort)

            var = {
                'students': students[:limit],
                'sort': sort,
                'limit': limit,
                'jobs_type': jobs_type,
                'zips': zips,
                'filter': filter,
                'employeur': employeur,
                'jobs_selected': jobs_selected,
                'zips_selected': zips_selected,
                'dispos_selected': dispos_selected,
                'dispos_type': dispos_type,
                'jours_selected': jours_selected,
                'dispo_journee': dispo_journee,
                'dispo_soiree': dispo_soiree
            }
            return render(request, 'students/search.html', var)
    return redirect(authviews.loginviews)

def search_by_job_type(request, id):
    return render(yedoviews.main_home)

def all_student(request):
    return render(yedoviews.main_home)

def profile(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Student.objects.filter(is_deleted=False, user=user)) == 1:
            student = Student.objects.get(user=user)
            if not student.name and student.prenom and student.nom:
                student.name = student.prenom + ' ' + student.nom
                student.save()
            jobs = JobType.objects.filter(is_visible=True)
            dispo_type = DisponilityType.objects.filter(is_visible=True)
            if student.signup_step == 1 or student.signup_step == 2 or student.signup_step == 3 or student.default_password:
                return redirect(yedoviews.new)
            sort = '-date'
            if 'sort' in request.POST:
                sort = request.POST['sort']
            if 'accept' in request.POST:
                demande = Demande.objects.get(id=request.POST['demande_id'])
                demande.student_accepted = True
                demande.save()
                sendEmail(mailjettemplates['notif_employeur'], "Demande Yedo acceptée", demande.employeur.user.email)
            if 'refuse' in request.POST:
                demande = Demande.objects.get(id=request.POST['demande_id'])
                demande.student_refused = True
                demande.save()
            if 'video_sent' in request.POST and 'video' in request.FILES:
                student.video = request.FILES['video']
                student.save()
            if 'delete_video' in request.POST:
                student.video = None
                student.save()
            demandes = Demande.objects.filter(student=student).order_by(sort)
            var = {
                'student': student,
                'jobs_type': jobs,
                'dispos_type': dispo_type,
                'demandes': demandes,
                'sort': sort
            }
            return render(request, 'common/common-profile.html', var)
        else:
            return redirect(yedoviews.main_home)
    else:
        return redirect(authviews.loginviews)

def settings(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Student.objects.filter(is_deleted=False, user=user)) == 1:
            student = Student.objects.get(user=user)
            jobs = JobType.objects.filter(is_visible=True)
            dispos_type = DisponilityType.objects.filter(is_visible=True)
            if student.signup_step != 4:
                return redirect(yedoviews.new)

            if 'dispo_type' in request.POST and request.POST['dispo_type'] != '0':

                dispo_type = request.POST['dispo_type']
                dispo = DisponilityType.objects.get(intern_id=dispo_type) if len(DisponilityType.objects.filter(intern_id=dispo_type)) > 0 else None
                student.resetDispo()
                student.dispo_type = dispo

                if 'journee' in request.POST:
                    student.soiree = False if request.POST['journee'] == 1 else True
                if 'stage_remunere' in request.POST:
                    student.stage_remunere = False if request.POST['stage_remunere'] == 0 else True
                if 'nb_days' in request.POST:
                    student.nb_jours_dispos = int(request.POST['nb_days'])
                if 'description_dispo' in request.POST:
                    student.dispo_explications = request.POST['description_dispo']
                student.dispos_set = True
                student.save()

            if 'dates' in request.POST:
                dates = request.POST.getlist('dates')
                dates = dates[0].replace('\'','')
                if len(dates) > 0:
                    dates = dates.split(', ')
                    print(dates)
                    student.jours_dispo.clear()
                    for d in dates:
                        print(d)
                        d = str(d)
                        if len(d) > 0:
                            d = d.replace('/','')
                            date = datetime.strptime(d,'%d%m%Y')
                            if len(JourDispo.objects.filter(date=date)) == 0:
                                student.jours_dispo.create(date=date)
                            else:
                                student.jours_dispo.add(JourDispo.objects.get(date=date))
                student.save()
                return redirect(yedoviews.main_home)

            var = {
                'student': student,
                'jobs_type': jobs,
                'dispos_type': dispos_type
            }
            return render(request, 'students/settings.html', var)
        else:
            return redirect(yedoviews.main_home)
    else:
        return redirect(authviews.loginviews)

def demande(request, id):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Employeur.objects.filter(is_deleted=False, user=user)) == 1:
            employeur = Employeur.objects.get(user=user)
            employeur.checkIfPremium()
            if employeur.signup_step == 0 or not employeur.phone_validated:
                request.session['demande_redirect'] = True
                request.session['student_demande'] = id
                return redirect(yedoviews.new)
            jobs = JobType.objects.filter(is_visible=True).order_by('nom')
            dispos_type = DisponilityType.objects.filter(is_visible=True)
            periodes = Periode.objects.filter(is_visible=True)
            try:
                student_to_load = Student.objects.get(id=id)
                if not student_to_load.is_visible or student_to_load.is_deleted or student_to_load.signup_step != 4:
                    return redirect(yedoviews.main_home)
            except Student.DoesNotExist:
                return redirect(yedoviews.main_home)
            config = None
            if len(ConfigDemande.objects.filter(employeur=employeur)) == 1:
                config = ConfigDemande.objects.get(employeur=employeur)
            if 'form_sent' in request.POST and 'adresse' in request.POST:
                adresse = Adresse.objects.get(id=int(request.POST['adresse']))
                demande = Demande(employeur=employeur, adresse=adresse, student=student_to_load)
                demande.save()
                if 'comment' in request.POST and len(request.POST['comment']) > 1:
                    demande.comment = request.POST['comment']
                if 'dispo_type' in request.POST and len(request.POST['dispo_type']) > 0:
                    dispo = DisponilityType.objects.get(id=int(request.POST['dispo_type']))
                    demande.dispo_type = dispo
                if 'job' in request.POST and len(request.POST['job']) > 0:
                    job = JobType.objects.get(id=int(request.POST['job']))
                    demande.job_type = job
                if 'periode' in request.POST and len(request.POST['periode']):
                    periode = Periode.objects.get(id=int(request.POST['periode']))
                    demande.periode = periode
                if 'dates' in request.POST and len(request.POST['dates']) > 0:
                    dates = request.POST.getlist('dates')
                    dates = dates[0].replace('\'', '')
                    if len(dates) > 0:
                        dates = dates.split(', ')
                        for d in dates:
                            d = str(d)
                            if len(d) > 0:
                                d = d.replace('/', '')
                                date = datetime.strptime(d, '%d%m%Y')
                                if len(JourDispo.objects.filter(date=date)) == 0:
                                    demande.jours.create(date=date)
                                else:
                                    demande.jours.add(JourDispo.objects.get(date=date))
                if employeur.is_premium:
                    demande.is_paid = True
                    demande.amount_paid = PRICE_UNLOCK
                demande.save()
                sendEmail(mailjettemplates['notif_student'], "Nouvelle demande d'employeur", demande.student.user.email)
                if demande.student.phone_validated:
                    sendNotificationSms(demande.student)
                if student_to_load.messenger_id:
                    sendNotif(messenger_id=student_to_load.messenger_id)
                if 'save' in request.POST:
                    if len(ConfigDemande.objects.filter(employeur=employeur)) == 0:
                        config = ConfigDemande(employeur=employeur)
                        if 'comment' in request.POST and len(request.POST['comment']) > 1:
                            config.comment = request.POST['comment']
                        if 'dispo_type' in request.POST and len(request.POST['dispo_type']) > 0:
                            dispo = DisponilityType.objects.get(id=int(request.POST['dispo_type']))
                            config.dispo_type = dispo
                        if 'job' in request.POST and len(request.POST['job']) > 0:
                            job = JobType.objects.get(id=int(request.POST['job']))
                            config.job_type = job
                        if 'periode' in request.POST and len(request.POST['periode']):
                            periode = Periode.objects.get(id=int(request.POST['periode']))
                            config.periode = periode
                        config.save()
                    else:
                        config = ConfigDemande.objects.get(employeur=employeur)
                        if 'comment' in request.POST and len(request.POST['comment']) > 1:
                            config.comment = request.POST['comment']
                        if 'dispo_type' in request.POST and len(request.POST['dispo_type']) > 0:
                            dispo = DisponilityType.objects.get(id=int(request.POST['dispo_type']))
                            config.dispo_type = dispo
                        if 'job' in request.POST and len(request.POST['job']) > 0:
                            job = JobType.objects.get(id=int(request.POST['job']))
                            config.type = job
                        if 'periode' in request.POST and len(request.POST['periode']):
                            periode = Periode.objects.get(id=int(request.POST['periode']))
                            config.periode = periode
                        config.save()
                if demande.is_paid:
                    return redirect(yedoviews.profile)

                return redirect(payment)
            var = {
                'student_details': student_to_load,
                'employeur': employeur,
                'config': config,
                'jobs': jobs,
                'dispos_type': dispos_type,
                'periodes': periodes
            }
            return render(request, 'students/demande.html', var)
        else:
            return redirect(yedoviews.main_home)
    else:
        return redirect(authviews.loginviews)


def unlock(request, id):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Employeur.objects.filter(is_deleted=False, user=user)) == 1:
            employeur = Employeur.objects.get(user=user)
            employeur.checkIfPremium()
            try:
                student_to_load = Student.objects.get(id=id)
                if not student_to_load.is_visible or student_to_load.is_deleted or student_to_load.signup_step != 4:
                    return redirect(yedoviews.main_home)
            except Student.DoesNotExist:
                return redirect(yedoviews.main_home)

            if 'form_sent' in request.POST:
                weeks = int(request.POST['weeks'])
                comment = request.POST['comment']
                salary = float(request.POST['salary'].replace(',', '.'))
                demande = Demande(employeur=employeur, student=student_to_load, weeks=weeks, comment=comment, salary_proposed=salary)
                if employeur.is_premium:
                    demande.is_paid = True
                    demande.amount_paid = PRICE_UNLOCK
                demande.save()
                if not demande.waiting:
                    sendEmail(mailjettemplates['notif_student'], "Nouvelle demande d'employeur", demande.student.user.email)
                    if demande.student.phone_validated:
                        sendNotificationSms(demande.student)
                    if student_to_load.messenger_id:
                        sendNotif(messenger_id=student_to_load.messenger_id)
                if 'save' in request.POST:
                    if len(ConfigDemande.objects.filter(employeur=employeur)) == 0:
                        config = ConfigDemande(employeur=employeur, weeks=weeks, comment=comment, salary=salary)
                        config.save()
                    else:
                        config = ConfigDemande.objects.get(employeur=employeur)
                        config.weeks = weeks
                        config.salary = salary
                        config.comment = comment
                        config.save()
                if demande.is_paid:
                    return redirect(yedoviews.profile)

                return redirect(payment)
            else:
                return redirect(reverse('demande', kwargs={"id": student_to_load.id}))


    else:
        return redirect(authviews.loginviews)

@csrf_exempt
def recap(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Employeur.objects.filter(is_deleted=False, user=user)) == 1:
            employeur = Employeur.objects.get(user=user)
            recharge = False
            abonnement = False
            last_premium = None
            end_date = None
            today = datetime.today()
            if 'plan_selected' in request.POST:
                plan = int(request.POST['plan_selected'])
                if plan == 1:
                    recharge = True
                elif plan == 2:
                    abonnement = True
                    if employeur.is_premium:
                        last_premium = Premium.objects.filter(employeur=employeur, end_date__gte=datetime.today()).order_by('end_date')[0]
                        end_date = last_premium.end_date + timedelta(days=31)
                    else:
                        end_date = datetime.today() + timedelta(days=31)

                elif plan == 3:
                    stat = Stats.objects.all()[0]
                    stat.plan3_clics += 1
                    stat.save()
                    employeur.interest_in_plan3 = True
                    employeur.save()
                    return render(request, 'stay-tuned.html')

                var = {
                    'employeur': employeur,
                    'recharge': recharge,
                    'abonnement': abonnement,
                    'last_premium': last_premium,
                    'end_date': end_date,
                    'today': today
                }

                return render(request, 'payments/recap.html', var)
            else:
                return redirect(payment)
        else:
            return redirect(yedoviews.main_home)

    else:
        return redirect(authviews.loginviews)


def payment(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Employeur.objects.filter(is_deleted=False, user=user)) == 1:
            employeur = Employeur.objects.get(user=user)
            var = {
                'employeur': employeur,
                'pricing': True,
                'payment': True
            }
            if 'plan_selected' in request.POST:
                plan = int(request.POST['plan_selected'])
                if plan == 1:
                    error = None
                    if 'form_amount_sent' in request.POST:
                        if 'amount' in request.POST and request.POST['amount'] != '' and float(request.POST['amount'].replace(',','.')):
                            amount = float(request.POST['amount'].replace(',','.'))
                            price = int(amount * 100)
                            session = newPayment("Ajout de " + str(amount) + " euros de crédit à votre compte!",
                                                 "Merci de faire confiance à Yedo pour votre recrutement",
                                                 'https://yedo.s3.eu-west-3.amazonaws.com/static/tus/img/illustration/undraw_make_it_rain_iwk4.svg',
                                                 price, employeur, "credits")
                            return render(request, 'payments/payment.html', {'session_id': session.id})
                        else:
                            error = "Insérez un montant"
                    var = {
                        'employeur': employeur,
                        'error': error
                    }
                    return render(request, 'pricing.html', var)

                elif plan == 2:
                    days = 31
                    price = 15
                    nb = 1
                    if 'nb_months' in request.POST:
                        nb = int(request.POST['nb_months'])
                        print(nb)
                        days = int(31*nb)
                        if nb == 3:
                            price = 40
                        elif nb == 6:
                            price = 60
                        elif nb == 9:
                            price = 85
                        elif nb == 12:
                            price = 100

                    session = newPayment("Formule Illimité " + str(nb) + " mois!", "Merci de faire confiance à Yedo pour votre recrutement",
                                         'https://yedo.s3.eu-west-3.amazonaws.com/static/tus/img/illustration/undraw_make_it_rain_iwk4.svg',
                                         price*100, employeur, "subscription", days)
                    return render(request, 'payments/payment.html', {'session_id': session.id})

            return render(request, 'pricing.html', var)
        else:
            return redirect(yedoviews.main_home)
    else:
        return redirect(authviews.loginviews)

def profile_infos(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Student.objects.filter(is_deleted=False, user=user)) == 1:
            student = Student.objects.get(user=user)
            print(student.video)
            if student.video:
                print(student.video.url)
            zips = Zip.objects.all().order_by('value')
            languages_text = LanguageText.objects.all().order_by('value_fr')
            languages_levels = LanguageLevel.objects.all().order_by('number')
            to_experience = False

            if 'student_profile' in request.POST and 'added_experience' in request.POST and request.POST['added_experience'] == 'false':
                if 'prenom' in request.POST:
                    student.prenom = request.POST['prenom']
                if 'nom' in request.POST:
                    student.nom = request.POST['nom']
                if 'zip' in request.POST:
                    zip = Zip.objects.get(id=int(request.POST['zip']))
                    student.zip_obj = zip
                if 'salary' in request.POST:
                    student.salary = float(request.POST['salary'].replace(',','.'))
                if 'file' in request.FILES:
                    student.photo = request.FILES['file']
                if 'video' in request.FILES:
                    student.video = request.FILES['video']
                if 'contact' in request.POST and len(request.POST['contact']) > 0 and 'job_type' in request.POST and len(request.POST['job_type']) > 0 and 'nb_semaines' in request.POST and len(request.POST['nb_semaines']) > 0 and 'employeur' in request.POST and len(request.POST['employeur']) > 0:
                    experience = Experience(employeur=request.POST['employeur'], contact=request.POST['contact'], fonction=request.POST['job_type'], duree=int(request.POST['nb_semaines']))
                    experience.save()
                    student.experiences.add(experience)
                    student.updateExperience()
                student.save()
                return redirect(yedoviews.main_home)

            if 'student_profile' in request.POST and 'added_experience' in request.POST and request.POST['added_experience'] == 'true':
                to_experience = True
                if 'prenom' in request.POST:
                    student.prenom = request.POST['prenom']
                if 'nom' in request.POST:
                    student.nom = request.POST['nom']
                if 'zip' in request.POST:
                    zip = Zip.objects.get(id=int(request.POST['zip']))
                    student.zip_obj = zip
                if 'salary' in request.POST:
                    student.salary = float(request.POST['salary'].replace(',','.'))
                if 'file' in request.FILES:
                    student.photo = request.FILES['file']
                if 'video' in request.FILES:
                    student.video = request.FILES['video']
                if 'contact' in request.POST and len(request.POST['contact']) > 0 and 'job_type' in request.POST and len(request.POST['job_type']) > 0 and 'nb_semaines' in request.POST and len(request.POST['nb_semaines']) > 0 and 'employeur' in request.POST and len(request.POST['employeur']) > 0:
                    experience = Experience(employeur=request.POST['employeur'], contact=request.POST['contact'], fonction=request.POST['job_type'], duree=int(request.POST['nb_semaines']))
                    experience.save()
                    student.experiences.add(experience)
                    student.updateExperience()
                if 'language_text' in request.POST and len(request.POST['language_text']) > 0 and 'language_level' in request.POST and len(request.POST['language_level']) > 0:
                    level_id = int(request.POST['language_level'])
                    text_id = int(request.POST['language_text'])
                    already_added = False
                    for i in student.languages:
                        if i.language == LanguageText.objects.get(id=text_id):
                            already_added = True
                            if i.level != LanguageLevel.objects.get(id=level_id):
                                i.level = LanguageLevel.objects.get(id=level_id)
                                i.save()
                    if not already_added:
                        student_lang = LanguageStudent(level=LanguageLevel.objects.get(id=level_id),
                                                       language=LanguageText.objects.get(id=text_id))
                        student_lang.save()
                        student.languages.add(student_lang)
                student.save()

            if 'delete_experience' in request.POST:
                to_experience = True
                experience = Experience.objects.get(id=int(request.POST['experience_id']))
                student.experiences.remove(experience)
                student.updateExperience()
                student.save()

            if 'delete_language' in request.POST:
                to_experience = True
                language = LanguageStudent.objects.get(id=int(request.POST['language_id']))
                student.languages.remove(language)
                student.save()

            var = {
                'student': student,
                'zips': zips,
                'languages_text': languages_text,
                'languages_levels': languages_levels,
                'to_experience': to_experience
            }

            return render(request, 'common/profile_infos.html', var)

        else:
            return redirect(yedoviews.main_home)
    else:
        return redirect(authviews.loginviews)

def refer(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Student.objects.filter(is_deleted=False, user=user)) == 1:
            student = Student.objects.get(user=user)

            var = {
                'student': student
            }
            return render(request, 'students/referral.html', var)

        else:
            return redirect(yedoviews.main_home)
    else:
        return redirect(authviews.loginviews)
def video(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Student.objects.filter(is_deleted=False, user=user)) == 1:
            student = Student.objects.get(user=user)

            var = {
                'student': student
            }
            return render(request, 'common/video.html', var)

        else:
            return redirect(yedoviews.main_home)
    else:
        return redirect(authviews.loginviews)
def photo(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Student.objects.filter(is_deleted=False, user=user)) == 1:
            student = Student.objects.get(user=user)

            var = {
                'student': student
            }
            return render(request, 'common/photo.html', var)

        else:
            return redirect(yedoviews.main_home)
    else:
        return redirect(authviews.loginviews)

def mypreview(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(Student.objects.filter(is_deleted=False, user=user)) == 1:
            student = Student.objects.get(user=user)

            background_picture = "https://yedo.s3.eu-west-3.amazonaws.com/static/tus/img/photo/restaurant-1515164783716-8e6920f3e77c.jpg"

            jobs_type = student.jobs_wanted.all()
            if len(jobs_type) > 0:
                rand = randint(0, len(jobs_type) - 1)
                background_picture = jobs_type[rand].picture_url

            var = {
                'student_details': student,
                'student': True,
                'preview': True,
                'background_picture': background_picture
            }
            return render(request, 'students/student_details.html', var)

        else:
            return redirect(yedoviews.main_home)
    else:
        return redirect(authviews.loginviews)


