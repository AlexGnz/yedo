from yedo.models import *
from yedo.settings import MJ_APIKEY_PUBLIC, MJ_APIKEY_SECRET, mailjettemplates, SMSAPISECRETKEY
from mailjet_rest import Client
import random
from datetime import datetime, timedelta
from smsapi.client import SmsApiComClient
from smsapi.exception import SmsApiException
from django.utils import timezone
now_aware = timezone.now()

def getAllEligibleStudents(limit = None, sort = '-last_updated'):
    return Student.objects.filter(signup_step=4, is_deleted=False, is_visible=True, nom__isnull=False,
                                                  prenom__isnull=False, zip__isnull=False, photo__isnull= False, last_updated__gte=datetime.today() - timedelta(days=60)).order_by(sort)[:limit]

def getJobTypes():
    return JobType.objects.all().filter(is_visible=True)

def getRandomPassword():
    s = "abcdefghijklmnopqrstuvwxyz01234567890"
    passlen = 10
    p = "".join(random.sample(s, passlen))
    return p

def getRandomSMSCode():
    s = "01234567890"
    passlen = 4
    p = "".join(random.sample(s, passlen))
    return p

def getRandomUsername(email):
    username = '' + email.lower().replace('@', '') + getRandomPassword()
    return username

def getSales():
    achats_month = Achat.objects.filter(date__gte=datetime.today() - timedelta(days=31))
    achats_year = Achat.objects.filter(date__gte=datetime.today() - timedelta(days=365))
    somme_month = 0
    somme_year = 0
    for a in achats_month:
        somme_month += a.amount
    for a in achats_year:
        somme_year += a.amount
    return (somme_month, somme_year)

def getRatio():
    inscriptions_completed = Student.objects.filter(signup_step=4).count()
    inscriptions = Student.objects.all().count()
    if inscriptions_completed == 0:
        return 0
    return int((inscriptions_completed/inscriptions)*100)

def getAmountStudents():
    return Student.objects.filter(signup_step=4).count()

def getRatioStudentsEmployeurs():
    employeurs = len(Employeur.objects.filter(signup_step=1))
    students = len(Student.objects.filter(signup_step=4))
    if employeurs == 0:
        return students
    return float(students/employeurs)

def getLastStudentsAndTime():
    students = Student.objects.filter(signup_step=4).order_by('-created_at')[:7]
    times = []
    for s in students:
        times.append({'id': s.id, 'time': datetime.now() - s.created_at})
    return (students, times)

def getAmountPremiums():
    achats = Achat.objects.filter(achat_type="subscription")
    somme = 0
    for a in achats:
        somme += a.amount
    return somme

def getAmountCredits():
    achats = Achat.objects.filter(achat_type="credits")
    somme = 0
    for a in achats:
        somme += a.amount
    return somme

def sendEmailsToUnregisteredStudents():
    # students = Student.objects.exclude(signup_step=4, last_reminder_sent__gte= datetime.now() - timedelta(days=2), unsubscribed=True, amount_sent__lte=7)
    # students = Student.objects.filter(id=1)
    # print(students)
    # if len(students) > 0:
    #     for s in students:
    #         print(hash(s.user.password))
    #         print(s.user.email)
    #         #sendEmail(1020425, "Test", s.user.email)
    #         sendReminderEmail(s.user.email, hash(s.user.password))
    #         s.last_reminder_sent = datetime.now()
    #         s.amount_sent += 1
    #         s.save()
    return True

def sendReminderEmail(email, hash):
    mailjet = Client(auth=(MJ_APIKEY_PUBLIC, MJ_APIKEY_SECRET), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "hello@yedo.io",
                    "Name": 'Yedo.io'
                },
                "To": [
                    {
                        "Email": email,
                        "Name": email
                    }
                ],
                "Variables": {
                    "email": email,
                    "hash": hash
                },
                "TemplateID": mailjettemplates['students_reminder'],
                "TemplateLanguage": True,
                "Subject": "Complète ton profil Yedo"
            }
        ]
    }
    mailjet.send.create(data=data)


def mailjetResetPassword(receiver_email, name, password):
    mailjet = Client(auth=(MJ_APIKEY_PUBLIC, MJ_APIKEY_SECRET), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "hello@yedo.io",
                    "Name": 'Yedo.io'
                },
                "To": [
                    {
                        "Email": receiver_email,
                        "Name": name
                    }
                ],
                "Variables": {
                    "email": receiver_email,
                    "password": password
                },
                "TemplateID": mailjettemplates['pass_reset'],
                "TemplateLanguage": True,
                "Subject": "Réinitialisation de votre mot de passe Yedo.io"
            }
        ]
    }
    mailjet.send.create(data=data)

def sendEmail(template, subject, receiver):
    mailjet = Client(auth=(MJ_APIKEY_PUBLIC, MJ_APIKEY_SECRET), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "hello@yedo.io",
                    "Name": 'Yedo.io'
                },
                "To": [
                    {
                        "Email": receiver
                    }
                ],
                "Variables": {
                    "email": receiver
                },
                "TemplateID": template,
                "TemplateLanguage": True,
                "Subject": subject
            }
        ]
    }
    mailjet.send.create(data=data)

def sendEmailCredits(template, subject, receiver, credits):
    mailjet = Client(auth=(MJ_APIKEY_PUBLIC, MJ_APIKEY_SECRET), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "hello@yedo.io",
                    "Name": 'Yedo.io'
                },
                "To": [
                    {
                        "Email": receiver
                    }
                ],
                "Variables": {
                    "email": receiver,
                    "credits": credits
                },
                "TemplateID": template,
                "TemplateLanguage": True,
                "Subject": subject
            }
        ]
    }
    mailjet.send.create(data=data)


def sendSMS(code, student, phone):
    client = SmsApiComClient(access_token=SMSAPISECRETKEY)
    print("CODE", code)
    try:
        send_results = client.sms.send(to=phone, message='Bienvenue sur yedo. Voici ton code de vérification : ' + str(code))
        print(send_results)
        phone = PhoneValidate(student=student, phone=phone, code=code, sent=True)
        phone.save()
        for result in send_results:
            print(result.id, result.points, result.error)
    except SmsApiException as e:
        print(e.message, e.code)

def sendSMSEmployeur(code, employeur, phone):
    client = SmsApiComClient(access_token=SMSAPISECRETKEY)
    print("CODE", code)
    try:
        send_results = client.sms.send(to=phone, message='Bienvenue sur yedo. Voici votre code de vérification : ' + str(code))
        print(send_results)
        phone = PhoneValidate(employeur=employeur, phone=phone, code=code, sent=True)
        phone.save()
        for result in send_results:
            print(result.id, result.points, result.error)
    except SmsApiException as e:
        print(e.message, e.code)

def sendNotificationSms(student):
    client = SmsApiComClient(access_token=SMSAPISECRETKEY)
    try:
        send_results = client.sms.send(to=student.phone, message='Un employeur t\'a envoyé une demande sur yedo. Connecte toi pour l\'accepter : https://yedo.io')
        for result in send_results:
            print(result.id, result.points, result.error)
    except SmsApiException as e:
        print(e.message, e.code)
