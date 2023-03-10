from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from datetime import timedelta
from django.contrib.postgres.fields import ArrayField

class ImportdantDates(models.Model):
    class Meta:
        abstract=True
    created_on = models.DateTimeField(_("Created on"), auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(_("Updated on"), auto_now=True, null=True, blank=True)

class MetaDetails(models.Model):
    class Meta:
        abstract=True
    meta_title = models.CharField(_("Meta Title"), max_length=50, blank=True, null=True)
    meta_description = models.TextField(_("Meta Description"), null=True, blank=True)
    meta_keywords = models.TextField(_("Meta Keywords"), blank=True, null=True)
    created_on = models.DateTimeField(_("Created on"), auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(_("Updated on"), auto_now=True, null=True, blank=True)


class CustomAccountManager(BaseUserManager):
    def create_superuser(self, first_name, email, mobile_number, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True.')

        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be assigned to is_superuser=True.')

        return self.create_user(first_name, email, mobile_number, password, **other_fields)

    def create_user(self, first_name, email, mobile_number, password, **other_fields):
        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, mobile_number=mobile_number, **other_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Meta:
        db_table = 'Users'
        verbose_name = 'User'

    first_name = models.CharField(max_length=20, null=True, blank=False)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True, max_length=150, null=True, blank=False)
    mobile_number = PhoneNumberField(null=True, unique=True, blank=True)
    parent_name = models.CharField(max_length=50, null=True, blank=True)

    class_name = models.CharField(max_length=50, null=True, blank=True)
    school_name = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=40, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)

    password = models.CharField(max_length=200, null=True, blank=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    
    profile_pic = models.ImageField(upload_to="ProfilePictures/", blank=True, default='profilePictures/user.png')

    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

    objects = CustomAccountManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'mobile_number']

    def __str__(self):
        return self.email

class Blogs(MetaDetails):
    title = models.CharField(_("Title"), max_length=250, blank=False, null=True)
    description = models.TextField(_("Description"),blank=True, null=True)
    url = models.SlugField(_("URL"), blank=True, null=True, unique=True)
    image = models.ImageField(_("Image"), upload_to="blog_images/",blank=True, null=True)
    image_alt_name = models.CharField(_("Image Alt Name"), max_length=50, blank=True, null=True)
    overall_description = models.TextField(_("Overall Description"),blank=True, null=True)

    class Meta:
        verbose_name = _("Blogs")
        verbose_name_plural = _("Blogs")

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.url = str(self.url.lower()).strip()
        return super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse("application:blog-detail", kwargs={"url": self.url})

class Events(ImportdantDates):
    title = models.CharField(_("Title"), max_length=250, blank=False, null=True)
    label = models.CharField(_("Label"), max_length=250, blank=False, null=True)
    event_date = models.DateField(_("Event Date"), auto_now=False, auto_now_add=False,blank=False, null=True)
    event_meeting_link = models.URLField(_("Event Meeting Link"), max_length=200,blank=True, null=True)
    image = models.ImageField(_("Image"), upload_to="event_images/",blank=True, null=True)
    image_alt_name = models.CharField(_("Image Alt Name"), max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = _("Events")
        verbose_name_plural = _("Events")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("Events_detail", kwargs={"pk": self.pk})

class RegisterdEvents(ImportdantDates):
    student = models.ForeignKey("application.CustomUser", verbose_name=_("Student"), on_delete=models.CASCADE, blank=True, null=True)
    event = models.ManyToManyField("application.Events", verbose_name=_("Event"), blank=True)

    class Meta:
        verbose_name = _("RegisterdEvents")
        verbose_name_plural = _("RegisterdEvents")

    def get_absolute_url(self):
        return reverse("RegisterdEvents_detail", kwargs={"pk": self.pk})

class News(ImportdantDates):
    event_date = models.DateField(_("Event Date"), auto_now=False, auto_now_add=False,blank=False, null=True)
    image = models.ImageField(_("Image"), upload_to="news_images/",blank=True, null=True)
    image_alt_name = models.CharField(_("Image Alt Name"), max_length=50, blank=True, null=True)
    description = models.TextField(_("Description"),blank=True, null=True)

    class Meta:
        verbose_name = _("News")
        verbose_name_plural = _("News")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("News_detail", kwargs={"pk": self.pk})

class Testimonials(ImportdantDates):
    client_name = models.CharField(_("Client Name"), max_length=50, null=True, blank=True)
    client_role = models.CharField(_("Client Role"), max_length=50, null=True, blank=True)
    image = models.ImageField(_("Image"), upload_to="event_images/",blank=True, null=True)
    image_alt_name = models.CharField(_("Image Alt Name"), max_length=50, blank=True, null=True)
    description = models.TextField(_("Description"),blank=True, null=True)
    assigned_pages = ArrayField(models.CharField(max_length=255, null=True, blank=True), null=True, blank=True)
    class Meta:
        verbose_name = _("Testimonials")
        verbose_name_plural = _("Testimonials")

  
    def get_absolute_url(self):
        return reverse("Testimonials_detail", kwargs={"pk": self.pk})

class ResultAnnouncements(ImportdantDates):
    title = models.CharField(_("Title"), max_length=250, blank=False, null=True)
    winner_name = models.CharField(_("Winner Name"), max_length=250, blank=False, null=True)
    winner_mark= models.CharField(_("Winner Mark"),max_length=20, blank=False, null=True)
    winner_image = models.ImageField(_("Image"), upload_to="winner_images/",blank=True, null=True)
    winner_image_alt_name = models.CharField(_("Winner Image Alt Name"), max_length=50, blank=True, null=True)
    winner_description = models.TextField(_("Winner Description"),blank=True, null=True)

    class Meta:
        verbose_name = _("ResultAnnouncements")
        verbose_name_plural = _("ResultAnnouncements")

   

    def get_absolute_url(self):
        return reverse("ResultAnnouncement_detail", kwargs={"pk": self.pk})

class ContactUs(ImportdantDates):
    full_name = models.CharField(_("Full Name"), max_length=28, blank=True, null=True)
    email = models.EmailField(_("Email"), max_length=254,blank=True, null=True)
    mobile_number = PhoneNumberField(null=True, unique=True, blank=True)
    message = models.TextField(_("Message"),blank=True, null=True)
    
    class Meta:
        verbose_name = _("ContactUs")
        verbose_name_plural = _("ContactUs")

    def __str__(self):
        if self.email:
            return self.email

    def get_absolute_url(self):
        return reverse("ContactUs_detail", kwargs={"pk": self.pk})

class HomeBanners(ImportdantDates):
    title = models.CharField(_("Title"), max_length=250, blank=False, null=True)
    main_title = models.CharField(_("Main Title"), max_length=250, blank=False, null=True)
    description = models.TextField(_("Description"),blank=True, null=True)
    button_name = models.CharField(_("Button Name"), max_length=50, blank=True, null=True)
    button_url = models.URLField(_("Button Url"), max_length=200, blank=True, null=True)
    image = models.ImageField(_("Image"), upload_to="banner_images/",blank=True, null=True)

    class Meta:
        verbose_name = _("HomeBanner")
        verbose_name_plural = _("HomeBanners")


    def get_absolute_url(self):
        return reverse("HomeBanner_detail", kwargs={"pk": self.pk})

class MarqueeTexts(ImportdantDates):
    text = models.TextField(_("Text"),blank=True, null=True)
    

    class Meta:
        verbose_name = _("MarqueeTexts")
        verbose_name_plural = _("MarqueeTexts")

    def get_absolute_url(self):
        return reverse("MarqueeTexts_detail", kwargs={"pk": self.pk})

class Questions(ImportdantDates):
    section = models.CharField(_("Section"), max_length=50, blank=True, null=True)
    section_description = models.TextField(_("Section Description"), blank=True, null=True)
    section_time_limit = models.DurationField(_("Section Duration"),default=timedelta, null=True, blank=True)
    question = models.TextField(_("Question"),null=True, blank=True)
    option1 = models.TextField(_("Option 1"), null=True, blank=True)
    option2 = models.TextField(_("Option 2"), null=True, blank=True)
    option3 = models.TextField(_("Option 3"), null=True, blank=True)
    option4 = models.TextField(_("Option 4"), null=True, blank=True)
    correct_answer = models.TextField(_("Correct Answer"), null=True, blank=True)

    class Meta:
        verbose_name = _("Questions")
        verbose_name_plural = _("Questions")


    def get_absolute_url(self):
        return reverse("Questions_detail", kwargs={"pk": self.pk})

class Papers(MetaDetails):
    title = models.CharField(_("Title"), max_length=50, blank=True, null=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    instructions = models.TextField(_("Instructions"), blank=True, null=True)
    assigned_questions = models.ManyToManyField("application.Questions", verbose_name=_("Questions"), blank=True,)
    is_competitive = models.BooleanField(_("Is competitive"),default=False)
    price = models.DecimalField(_("Price"), max_digits=8, decimal_places=2,blank=True, null=True)
    section_details = ArrayField(models.JSONField(null = True,blank = True), blank=True, null = True)


    class Meta:
        verbose_name = _("Papers")
        verbose_name_plural = _("Papers")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("Papers_detail", kwargs={"pk": self.pk})
    
class CompetitiveExam(ImportdantDates):
    exam_name = models.CharField(_("Exam Name"), max_length=50)
    description = models.TextField(_("Description"), blank=True, null=True)
    assigned_papers = models.ManyToManyField("application.Papers", verbose_name=_("Papers"), blank=True,)
    price = models.DecimalField(_("Price"), max_digits=8, decimal_places=2,blank=True, null=True)

class Subjects(MetaDetails):
    title = models.CharField(_("Title"), max_length=50, blank=True, null=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    assigned_papers = models.ManyToManyField("application.Papers", verbose_name=_("Papers"), blank=True,)
    price = models.DecimalField(_("Price"), max_digits=8, decimal_places=2,blank=True, null=True)
    
    class Meta:
        verbose_name = _("Subjects")
        verbose_name_plural = _("Subjects")

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return reverse("Subjects_detail", kwargs={"pk": self.pk})


class Classes(MetaDetails):
    title = models.CharField(_("Title"), max_length=50, blank=True, null=True)
    description = models.TextField(_("Description"), null=True, blank=True)
    assigned_subjects = models.ManyToManyField("application.Subjects", verbose_name=_("Subjects"), blank=True,)
    price = models.DecimalField(_("Price"), max_digits=8, decimal_places=2,blank=True, null=True)

    class Meta:
        verbose_name = _("Classes")
        verbose_name_plural = _("Classes")

    # def __str__(self):
    #     return self.name

    def get_absolute_url(self):
        return reverse("classes_detail", kwargs={"pk": self.pk})
    

    
class StudentPayments(ImportdantDates):
    ENROLL_CHOICES = [
        ("class","class"),
        ("subject","subject"),
        ("paper","paper"),
        ("competitive-exam","competitive-exam"),
        ("competitive-paper","competitive-paper"),
    ]
    student = models.ForeignKey("application.CustomUser", verbose_name=_("Student"), on_delete=models.CASCADE, blank=True, null=True)
    order_id = models.CharField(_("Order ID"), max_length=40, null=True, blank=True)
    payment_id = models.CharField(_("Payment ID"), max_length=36, null=True, blank=True)
    signature_id = models.CharField(_("Signature ID"), max_length=128, null=True, blank=True)
    price = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10, help_text="In Rupees")
    
    subjects = models.ForeignKey("application.Subjects", verbose_name=_("Subject"), blank=True, null=True, on_delete=models.CASCADE)
    papers = models.ForeignKey("application.Papers", verbose_name=_("Paper"), blank=True, null=True, on_delete=models.CASCADE)
    classes = models.ForeignKey("application.Classes", verbose_name=_("Classe"), blank=True, null=True, on_delete=models.CASCADE)
    competitive_exam = models.ForeignKey("application.CompetitiveExam", verbose_name=_("Competitive Exam"), blank=True, null=True, on_delete=models.CASCADE)
    competitive_paper = models.ForeignKey("application.Papers", verbose_name=_("Competitive Paper"), blank=True, null=True, on_delete=models.CASCADE, related_name="competitive_paper")

    enrolled_type = models.CharField(_("Enrolled Type"), max_length=50, null=True, blank=True,choices=ENROLL_CHOICES)
    class Meta:
        verbose_name = _("StudentPayments")
        verbose_name_plural = _("StudentPayments")

    def __str__(self):
        return f"{self.student.first_name} {self.enrolled_type}"

    def get_absolute_url(self):
        return reverse("enrolls_detail", kwargs={"pk": self.pk})


class StudentSubmittedAnswers(ImportdantDates):
    student = models.ForeignKey("application.CustomUser", verbose_name=_("Student"), on_delete=models.CASCADE, blank=True, null=True)
    question = models.ForeignKey("application.Questions", verbose_name=_("Question"), on_delete=models.CASCADE, blank=True, null=True)
    submitted_answer = models.TextField(_("Correct Answer"), null=True, blank=True)
    is_correct_answer = models.BooleanField(_("Is correct Answer"), default=False)
    answered_time = models.DurationField(_("Answered Time"),default=timedelta, null=True, blank=True)
    class Meta:
        verbose_name = _("StudentSubmittedAnswers")
        verbose_name_plural = _("StudentSubmittedAnswers")

    

class AttendedPapers(ImportdantDates):
    student = models.ForeignKey("application.CustomUser", verbose_name=_("Student"), on_delete=models.CASCADE, blank=True, null=True)
    paper = models.ForeignKey("application.Papers", verbose_name=_("Paper"), blank=True, null=True, on_delete=models.CASCADE)
    attended_questions = models.ManyToManyField("application.StudentSubmittedAnswers", verbose_name=_("Submitted Answers"),blank=True,)

    class Meta:
        verbose_name = _("AttendedPapers")
        verbose_name_plural = _("AttendedPapers")
