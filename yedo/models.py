

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
import uuid
from django.contrib.auth.models import User
import datetime
from sorl.thumbnail import ImageField, get_thumbnail

class JobType(models.Model):
    nom = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=5000, blank=True, null=True)
    photo = models.FileField(blank=True, null=True, default=None)
    picture_url = models.CharField(max_length=10000, blank=True, null=True)
    is_visible = models.BooleanField(default=True, blank=True, null=True)
    def __str__(self):
        return "%s" % (self.nom)

    def toggleVisibility(self):
        if self.is_visible:
            self.is_visible = False
        else:
            self.is_visible = True
        self.save()

class Zip(models.Model):
    value = models.IntegerField(default=0, blank=True, null=True)
    name_fr = models.CharField(max_length=1000, blank=True, null=True)
    name_nl = models.CharField(max_length=1000, blank=True, null=True)
    def __str__(self):
        return "%s - %s - %s" % (self.value, self.name_nl, self.name_fr)

class Experience(models.Model):
    fonction = models.CharField(max_length=1000, blank=True, null=True)
    duree = models.IntegerField(default=0, blank=True, null=True)
    contact = models.CharField(max_length=1000, null=True, blank=True)
    employeur = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return "%s - %s - %s - %s" % (self.fonction, self.duree, self.employeur, self.contact)

class DisponilityType(models.Model):
    texte = models.CharField(max_length=50, blank=True, null=True)
    is_visible = models.BooleanField(default=True, blank=True, null=True)
    intern_id = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return "%s" % (self.texte)

class Periode(models.Model):
    texte = models.CharField(max_length=50, blank=True, null=True)
    is_visible = models.BooleanField(default=True, blank=True, null=True)
    intern_id = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return "%s" % (self.texte)

class Dispo(models.Model):
    type = models.ForeignKey('DisponilityType', on_delete=models.SET_NULL, blank=True, null=True)
    jours_dispo = models.IntegerField(default=0)
    dispo_explications = models.CharField(max_length=500, blank=True, null=True)
    soiree = models.BooleanField(default=False, blank=True, null=True)
    stage_remunere = models.BooleanField(default=False, null=True, blank=True)

class Horaires(models.Model):
    dispo = models.ForeignKey('Dispo', on_delete=models.SET_NULL, blank=True, null=True)
    begin = models.DateTimeField(auto_now=False, blank=True, null=True)
    end = models.DateTimeField(auto_now=False, blank=True, null=True)

class Adresse(models.Model):
    rue = models.CharField(max_length=1000, blank=True, null=True)
    numero = models.CharField(max_length=1000, blank=True, null=True)
    zip = models.ForeignKey('Zip', on_delete=models.SET_NULL, blank=True, null=True)
    nom = models.CharField(max_length=1000, blank=True, null=True)

class JourDispo(models.Model):
    date = models.DateField(auto_now=False, blank=True, null=True)
    def __str__(self):
        return "%s" % (self.date)

class Demande(models.Model):
    employeur = models.ForeignKey('Employeur', on_delete=models.SET_NULL, blank=True, null=True)
    student = models.ForeignKey('Student', on_delete=models.SET_NULL, blank=True, null=True)
    is_paid = models.BooleanField(default=False, blank=True, null=True)
    amount_paid = models.FloatField(default=0, null=True, blank=True)
    student_accepted = models.BooleanField(default=False, blank=True, null=True)
    student_refused = models.BooleanField(default=False, blank=True, null=True)
    comment = models.CharField(max_length=10000, blank=True, null=True)
    salary_proposed = models.FloatField(default=0, blank=True, null=True)
    dispo_type = models.ForeignKey('DisponilityType',on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True, null=True)
    jours = models.ManyToManyField('JourDispo')
    weeks = models.IntegerField(default=0, blank=True, null=True)
    job_type = models.ForeignKey('JobType', on_delete=models.SET_NULL, blank=True, null=True)
    adresse = models.ForeignKey('Adresse', on_delete=models.SET_NULL, blank=True, null=True)
    periode = models.ForeignKey('Periode', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return "Demande de %s à %s" % (self.employeur.name, self.student.prenom + ' ' + self.student.nom)

class Student(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    nom = models.CharField(max_length=50, default='', blank=True, null=True)
    prenom = models.CharField(max_length=50, default='', blank=True, null=True)
    name = models.CharField(max_length=1000, default='', blank=True, null=True)
    phone = models.CharField(max_length=20, default='', blank=True, null=True)
    phone_validated = models.BooleanField(default=False, blank=True, null=True)
    fb_pic = models.CharField(max_length=5000, default='', blank=True, null=True)
    language = models.CharField(max_length=20, default='fr_FR', blank=True, null=True)
    gender = models.CharField(max_length=20, default='male', blank=True, null=True)
    description = models.CharField(max_length=5000, default='', blank=True, null=True)
    zip = models.IntegerField(default=0)
    zip_obj = models.ForeignKey(Zip, on_delete=models.SET_NULL, blank=True, null=True)
    salary = models.FloatField(default=0, blank=True, null=True)
    exp = models.IntegerField(default=0, blank=True, null=True)
    photo = models.FileField(blank=True, null=True, default=None, upload_to="student_pictures")
    thumbnail = ImageField(upload_to='thumbnails', blank=True, null=True)
    video = models.FileField(blank=True, null=True, default=None, upload_to='videos')
    validated = models.BooleanField(default=False)
    default_password = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False, blank=True, null=True)
    is_visible = models.BooleanField(default=True, blank=True, null=True)
    signup_step = models.IntegerField(default=1)
    jobs_wanted = models.ManyToManyField('JobType', blank=True)
    #dispos = models.ManyToManyField(Dispo)
    dispos_set = models.BooleanField(default=False, null=True, blank=True)
    dispo_type = models.ForeignKey('DisponilityType', on_delete=models.SET_NULL, blank=True, null=True)
    dispo_explications = models.CharField(max_length=500, blank=True, null=True)
    nb_jours_dispos = models.IntegerField(default=0, null=True, blank=True)
    soiree = models.BooleanField(default=False, blank=True, null=True)
    stage_remunere = models.BooleanField(default=False, null=True, blank=True)
    notes = models.ManyToManyField('Rating', blank=True)
    last_updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    messenger_id = models.CharField(max_length=500, blank=True, null=True)
    jours_dispo = models.ManyToManyField('JourDispo', blank=True)
    last_reminder_sent = models.DateTimeField(auto_now_add=True, auto_now=False, blank=True, null=True)
    unsubscribed = models.BooleanField(default=False, null=True, blank=True)
    amount_sent = models.IntegerField(default=0, null=True, blank=True)
    permis = models.BooleanField(default=False, null=True, blank=True)
    experiences = models.ManyToManyField('Experience', blank=True)
    study_type = models.ForeignKey('StudyType', on_delete=models.SET_NULL, null=True, blank=True)
    study_level = models.ForeignKey('StudyLevel', on_delete=models.SET_NULL, null=True, blank=True)
    study_domain = models.ForeignKey('StudyDomain', on_delete=models.SET_NULL, null=True, blank=True)
    age = models.IntegerField(default=18, blank=True, null=True)
    languages = models.ManyToManyField('LanguageStudent', blank=True)

    def __str__(self):
        return "[Step %s] %s" % (self.signup_step, self.prenom + ' ' + self.nom)

    def resetDispo(self):
        self.dispos_set = False
        self.dispo_type = None
        self.dispo_explications = None
        self.soiree = False
        self.stage_remunere = False
        self.nb_jours_dispos = 0
        self.save()
    def updateExperience(self):
        nb = 0
        for i in self.experiences.all():
            nb += i.duree
        self.exp = nb
        self.save()

    def save(self, *args, **kwargs):
        if self.photo:
            self.thumbnail = get_thumbnail(self.photo, "500", crop='center', quality=99).url
        super(Student, self).save(*args, **kwargs)

class Employeur(models.Model):
    name = models.CharField(max_length=500, blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True, null=True)
    is_visible = models.BooleanField(default=True, blank=True, null=True)
    TVA = models.CharField(max_length=50, blank=True, null=True)
    ville = models.CharField(max_length=200, blank=True, null=True)
    adresse = models.CharField(max_length=500, blank=True, null=True, default='')
    adresses = models.ManyToManyField('Adresse', blank=True)
    zip = models.ForeignKey(Zip, on_delete=models.SET_NULL, blank=True, null=True)
    photo = models.FileField(blank=True, null=True, default=None, upload_to="logos_employeurs")
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    language = models.CharField(max_length=20, default='fr_FR', blank=True, null=True)
    default_password = models.BooleanField(default=True)
    phone = models.CharField(max_length=20, default='', blank=True, null=True)
    phone_validated = models.BooleanField(default=False)
    signup_step = models.IntegerField(default=0, null=True, blank=True)
    favoris = models.ManyToManyField('Student', blank=True)
    interest_in_plan3 = models.BooleanField(default=False, blank=True, null=True)
    is_premium = models.BooleanField(default=False, blank=True, null=True)
    credits = models.FloatField(default=0, blank=True, null=True)
    stripe_id = models.CharField(max_length=10000, blank=True, null=True)
    payment_method = models.CharField(max_length=10000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    code_used_at_signup = models.BooleanField(default=False, blank=True, null=True)
    code_used_at_signup_ref = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "%s - %s" % (self.name, self.user.email)

    def checkIfPremium(self):
        if len(Premium.objects.filter(employeur=self, end_date__gte=datetime.date.today())) > 0:
            self.is_premium = True
        else:
            self.is_premium = False
        self.save()

    # def save(self):
    #     if self.photo:
    #         im = Image.open(self.photo)
    #         output = BytesIO()
    #         im = im.resize((100, 100))
    #         im.save(output, format='JPEG', quality=90)
    #         output.seek(0)
    #         self.photo = InMemoryUploadedFile(output, 'FileField', "%s.jpg" % self.photo.name.split('.')[0], 'image/jpeg',
    #                                           sys.getsizeof(output), None)
    #         super(Employeur, self).save()

class Rating(models.Model):
    employeur = models.ForeignKey('Employeur', on_delete=models.SET_NULL, null=True, blank=True)
    note = models.IntegerField(default=0, null=True, blank=True)
    def __str__(self):
        return "%s" % (self.employeur.user.email)

class Stats(models.Model):
    clics_from_fb = models.IntegerField(default=0, null=True, blank=True)
    plan3_clics = models.IntegerField(default=0, null=True, blank=True)
    def __str__(self):
        return "%s clics fb et %s clics plan 3" % (self.clics_from_fb, self.plan3_clics)

class Achat(models.Model):
    employeur = models.ForeignKey('Employeur', on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField(default=0, blank=True, null=True)
    payment_id = models.CharField(max_length=10000, blank=True, null=True)
    date = models.DateTimeField(auto_created=True, blank=True, null=True)
    achat_type = models.CharField(max_length=1000, blank=True, null=True)
    code_promo = models.ForeignKey('CodePromo', on_delete=models.SET_NULL, blank=True, null=True)
    def __str__(self):
        return "%s a payé %s le %s" % (self.employeur.name, self.amount, self.date)

class Premium(models.Model):
    employeur = models.ForeignKey('Employeur', on_delete=models.SET_NULL, blank=True, null=True)
    begin_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "%s, du %s au %s" % (self.employeur.name, self.begin_date, self.end_date)

class ConfigDemande(models.Model):
    employeur = models.ForeignKey('Employeur', on_delete=models.SET_NULL, blank=True, null=True)
    weeks = models.IntegerField(default=0, blank=True, null=True)
    salary = models.FloatField(default=0, blank=True, null=True)
    comment = models.CharField(max_length=10000, blank=True, null=True)
    dispo_type = models.ForeignKey('DisponilityType', on_delete=models.SET_NULL, blank=True, null=True)
    periode = models.ForeignKey('Periode', on_delete=models.SET_NULL, blank=True, null=True)
    adresse = models.ForeignKey('Adresse', on_delete=models.SET_NULL, blank=True, null=True)
    type = models.ForeignKey('JobType', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return "%s - %s semaines, %s euros/h" % (self.employeur.name, self.weeks, self.salary)

class NewsLetter(models.Model):
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return "%s" % (self.email)

class AdminUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    admin = models.BooleanField(default=False, blank=True, null=True)
    nom = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return "%s - %s - %s" % (self.user.username, self.admin, self.nom)

class Diplome(models.Model):
    name = models.CharField(max_length=1000, blank=True, null=True)
    age = models.IntegerField(default=0, blank=True, null=True)
    def __str__(self):
        return "%s - %s" % (self.name, self.age)

class StudyDomain(models.Model):
    value_fr = models.CharField(max_length=1000, blank=True, null=True)
    value_nl = models.CharField(max_length=1000, blank=True, null=True)
    def __str__(self):
        return "%s - %s" % (self.value_fr, self.value_nl)

class StudyLevel(models.Model):
    value_fr = models.CharField(max_length=1000, blank=True, null=True)
    value_nl = models.CharField(max_length=1000, blank=True, null=True)
    def __str__(self):
        return "%s - %s" % (self.value_fr, self.value_nl)

class StudyType(models.Model):
    value_fr = models.CharField(max_length=1000, blank=True, null=True)
    value_nl = models.CharField(max_length=1000, blank=True, null=True)
    def __str__(self):
        return "%s - %s" % (self.value_fr, self.value_nl)

class Referral(models.Model):
    referrer = models.ForeignKey('Student', on_delete=models.SET_NULL, related_name="referrer", null=True, blank=True)
    referred = models.ForeignKey('Student', on_delete=models.SET_NULL, related_name="referred", null=True, blank=True)
    confirmed = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return "%s %s a invité %s %s" % (self.referrer.prenom, self.referrer.nom, self.referred.prenom, self.referred.nom)

class LanguageLevel(models.Model):
    value_fr = models.CharField(max_length=100, blank=True, null=True)
    value_nl = models.CharField(max_length=100, blank=True, null=True)
    number = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return '%s - %s - %s' % (self.value_fr, self.value_nl, self.number)

class LanguageText(models.Model):
    value_fr = models.CharField(max_length=100, blank=True, null=True)
    value_nl = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return '%s - %s' % (self.value_fr, self.value_nl)

class LanguageStudent(models.Model):
    level = models.ForeignKey('LanguageLevel', on_delete=models.SET_NULL, blank=True, null=True)
    language = models.ForeignKey('LanguageText', on_delete=models.SET_NULL, blank=True, null=True)


class StreetMarketer(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=1000, blank=True, null=True)
    code = models.CharField(max_length=100, blank=True, null=True)
    nb_parrainage = models.IntegerField(default=0, null=True, blank=True)
    def __str__(self):
        return "%s. Code : %s. Nombre d'invitations: %s" % (self.name, self.code, self.nb_parrainage)


class StreetMarketerReferral(models.Model):
    referrer = models.ForeignKey('StreetMarketer', blank=True, null=True,on_delete=models.SET_NULL)
    referred = models.ForeignKey('Student', blank=True, null=True,on_delete=models.SET_NULL)
    confirmed = models.BooleanField(default=False, blank=True, null=True)
    def __str__(self):
        return '%s a invité %s. Confirmé: %s' % (self.referrer.name, self.referred.prenom + ' ' + self.referred.nom, self.confirmed)


class PhoneValidate(models.Model):
    student = models.ForeignKey('Student', on_delete=models.SET_NULL, blank=True, null=True)
    employeur = models.ForeignKey('Employeur', on_delete=models.SET_NULL, blank=True, null=True)
    code = models.CharField(max_length=100, blank=True, null=True)
    sent = models.BooleanField(default=False, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return '%s - %s' % (self.student.prenom, self.phone)


class CodePromo(models.Model):
    code = models.CharField(max_length=100, blank=True, null=True)
    amount = models.IntegerField(default=0, blank=True, null=True)
    active = models.BooleanField(default=True, blank=True, null=True)

    def __str__(self):
        return '%s - %s. Actif ? %s' % (self.code, self.amount, self.active)






