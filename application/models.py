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
    mobile_number = PhoneNumberField(null=True, blank=True)
    parent_name = models.CharField(max_length=50, null=True, blank=True)

    class_name = models.CharField(max_length=50, null=True, blank=True)
    school_name = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length = 100, default = "India")
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
    is_external = models.BooleanField(default = False)
    event_meeting_link = models.URLField(_("Event Meeting Link"), max_length=200,blank=True, null=True)
    image = models.ImageField(_("Image"), upload_to="event_images/",blank=True, null=True)
    image_alt_name = models.CharField(_("Image Alt Name"), max_length=50, blank=True, null=True)
    event_fee = models.IntegerField(null = True, blank = True)

    class Meta:
        verbose_name = _("Events")
        verbose_name_plural = _("Events")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("Events_detail", kwargs={"pk": self.pk})

class RegisterdEvents(ImportdantDates):
    student = models.ForeignKey("application.CustomUser", verbose_name=_("Student"), on_delete=models.CASCADE, blank=True, null=True)
    event = models.ForeignKey("application.Events", verbose_name=_("Event"), blank=True, on_delete = models.CASCADE)
    document = models.FileField(upload_to="event_document/",blank=True, null=True)

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
    mobile_number = PhoneNumberField(null=True, blank=True)
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
    title = models.CharField(_("Title"), max_length=250, blank=True, null=True)
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
    image = models.ImageField(upload_to = "question_images/", blank=True, null=True)
    image_link = models.CharField(max_length = 300, null = True, blank = True)
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
    
    def __str__(self):
        return self.question[:200]

class Papers(MetaDetails):
    title = models.CharField(_("Title"), max_length=50, blank=True, null=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    instructions = models.TextField(_("Instructions"), blank=True, null=True)
    assigned_questions = models.ManyToManyField("application.Questions", verbose_name=_("Questions"), blank=True,)
    is_competitive = models.BooleanField(_("Is competitive"),default=False)
    price = models.DecimalField(_("Price"), max_digits=8, decimal_places=2,blank=True, null=True)
    repay_price = models.DecimalField(_("repay_price"), max_digits=8, decimal_places=2,blank=True, null=True)
    section_details = ArrayField(models.JSONField(null = True,blank = True), blank=True, null = True)

    completed_by = models.ManyToManyField("application.CustomUser", verbose_name=_("Completed By"), blank=True)


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
    repay_price = models.DecimalField(_("repay_price"), max_digits=8, decimal_places=2,blank=True, null=True)
    purchase_count = models.IntegerField(default = 0)

class Subjects(MetaDetails):
    title = models.CharField(_("Title"), max_length=50, blank=True, null=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    assigned_papers = models.ManyToManyField("application.Papers", verbose_name=_("Papers"), blank=True,)
    price = models.DecimalField(_("Price"), max_digits=8, decimal_places=2,blank=True, null=True)
    repay_price = models.DecimalField(_("repay_price"), max_digits=8, decimal_places=2,blank=True, null=True)

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
    repay_price = models.DecimalField(_("repay_price"), max_digits=8, decimal_places=2,blank=True, null=True)
    purchase_count = models.IntegerField(default = 0)

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
        ("olympiad-exam","olympiad-exam"),
    ]
    student = models.ForeignKey("application.CustomUser", verbose_name=_("Student"), on_delete=models.CASCADE, blank=True, null=True)
    order_id = models.CharField(_("Order ID"), max_length=40, null=True, blank=True)
    payment_id = models.CharField(_("Payment ID"), max_length=36, null=True, blank=True)
    signature_id = models.CharField(_("Signature ID"), max_length=128, null=True, blank=True)
    price = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10, help_text="In Rupees")
    is_repay = models.BooleanField(default = False)
    subjects = models.ForeignKey("application.Subjects", verbose_name=_("Subject"), blank=True, null=True, on_delete=models.CASCADE)
    papers = models.ForeignKey("application.Papers", verbose_name=_("Paper"), blank=True, null=True, on_delete=models.CASCADE)
    is_attended = models.BooleanField(default = False)
    attended_papers = models.ManyToManyField("application.Papers", blank = True, related_name = "attended_papers")
    classes = models.ForeignKey("application.Classes", verbose_name=_("Classe"), blank=True, null=True, on_delete=models.CASCADE)
    competitive_exam = models.ForeignKey("application.CompetitiveExam", verbose_name=_("Competitive Exam"), blank=True, null=True, on_delete=models.CASCADE)
    competitive_paper = models.ForeignKey("application.Papers", verbose_name=_("Competitive Paper"), blank=True, null=True, on_delete=models.CASCADE, related_name="competitive_paper")
    olympiad_exam = models.ForeignKey("application.OlympiadExam", verbose_name=_("Olympiad Exam"), blank=True, null=True, on_delete=models.CASCADE)
    @property
    def payment_for(self):
        if self.classes:
            return f"Class - {self.classes.title}"
        elif self.competitive_exam:
            return f"Competitive - {self.competitive_exam.exam_name}"
        elif self.subjects:
            return f"Subject - {self.subjects.title}"
        elif self.competitive_paper:
            return f"Paper - {self.competitive_paper.title}"
        elif self.papers:
            return f"Paper - {self.papers.title}"
    @property
    def is_repay_prop(self):
        if self.is_repay:
            return "Yes"
        return "No"
    @property
    def paid_amount(self):
        if self.is_repay:
            return self.repay_amount
        return self.price
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
    paper = models.ForeignKey("application.Papers", verbose_name=_("Paper"), on_delete=models.CASCADE, blank=True, null=True)
    question = models.ForeignKey("application.Questions", verbose_name=_("Question"), on_delete=models.CASCADE, blank=True, null=True)
    submitted_answer = models.TextField(_("Correct Answer"), null=True, blank=True)
    is_correct_answer = models.BooleanField(_("Is correct Answer"), default=False)
    answered_time = models.DurationField(_("Answered Time"),default=timedelta, null=True, blank=True)
    class Meta:
        verbose_name = _("StudentSubmittedAnswers")
        verbose_name_plural = _("StudentSubmittedAnswers")

class AttendedPapers(ImportdantDates):
    student = models.ForeignKey("application.CustomUser", verbose_name=_("Student"), on_delete=models.CASCADE, blank=True, null=True)
    class_obj = models.ForeignKey("application.Classes", null = True, blank = True, on_delete = models.CASCADE)
    competitive_exam = models.ForeignKey("application.CompetitiveExam", null = True, blank = True, on_delete = models.CASCADE)
    olympiad_exam = models.ForeignKey("application.OlympiadExam", null = True, blank = True, on_delete = models.CASCADE)
    paper = models.ForeignKey("application.Papers", verbose_name=_("Paper"), blank=True, null=True, on_delete=models.CASCADE)
    correct_answers = models.IntegerField()
    attended_questions = models.ManyToManyField("application.StudentSubmittedAnswers", verbose_name=_("Submitted Answers"),blank=True,)
    attend_date = models.DateField(_("Attend Date"), auto_now=False, auto_now_add=False, null=True,blank=True)

    @property
    def marks(self):
        correct_answers = 0
        for i in self.attended_questions.all():
            if i.is_correct_answer:
                correct_answers+=1
        return f"{(correct_answers)*10}/{(len(self.attended_questions.all()))*10}"
    
    @property
    def wrong_ans_qno(self):
        qno = []
        for count, i in enumerate(self.attended_questions.all()):
            if not i.is_correct_answer:
                qno.append(count+1)
        return qno
    
    @property
    def correct_ans_qno(self):
        qno = []
        for count, i in enumerate(self.attended_questions.all()):
            if i.is_correct_answer:
                qno.append(count+1)
        return qno

    @property
    def percentile(self):
        position = 0
        submissions = AttendedPapers.objects.filter(paper = self.paper).order_by("correct_answers")
        for i in submissions:
            if i.student == self.student:
                position+=1
                break
            else:
                position+=1
        return int((position/len(submissions))*100)

    @property
    def percentage(self):
        correct_answers = 0
        for i in self.attended_questions.all():
            if i.is_correct_answer:
                correct_answers+=1
        percentage_val = ((correct_answers)/(len(self.attended_questions.all())))*100
        return f"{int(percentage_val)}%"
    @property
    def more_score_count(self):
        position = 0
        submissions = AttendedPapers.objects.filter(paper = self.paper).order_by("correct_answers")
        for i in submissions:
            if i.student == self.student:
                position+=1
                break
            else:
                position+=1
        return int(len(submissions) - position)
    class Meta:
        verbose_name = _("AttendedPapers")
        verbose_name_plural = _("AttendedPapers")

class TempImages(models.Model):
    image = models.ImageField(upload_to = "question_temp_images/")
    paper = models.ForeignKey("application.Papers", verbose_name=_("Paper"), on_delete=models.CASCADE)

    def __str__(self):
        return self.paper.title
    
class OlympiadExam(ImportdantDates):
    paper = models.ForeignKey("application.Papers", verbose_name=_("Paper"), on_delete=models.CASCADE)
    purchase_count = models.IntegerField(default = 0)
    exam_date = models.DateField()
    exam_time = models.TimeField()

    def __str__(self):
        return self.paper.title