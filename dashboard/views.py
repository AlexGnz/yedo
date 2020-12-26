from django.shortcuts import render
from yedo.models import *
from yedo.utils import *
from yedo.views import *
# Create your views here.


def index(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(AdminUser.objects.filter(user=user)) == 1 and AdminUser.objects.get(user=user).admin:
            title = "Accueil"
            monthly, yearly = getSales()
            ratio = getRatio()
            ratio_students = getRatioStudentsEmployeurs()
            last_students, times = getLastStudentsAndTime()
            nb_students = getAmountStudents()
            amount_abonnement = getAmountPremiums()
            amount_credits = getAmountCredits()
            students_registered = Student.objects.filter(signup_step=4)
            students_unregistered = Student.objects.exclude(signup_step=4)
            var = {
                'title': title,
                'monthly_sales': monthly,
                'annual_sales': yearly,
                'ratio': ratio,
                'ratio_students': ratio_students,
                'last_students': last_students,
                'times': times,
                'amount_abonnements': amount_abonnement,
                'amount_credits': amount_credits,
                'nb_students': nb_students,
                'students_registered': students_registered,
                'students_unregistered': students_unregistered
            }
            return render(request, 'dashboard/index.html', var)
        else:
            return redirect(main_home)
    else:
        return redirect(authviews.loginviews)

def allStudents(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(AdminUser.objects.filter(user=user)) == 1 and AdminUser.objects.get(user=user).admin:
            title = "Les étudiants Yedo"
            monthly, yearly = getSales()
            ratio = getRatio()
            ratio_students = getRatioStudentsEmployeurs()
            last_students, times = getLastStudentsAndTime()
            nb_students = getAmountStudents()
            students = Student.objects.all().order_by('last_updated')
            var = {
                'students': students,
                'title': title,
                'monthly_sales': monthly,
                'annual_sales': yearly,
                'ratio': ratio,
                'ratio_students': ratio_students,
                'last_students': last_students,
                'times': times,
                'nb_students': nb_students
            }

            return render(request, 'dashboard/students.html', var)
        else:
            return redirect(main_home)
    else:
        return redirect(authviews.loginviews)

def allEmployeurs(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(AdminUser.objects.filter(user=user)) == 1 and AdminUser.objects.get(user=user).admin:
            title = 'Les employeurs Yedo.'
            monthly, yearly = getSales()
            ratio = getRatio()
            ratio_students = getRatioStudentsEmployeurs()
            last_students, times = getLastStudentsAndTime()
            nb_students = getAmountStudents()
            employeurs = Employeur.objects.all()
            var = {
                'employeurs': employeurs,
                'title': title,
                'monthly_sales': monthly,
                'annual_sales': yearly,
                'ratio': ratio,
                'ratio_students': ratio_students,
                'last_students': last_students,
                'times': times,
                'nb_students': nb_students
            }

            return render(request, 'dashboard/employeurs.html', var)
        else:
            return redirect(main_home)
    else:
        return redirect(authviews.loginviews)

def allJobsType(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(AdminUser.objects.filter(user=user)) == 1 and AdminUser.objects.get(user=user).admin:
            title = 'Les types de job'
            monthly, yearly = getSales()
            ratio = getRatio()
            ratio_students = getRatioStudentsEmployeurs()
            last_students, times = getLastStudentsAndTime()
            nb_students = getAmountStudents()
            job = None
            add_job = False

            if 'to_edit_jobs' in request.POST:
                job_id = request.POST['job_id']
                job = JobType.objects.get(id=job_id)

            if 'edit_job' in request.POST:
                job = JobType.objects.get(id=int(request.POST['edit_job']))
                job.nom = request.POST['nom']
                job.picture_url = request.POST['url']
                job.save()
                job = None
            if 'toggle_visibility' in request.POST:
                job_id = request.POST['job_id']
                job = JobType.objects.get(id=job_id)
                job.toggleVisibility()
                job = None

            if 'add_job' in request.POST:
                add_job = True

            if 'add_job_form' in request.POST and 'nom' in request.POST:
                new_job = JobType(nom=request.POST['nom'])
                if 'url' in request.POST:
                    new_job.picture_url = request.POST['url']
                new_job.save()

            jobs = JobType.objects.all()

            var = {
                'title': title,
                'monthly_sales': monthly,
                'annual_sales': yearly,
                'ratio': ratio,
                'ratio_students': ratio_students,
                'last_students': last_students,
                'times': times,
                'nb_students': nb_students,
                'jobs': jobs,
                'job': job,
                'add_job': add_job
            }

            return render(request, 'dashboard/jobs.html', var)
        else:
            return redirect(main_home)
    else:
        return redirect(authviews.loginviews)

def allDiplomeType(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(AdminUser.objects.filter(user=user)) == 1 and AdminUser.objects.get(user=user).admin:
            title = 'Les types de diplomes'
            monthly, yearly = getSales()
            ratio = getRatio()
            ratio_students = getRatioStudentsEmployeurs()
            last_students, times = getLastStudentsAndTime()
            nb_students = getAmountStudents()
            add_study_type = False
            add_study_domain = False
            add_study_level = False

            if 'delete_type' in request.POST:
                type = StudyType.objects.get(id=int(request.POST['type_id']))
                type.delete()
            if 'delete_domain' in request.POST:
                domain = StudyDomain.objects.get(id=int(request.POST['domain_id']))
                domain.delete()
            if 'delete_level' in request.POST:
                level = StudyLevel.objects.get(id=int(request.POST['level_id']))
                level.delete()


            if 'add_study_type' in request.POST:
                add_study_type = True
                if 'sent' in request.POST:
                    value = request.POST['value_fr']
                    quitting = request.POST['quit']
                    type = StudyType(value_fr=value)
                    type.save()

                    if quitting == 'true':
                        add_study_type = False

            if 'add_study_domain' in request.POST:
                add_study_domain = True
                if 'sent' in request.POST:
                    value = request.POST['value_fr']
                    quitting = request.POST['quit']
                    domain = StudyDomain(value_fr=value)
                    domain.save()

                    if quitting == 'true':
                        add_study_domain = False

            if 'add_study_level' in request.POST:
                add_study_level = True
                if 'sent' in request.POST:
                    value = request.POST['value_fr']
                    quitting = request.POST['quit']

                    level = StudyLevel(value_fr=value)
                    level.save()
                    if quitting == 'true':
                        add_study_level = False

            study_types = StudyType.objects.all()
            study_levels = StudyLevel.objects.all()
            study_domains = StudyDomain.objects.all()

            var = {
                'title': title,
                'monthly_sales': monthly,
                'annual_sales': yearly,
                'ratio': ratio,
                'ratio_students': ratio_students,
                'last_students': last_students,
                'times': times,
                'nb_students': nb_students,
                'study_types': study_types,
                'study_levels': study_levels,
                'study_domains': study_domains,
                'add_study_level': add_study_level,
                'add_study_domain': add_study_domain,
                'add_study_type': add_study_type
            }

            return render(request, 'dashboard/diplomes.html', var)
        else:
            return redirect(main_home)
    else:
        return redirect(authviews.loginviews)

def allLanguages(request):
    if 'username' in request.session and len(User.objects.filter(username=request.session['username'])) == 1:
        user = User.objects.get(username=request.session['username'])
        if len(AdminUser.objects.filter(user=user)) == 1 and AdminUser.objects.get(user=user).admin:
            title = 'Les différentes langues'
            monthly, yearly = getSales()
            ratio = getRatio()
            ratio_students = getRatioStudentsEmployeurs()
            last_students, times = getLastStudentsAndTime()
            nb_students = getAmountStudents()

            add_language_level = False
            add_language_text = False

            if 'delete_level' in request.POST:
                level = LanguageLevel.objects.get(id=int(request.POST['level_id']))
                level.delete()

            if 'delete_text' in request.POST:
                text = LanguageText.objects.get(id=int(request.POST['text_id']))
                text.delete()

            if 'add_language_level' in request.POST:
                add_language_level = True
                if 'sent' in request.POST and 'number' in request.POST and len(request.POST['number']) > 0 and 'value_fr' in request.POST:
                    value = request.POST['value_fr']
                    number = int(request.POST['number'])
                    quitting = request.POST['quit']
                    level = LanguageLevel(value_fr=value, number=number)
                    level.save()

                    if quitting == 'true':
                        add_language_level = False

            if 'add_language_text' in request.POST:
                add_language_text = True
                if 'sent' in request.POST:
                    value = request.POST['value_fr']
                    quitting = request.POST['quit']
                    level = LanguageText(value_fr=value)
                    level.save()

                    if quitting == 'true':
                        add_language_text = False

            languages_levels = LanguageLevel.objects.all()
            languages_text = LanguageText.objects.all()

            var = {
                'title': title,
                'monthly_sales': monthly,
                'annual_sales': yearly,
                'ratio': ratio,
                'ratio_students': ratio_students,
                'last_students': last_students,
                'times': times,
                'nb_students': nb_students,
                'add_language_level': add_language_level,
                'add_language_text': add_language_text,
                'languages_levels': languages_levels,
                'languages_text': languages_text,
            }

            return render(request, 'dashboard/languages.html', var)
        else:
            return redirect(main_home)
    else:
        return redirect(authviews.loginviews)

