
from datetime import datetime, date, timedelta
import json
import environ
import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail.message import EmailMessage
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, TemplateView, View
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template

from utils.constants import EmailContents, TextConstants
from utils.functions import OTP_Gen, is_ajax, str_to_timedelta

from .models import *
from django.core.exceptions import BadRequest


class SignUpView(View):
    def get(self,request, *args, **kwargs):
        return render(request, "sign-up.html")
    def post(self,request, *args, **kwargs):
        is_agreed = request.POST.get("flexCheckDefault2")
        if is_agreed == "agreed":
            if CustomUser.objects.filter(email = request.POST.get("email")).exists():
                messages.warning(request,"Email ID already exists")
                return redirect("application:signup")
            user_obj = CustomUser.objects.create(
                first_name = request.POST.get("first_name"),
                last_name = request.POST.get("last_name"),
                email = request.POST.get("email"),
                mobile_number = f'+91{request.POST.get("mobile_number")}',
                parent_name = request.POST.get("parent_name"),
                class_name = request.POST.get("class"),
                school_name = request.POST.get("school_name"),
                country = request.POST.get("country"),
                state = request.POST.get("state"),
                city = request.POST.get("city"),
                gender = request.POST.get("gender"),
            )
            user_obj.set_password(request.POST.get("password"))
            user_obj.save()
            login(request, user_obj)
            return redirect("application:account-dashboard")
        else:
            messages.warning(request,"please agree our terms & conditions to continue")
            return redirect("application:signup")

class SignInView(View):
    def get(self,request, *args, **kwargs):
        return render(request, "sign-in.html")
    
    def post(self,request, *args, **kwargs):
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("application:account-dashboard")
        else:
            messages.error(request,"Invalid Credentials")
            return redirect("application:signin")


class ForgetPassword(View):
    def get(self,request, *args, **kwargs):
        return render(request, "forget-password.html")
    
    def post(self,request, *args, **kwargs):
        if is_ajax(request):
            if request.POST.get("action") == "sendOtp":
                email = request.POST.get("emailId")
                is_exists = CustomUser.objects.filter(email=email).exists()
                if is_exists:
                    print("Send mail")
                    # FIXME -> send OTP
                    generated_otp = OTP_Gen()
                    subject = f'Firststepedu reset password OTP'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [email]
                    plaintext = get_template('email_templates/otp.txt')
                    htmly     = get_template('email_templates/otp.html')

                    d = { 
                        'otp': generated_otp,
                    }

                    text_content = plaintext.render(d)
                    html_content = htmly.render(d)
                    msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                    print("Success")
                    request.session[email]=generated_otp
                    to_return = {
                        "title":"OTP sent",
                        "icon":"success",
                    }
                else:
                    to_return = {
                        "title":"Entered email id doesn't have any active account",
                        "icon":"error",
                    }
                return JsonResponse(to_return,safe=True,)
        else:
            email = request.POST.get("email_id")
            generated_otp = request.session.get(email)
            submitted_otp =  request.POST.get("otp")
            new_password = request.POST.get("new_password")
            if generated_otp != None:
                if generated_otp == submitted_otp:
                    user = CustomUser.objects.get(email=email)
                    user.set_password(new_password)
                    user.save()
                    del request.session[email]
                    messages.success(request,"password has been changed")
                    return redirect("application:signin")
                else:
                    messages.error(request,"Invalid OTP")
            else:
                messages.warning(request,"OTP is not generated for submitted email please click send OTP")
            return redirect("application:forget-password")

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        user_type = request.user.is_superuser
        logout(request)
        if user_type:
            return redirect("admin_dashboard:admin-login")
        else:
            return redirect("application:index-page")

class AccountDashboard(LoginRequiredMixin,View):
    def get(self,request, *args, **kwargs):
        return render(request, "account.html")

    def post(self,request, *args, **kwargs):
        obj = CustomUser.objects.get(id=request.user.id)
        obj.profile_pic = request.FILES.get("image", obj.profile_pic)
        obj.first_name = request.POST.get("first_name",obj.first_name)
        obj.last_name = request.POST.get("last_name",obj.last_name)
        obj.email = request.POST.get("email",obj.email)
        obj.mobile_number = request.POST.get("mobile_number",obj.mobile_number)
        obj.state = request.POST.get("state",obj.state)
        obj.country = request.POST.get("country",obj.country)
        obj.city = request.POST.get("city",obj.city)
        obj.school_name = request.POST.get("school_name",obj.school_name)
        obj.class_name = request.POST.get("class_name",obj.class_name)
        obj.save()
        return redirect("application:account-dashboard")

class IndexView(View):
    def get_registeredEvents(self):
        try:
            events = []
            registerdEvents = RegisterdEvents.objects.filter(student = self.request.user)
            for i in registerdEvents:
                events.append(i.event)
            return events
        except ObjectDoesNotExist as e:
            events = []
            return events
    def get(self,request, *args, **kwargs):
        bannerObj = HomeBanners.objects.all()
        classesObj = Classes.objects.all().order_by("-purchase_count")[:6]
        competitiveExamObj = CompetitiveExam.objects.all().order_by("-purchase_count")[:6]
        today = date.today()
        olympiad_enrolled = []
        if request.user.is_authenticated:
            board_exams = StudentPayments.objects.filter(student=request.user)
            board_exams = board_exams.exclude(enrolled_type__in=["class","subject","paper", "competitive-exam","competitive-paper"])
            for i in board_exams:
                olympiad_enrolled.append(i.olympiad_exam)
        olympiadExamObj = OlympiadExam.objects.filter(exam_date__gte=today).order_by("-purchase_count")[:6]
        results = ResultAnnouncements.objects.all()[:6]
        news=News.objects.all()[:6]
        blogs = Blogs.objects.all().order_by("created_on")[:3]
        testimonials = Testimonials.objects.all()[:6]
        events = Events.objects.all().order_by("created_on")[:3]
        current_time = datetime.now()
        one_hour_after = current_time + timedelta(hours=1)
        context = {
            "bannerObj":bannerObj,
            "classesObj":classesObj,
            "competitiveExamObj":competitiveExamObj,
            "olympiadExamObj":olympiadExamObj,
            "olympiad_enrolled":olympiad_enrolled,
            "resultsObj":results,
            "news":news,
            "blogs":blogs,
            "testimonials":testimonials,
            "events":events,
            "one_hour_after": one_hour_after,
        }
        context["registered_events"] = []
        if request.user.is_authenticated:
            context["registered_events"] = self.get_registeredEvents()
        return render(request, "index.html",context)
    
    def post(self, request, *args, **kwargs):
        if request.POST.get("action") == "register":
            event = Events.objects.get(id = request.POST.get("eventId"))
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            resp = client.order.create(
                {"amount": float(event.event_fee) * 100, "currency": "INR", "payment_capture": "1"}
            )
            callBackUrl = reverse("event-callback",kwargs={"id":request.POST.get("eventId"), "uid": request.user.id})
            callBackUrl = request.build_absolute_uri(f"{callBackUrl}")
            print(callBackUrl)
            con = {
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order_id": resp["id"],
                "price":resp["amount"],
                "callback_url":callBackUrl,
            }
            # eventId = request.POST.get("eventId")
            # evnt = Events.objects.get(id=eventId)
            # if not RegisterdEvents.objects.filter(student = request.user, event = evnt).exists():
            #     obj = RegisterdEvents.objects.create(student = request.user, event = evnt)
            # res = {"msg":"Event Registered"}
            res = con
        else:
            blog_count = request.POST.get("blogCount")
            start_num = int(blog_count)
            end_num = start_num + self.paginate_by
            evnt = Events.objects.all().order_by("created_on")
            objs = evnt[start_num:end_num]
            data = serializers.serialize('json', objs, fields=("id","title","label","event_date","image","image_alt_name"))
            registerdEvents_ids = self.get_registeredEvents()
            res = {"data":data, "media_url":settings.MEDIA_URL,"registerdEvents_ids":registerdEvents_ids}
        return JsonResponse(res)

class AboutUs(View):
    def get(self, request):
        testimonials = Testimonials.objects.all()[:6]
        context = {"testimonials": testimonials}
        template_name="about-us.html" 
        return render(request, template_name, context=context)
    

class WhyChooseUs(View):
    def get(self, request):
        testimonials = Testimonials.objects.all()[:6]
        context = {"testimonials": testimonials}
        template_name="why-choose-us.html"
        return render(request, template_name, context=context)


class OurTeam(TemplateView):
    template_name="our-team.html"


class BlogsList(ListView):
    template_name = "blog.html"
    model = Blogs
    # FIXME - > pagenated count for developement i just put 6 count  
    paginate_by = 6
    ordering = "created_on"

    def get_context_data(self,**kwargs):
        env = environ.Env()
        blog_url = env.get_value("blog_url")
        context = super(BlogsList,self).get_context_data(**kwargs)
        list_exam = Blogs.objects.all().order_by("created_on").defer("id","title","image","description","url","image_alt_name")
        context["blog_url"] = blog_url
        context["show_loadmore"] = False
        if len(list_exam)>self.paginate_by:
            context["show_loadmore"] = True
        return context

    def post(self, request, *args, **kwargs):
        blog_count = request.POST.get("blogCount")
        print(blog_count)
        start_num = int(blog_count)
        end_num = start_num + self.paginate_by
        list_exam = Blogs.objects.all().order_by("created_on").defer("id","title","image","description","url","image_alt_name")
        objs = list_exam[start_num:end_num]
        data = serializers.serialize('json', objs, fields=("id","title","image","description","url","image_alt_name")),
        show_loadmore = False
        if int(blog_count)+self.paginate_by < len(list_exam):
            show_loadmore = True
        res = {"data":data, "media_url":settings.MEDIA_URL, "show_loadmore": show_loadmore}
        return JsonResponse(res)

class BlogView(View):
    def get(self, request, *args, **kwargs):
        blogsObj = Blogs.objects.all()[:6]
        context = {
            "objs":blogsObj,
        }
        return render(request,"blog.html",context)
    

class BlogDetailView(DetailView):
    template_name = "bloglanding.html"
    model = Blogs
    slug_field = 'url'
    slug_url_kwarg = 'url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recent_blogs = Blogs.objects.all().order_by("created_on")[:3]
        context["recent_blogs"] = recent_blogs
        return context


class Announcement(View):
    def get(self, request):
        template_name="announcement.html"
        results = ResultAnnouncements.objects.all()
        context = {"resultsObj":results}
        return render(request, template_name, context = context)
    
class DashboardResult(View):
    def get(self, request):
        user = request.user
        attended_papers = AttendedPapers.objects.filter(student = user)
        print(attended_papers)
        context = {"attended_papers": attended_papers}
        return render(request, "result.html", context = context)

class ContactUsView(View):
    def get(self, request, *args, **kwargs):
        return render(request,"contact.html")
    
    def post(self, request, *args, **kwargs):
        ContactUs.objects.create(
            full_name=request.POST.get("full_name"),
            email=request.POST.get("email"),
            mobile_number=request.POST.get("mobile_number"),
            message=request.POST.get("message"),
        )
        messages.success(request, TextConstants.contact_enquiry_success_msg)
        return redirect("application:index-page")

class CompetitivePage(View):
    def get(self, request, *args, **kwargs):
        obj = CompetitiveExam.objects.all().order_by("created_on")
        testimonials = Testimonials.objects.all()[:6]
        context = {
            "objs":obj,
            "testimonials": testimonials,
        }
        return render(request, "competitive.html",context)

    def post(self, request, *args, **kwargs):
        objId = request.POST.get("choosedClass")
        if objId != "popular":
            classes_obj = CompetitiveExam.objects.get(id=objId)

            buyPaperWise = reverse("application:school_paper_wise")
            buyPaperWise = request.build_absolute_uri(f"{buyPaperWise}?competitive={objId}")
        
            redirectUrl = reverse("application:checkout",kwargs={"id":objId})
            redirectUrl = request.build_absolute_uri(f"{redirectUrl}?type=competitive-exam")

            toReturn = {
                "id":classes_obj.id,
                "title":classes_obj.exam_name,
                "description":classes_obj.description,
                "count":classes_obj.assigned_papers.count(),
                "buyPaperWise":buyPaperWise,
                "buyClass":redirectUrl,
            }
        else:
            objs = CompetitiveExam.objects.all().order_by("-purchase_count")
            data = serializers.serialize('json', objs)
            toReturn = {"data": data}

        return JsonResponse(toReturn)

class OlympiadPage(View):
    def get(self, request, *args, **kwargs):
        today = date.today()
        obj = OlympiadExam.objects.filter(exam_date__gte=today).order_by("created_on")
        testimonials = Testimonials.objects.all()[:6]
        board_exams = []
        if request.user.is_authenticated:
            board_exams = StudentPayments.objects.filter(student=request.user)
            board_exams = board_exams.exclude(enrolled_type__in=["class","subject","paper", "competitive-exam","competitive-paper"])
        olympiad_enrolled = []
        for i in board_exams:
            olympiad_enrolled.append(i.olympiad_exam)
        current_time = datetime.now()
        one_hour_after = current_time + timedelta(hours=1)
        context = {
            "objs":obj,
            "testimonials": testimonials,
            "olympiad_enrolled": olympiad_enrolled,
            "one_hour_after": one_hour_after,
        }
        return render(request, "olympiad.html",context)
    
    def post(self, request, *args, **kwargs):
        objId = request.POST.get("choosedClass")
        if objId != "popular":
            olympiad_obj = OlympiadExam.objects.get(id=objId)
            redirectUrl = reverse("application:checkout",kwargs={"id":objId})
            redirectUrl = request.build_absolute_uri(f"{redirectUrl}?type=olympiad-exam")

            toReturn = {
                "id":olympiad_obj.id,
                "title":olympiad_obj.paper.title,
                "price": olympiad_obj.paper.price,
                "description":olympiad_obj.paper.description,
                "buyClass":redirectUrl,
                "exam_date": olympiad_obj.exam_date,
                "exam_time": olympiad_obj.exam_time
            }
        else:
            objs = OlympiadExam.objects.all().order_by("-purchase_count")
            data = []
            for obj in objs:
                redirectUrl = reverse("application:checkout",kwargs={"id":obj.id})
                redirectUrl = request.build_absolute_uri(f"{redirectUrl}?type=olympiad-exam")
                data.append({
                    "id":obj.id,
                    "title":obj.paper.title,
                    "price": obj.paper.price,
                    "description":obj.paper.description,
                    "buyClass":redirectUrl,
                    "exam_date": obj.exam_date,
                    "exam_time": obj.exam_time
                })
            toReturn = {"data": data}

        return JsonResponse(toReturn)

class EventsPage(ListView):
    template_name = "events.html"
    model = Events
    # FIXME - > pagenated count.. for developement i just put 3  
    paginate_by = 3
    ordering = "created_on"

    def get_registeredEvents(self):
        try:
            events = []
            registerdEvents = RegisterdEvents.objects.filter(student = self.request.user)
            for i in registerdEvents:
                events.append(i.event)
            return events
        except :
            events = []
            return events

    def get_context_data(self,**kwargs):
        context = super(EventsPage,self).get_context_data(**kwargs)
        context["registered_events"] = self.get_registeredEvents()
        context["show_loadmore"] = False
        if len(Events.objects.all()) > self.paginate_by:
            context["show_loadmore"] = True
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get("action") == "register":
            event = Events.objects.get(id = request.POST.get("eventId"))
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            resp = client.order.create(
                {"amount": float(event.event_fee) * 100, "currency": "INR", "payment_capture": "1"}
            )
            callBackUrl = reverse("event-callback",kwargs={"id":request.POST.get("eventId"), "uid": request.user.id})
            callBackUrl = request.build_absolute_uri(f"{callBackUrl}")
            print(callBackUrl)
            con = {
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order_id": resp["id"],
                "price":resp["amount"],
                "callback_url":callBackUrl,
            }
            # eventId = request.POST.get("eventId")
            # evnt = Events.objects.get(id=eventId)
            # if not RegisterdEvents.objects.filter(student = request.user, event = evnt).exists():
            #     obj = RegisterdEvents.objects.create(student = request.user, event = evnt)
            # res = {"msg":"Event Registered"}
            res = con
        else:
            blog_count = request.POST.get("blogCount")
            start_num = int(blog_count)
            end_num = start_num + self.paginate_by
            evnt = Events.objects.all().order_by("created_on")
            objs = evnt[start_num:end_num]
            data = serializers.serialize('json', objs, fields=("id","title","label","event_date","image","image_alt_name", "is_external", "event_meeting_link"))
            registerdEvents_ids = []
            for i in self.get_registeredEvents():
                registerdEvents_ids.append(i.id)
            show_loadmore = False
            if len(evnt)>end_num:
                show_loadmore = True
            res = {"data":data, "media_url":settings.MEDIA_URL,"registerdEvents_ids":registerdEvents_ids, "show_loadmore": show_loadmore}
        return JsonResponse(res)
    

class RegisterdEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            events = RegisterdEvents.objects.filter(student = self.request.user).order_by("-id")
        except ObjectDoesNotExist as e:
            events = []
        finally:
            context = {
                "events":events,
            }
            return render(request,"dash-events.html", context)
        
    def post(self, request):
        try:
            registered_event = RegisterdEvents.objects.get(student = request.user, event = Events.objects.get(id = request.POST["eventId"]))
            registered_event.document = request.FILES["document"]
            registered_event.save()
            to_return = {"status": "Success"}
            return JsonResponse(to_return,safe=True)
        except:
            raise BadRequest('Invalid files.')


class EnrolledClassesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        board_exams = StudentPayments.objects.filter(student=request.user)
        attended_exams = AttendedPapers.objects.filter(student =request.user, olympiad_exam__isnull = False)
        attended_olympiads = []
        for i in attended_exams:
            attended_olympiads.append(i.olympiad_exam)
        context = {
            "board_exams":board_exams.exclude(enrolled_type__in=["competitive-exam","competitive-paper", "olympiad-exam"]),
            "competitive_exams_list":board_exams.exclude(enrolled_type__in=["class","subject","paper", "olympiad-exam"]),
            "olympiad_exams":board_exams.exclude(enrolled_type__in=["class","subject","paper", "competitive-exam","competitive-paper"]),
            "attended_olympiads": attended_olympiads
        }
        return render(request,"enrolled.html",context)


class EnrolledSubjectsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        obj = StudentPayments.objects.get(id=kwargs.get("id"))
        attended_papers = obj.attended_papers.all()
        
        context = {
            "obj":obj,
            "attended_papers": attended_papers
        }
        return render(request,"view-paper.html",context)
    


class ExamView(View):
    def get(self,request, *args, **kwargs):
        class_id = request.GET.get("class")
        subject_id = request.GET.get("subject")
        competitive_exam_id = request.GET.get("competitive-exam")
        paper_id = kwargs.get("id")
        paper_obj = get_object_or_404(Papers,id=paper_id)
        questions = paper_obj.assigned_questions.all()

        SECTION_DETAILS = []
        TOTAL_QUES = 0
        ALL_QUES = []
        
        if paper_obj.section_details:
            for count, section_detail in enumerate(paper_obj.section_details):
                to_dict = json.loads(section_detail)
                section_questions = questions.filter(section=to_dict["name"])
                SECTION_QUES_COUNT = section_questions.count()
                to_dict["questions"] = section_questions
                to_dict["questions_count"] = SECTION_QUES_COUNT
                TOTAL_QUES += SECTION_QUES_COUNT
                SECTION_DETAILS.append(to_dict)
                
                if count == 0:
                    to_dict["section_questions_details"] = f"1 - {SECTION_QUES_COUNT}"
                else:
                    previous_dict = SECTION_DETAILS[count]
                    previous_el = SECTION_DETAILS[count-1]["questions_count"]
                    previous_dict["section_questions_details"] = f"{previous_el+1} - {previous_el+SECTION_QUES_COUNT}"
                ALL_QUES.extend(section_questions)
        TOTAL_TIME =sum([ques.section_time_limit for ques in ALL_QUES],timedelta(0,0))
        TIME_IN_MIN = TOTAL_TIME.total_seconds()/60

        if class_id and subject_id:
            class_obj = get_object_or_404(Classes,id=class_id)
            subject_obj = get_object_or_404(Subjects,id=subject_id)
            context = {
            "class_obj":class_obj,
            "subject_obj":subject_obj,
            "paper_obj":paper_obj,
            "section_details":SECTION_DETAILS,
            "total_ques":TOTAL_QUES,
            "all_ques":ALL_QUES,
            "tot_time":TIME_IN_MIN,
            }
        elif not class_id and subject_id:
            subject_obj = get_object_or_404(Subjects,id=subject_id)
            context = {
                "subject_obj":subject_obj,
                "paper_obj":paper_obj,
                "section_details":SECTION_DETAILS,
                "total_ques":TOTAL_QUES,
                "all_ques":ALL_QUES,
                "tot_time":TIME_IN_MIN,
            }
        elif competitive_exam_id:
            competitive_exam_obj = get_object_or_404(CompetitiveExam,id=competitive_exam_id)

            # FIXME ALL_QUES and TOTAL_QUES
            ALL_QUES = questions
            TOTAL_QUES = len(questions)
            TOTAL_TIME =sum([ques.section_time_limit for ques in ALL_QUES],timedelta(0,0))
            TIME_IN_MIN = TOTAL_TIME.total_seconds()/60
            # =========================

            context = {
                "competitive_exam_obj":competitive_exam_obj,
                "paper_obj":paper_obj,
                "section_details":SECTION_DETAILS,
                "total_ques":TOTAL_QUES,
                "all_ques":ALL_QUES,
                "tot_time":TIME_IN_MIN,
            }
        else:
            # FIXME ALL_QUES and TOTAL_QUES
            ALL_QUES = questions
            TOTAL_QUES = len(questions)
            TOTAL_TIME =sum([ques.section_time_limit for ques in ALL_QUES],timedelta(0,0))
            TIME_IN_MIN = TOTAL_TIME.total_seconds()/60
            # =========================
            
            context = {
            "paper_obj":paper_obj,
            "section_details":SECTION_DETAILS,
            "paper_only":True,
            "total_ques":TOTAL_QUES,
            "all_ques":ALL_QUES,
            "tot_time":TIME_IN_MIN,

            }
        return render(request, "exam.html",context)


    def post(self, request, *args, **kwargs):
        class_id = request.GET.get("class")
        subject_id = request.GET.get("subject")
        competitive_exam_id = request.GET.get("competitive-exam")
        olympiad_id = request.GET.get("olympiad_id")
        paper_id = kwargs.get("id")
        paper_obj = get_object_or_404(Papers,id=paper_id)
        questions = paper_obj.assigned_questions.all()
        # if request.GET.get("obj_id"):
        #     student_payment = get_object_or_404(StudentPayments,id=request.GET.get("obj_id"))
        if request.POST.get("action") == "getQues":
            question_id = request.POST.get("quesId")
            question_obj = get_object_or_404(Questions,id=question_id)
            time_limit = question_obj.section_time_limit.total_seconds()
            to_return = {
                "question":question_obj.question,
                "option1":question_obj.option1,
                "option2":question_obj.option2,
                "option3":question_obj.option3,
                "option4":question_obj.option4,
                "time_limit":time_limit,
                "section_name":question_obj.section,
            }
            if question_obj.image:
                to_return["image"] = question_obj.image.url
            elif question_obj.image_link:
                to_return["image"] = question_obj.image_link

            return JsonResponse(to_return)
        
        if request.POST.get("action") == "finalSubmit":
            print("Entered3")
            DATA = request.POST.getlist("data[]")
            print(DATA)
            if competitive_exam_id:
                competitive_exam = CompetitiveExam.objects.get(id = competitive_exam_id)
                attend_paper_obj = AttendedPapers.objects.create(
                        student = request.user,
                        competitive_exam = competitive_exam,
                        paper = paper_obj,
                        correct_answers = 0,
                        attend_date = datetime.now().date(),
                    )
            elif class_id:
                attend_paper_obj = AttendedPapers.objects.create(
                        student = request.user,
                        class_obj = Classes.objects.get(id = class_id),
                        paper = paper_obj,
                        correct_answers = 0,
                        attend_date = datetime.now().date(),
                    )
            elif olympiad_id:
                olympiad_exam = OlympiadExam.objects.get(id = olympiad_id)
                attend_paper_obj = AttendedPapers.objects.create(
                    student = request.user,
                    paper = paper_obj,
                    olympiad_exam = olympiad_exam,
                    correct_answers = 0,
                    attend_date = datetime.now().date(),
                )
            else:
                attend_paper_obj = AttendedPapers.objects.create(
                        student = request.user,
                        paper = paper_obj,
                        correct_answers = 0,
                        attend_date = datetime.now().date(),
                    )
                # if request.GET.get("obj_id"):
                #     student_payment.is_attended = True
                #     student_payment.save()
            # if request.GET.get("obj_id"):
            #     student_payment.attended_papers.add(paper_obj)
            #     student_payment.save()
            for i in DATA:
                loaded_json = json.loads(i)
                print(loaded_json)
                paper = Papers.objects.get(id = paper_id)
                question_id = loaded_json.get("id") 
                question_obj = get_object_or_404(Questions,id=question_id)
                answer = loaded_json.get("ans")
                is_correct_ans = True if question_obj.correct_answer == answer else False
                submitted_time = loaded_json.get("submitted_time")
                time_delta = str_to_timedelta(str_time=submitted_time)

                obj = StudentSubmittedAnswers.objects.create(
                    student = request.user,
                    paper = paper,
                    question = question_obj,
                    submitted_answer = answer,
                    is_correct_answer = is_correct_ans,
                    answered_time = time_delta,
                )
                attend_paper_obj.attended_questions.add(obj)
                if is_correct_ans:
                    attend_paper_obj.correct_answers = attend_paper_obj.correct_answers+1
                    attend_paper_obj.save()
            
            # BUG: -> needs to mark it that the student is completed this paper.

            REDIRECT_URL = request.build_absolute_uri(reverse('application:enrolled_classes'))
            return JsonResponse({"redirect_url":REDIRECT_URL})
        return JsonResponse({})
    
class SchoolPage(View):
    def get(self, request, *args, **kwargs):
        classes_obj = Classes.objects.all().order_by("created_on")
        testimonials = Testimonials.objects.all()[:6]
        context = {
            "objs":classes_obj,
            "testimonials": testimonials
        }
        return render(request, "school.html", context)

    def post(self, request, *args, **kwargs):
        objId = request.POST.get("choosedClass")
        if objId != "popular":
            classes_obj = Classes.objects.get(id=objId)

            buyPaperWise = reverse("application:school_paper_wise")
            buyPaperWise = request.build_absolute_uri(f"{buyPaperWise}?class={objId}")
            buySubjectWise = reverse("application:school_subject_wise",kwargs={"pk":objId})
            buySubjectWise = request.build_absolute_uri(buySubjectWise)

            redirectUrl = reverse("application:checkout",kwargs={"id":objId})
            redirectUrl = request.build_absolute_uri(f"{redirectUrl}?type=class")

            toReturn = {
                "id":classes_obj.id,
                "title":classes_obj.title,
                "description":classes_obj.description,
                "subjects_count":classes_obj.assigned_subjects.count(),
                "buyPaperWise":buyPaperWise,
                "buySubjectWise":buySubjectWise,
                "buyClass":redirectUrl,
            }
        else:
            objs = Classes.objects.all().order_by("-purchase_count")
            data = serializers.serialize('json', objs, fields = ("id", "title", "description", "assigned_subjects", "price", "repay_price"))
            toReturn = {"data": data}
        return JsonResponse(toReturn)
    
class SchoolSubjectWise(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        choosed_class = Classes.objects.get(id = kwargs.get("pk"))
        testimonials = Testimonials.objects.all()[:6]
        context = {
            "class": choosed_class,
            "class_id":kwargs.get("pk"),
            "subjects":choosed_class.assigned_subjects.all(),
            "testimonials": testimonials,
        }
        return render(request,"subject.html",context)
    
    def post(self, request, *args, **kwargs):
        objId = request.POST.get("choosedClass")
        classes_obj = Subjects.objects.get(id=objId)

        buyPaperWise = reverse("application:school_paper_wise")
        buyPaperWise = request.build_absolute_uri(f"{buyPaperWise}?subject={objId}")

        redirectUrl = reverse("application:checkout",kwargs={"id":objId})
        redirectUrl = request.build_absolute_uri(f"{redirectUrl}?type=subject")

        toReturn = {
            "id":classes_obj.id,
            "title":classes_obj.title,
            "description":classes_obj.description,
            "price":classes_obj.price,
            "counts":classes_obj.assigned_papers.count(),
            "buyPaperWise":buyPaperWise,
            "buyClass":redirectUrl,
        }
        
        return JsonResponse(toReturn)

class SchoolPageWise(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        classId = request.GET.get("class")
        subjectId = request.GET.get("subject")
        competitive = request.GET.get("competitive")
        olympiad = request.GET.get("olympiad")
        testimonials = Testimonials.objects.all()[:6]

        if classId != None:
            choosed_class = get_object_or_404(Classes, id = classId)
            data = choosed_class.assigned_subjects.all()
            listOfQuerySet = []
            for d in data:
                listOfQuerySet.extend(d.assigned_papers.all())
            context = {
                "subject_id":subjectId,
                "papers":listOfQuerySet,
                "testimonials":testimonials,
                "title": choosed_class.title,
                "description": choosed_class.description,
            }

        if subjectId != None:
            choosed_subject = get_object_or_404(Subjects, id = subjectId)
            context = {
                "subject_id":subjectId,
                "papers":choosed_subject.assigned_papers.all(),
                "testimonials":testimonials,
                "title": choosed_subject.title,
                "description": choosed_subject.description
            }
        if competitive != None:
            choosed_subject = get_object_or_404(CompetitiveExam, id = competitive)
            
            context = {
                "subject_id":competitive,
                "papers":choosed_subject.assigned_papers.all(),
                "testimonials":testimonials,
                "title": choosed_subject.exam_name,
                "description": choosed_subject.description,
            }
        if olympiad != None:
            choosed_subject = get_object_or_404(OlympiadExam, id = olympiad)
            
            context = {
                "subject_id":competitive,
                "papers":choosed_subject.assigned_papers.all(),
                "testimonials":testimonials,
                "title": choosed_subject.exam_name,
                "description": choosed_subject.description,
            }

        return render(request,"paper.html",context)

    def post(self, request, *args, **kwargs):
        objId = request.POST.get("choosedClass")
        classes_obj = Papers.objects.get(id=objId)
        competitive = request.GET.get("competitive")

        if competitive == None:
            redirectUrl = reverse("application:checkout",kwargs={"id":objId})
            redirectUrl = request.build_absolute_uri(f"{redirectUrl}?type=paper")
        else:
            redirectUrl = reverse("application:checkout",kwargs={"id":objId})
            redirectUrl = request.build_absolute_uri(f"{redirectUrl}?type=competitive-paper")

        toReturn = {
            "id":classes_obj.id,
            "title":classes_obj.title,
            "description":classes_obj.description,
            "price":classes_obj.price,
            "buyClass":redirectUrl,
        }
        
        return JsonResponse(toReturn)
    
class Checkout(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        is_repay = False
        match request.GET.get("type"):
            case "class":
                obj = get_object_or_404(Classes,id=kwargs.get("id"))
                subjects = obj.assigned_subjects.all()
                papers_count = 0
                for i in subjects:
                    papers_count+=i.assigned_papers.all().count()
                if StudentPayments.objects.filter(student = request.user, classes = Classes.objects.get(id = kwargs.get("id"))).exists():
                    is_repay = True
            case "subject":
                obj = get_object_or_404(Subjects,id=kwargs.get("id"))
                papers_count = obj.assigned_papers.all().count()
                if StudentPayments.objects.filter(student = request.user, subjects = Subjects.objects.get(id = kwargs.get("id"))).exists():
                    is_repay = True
            case "paper":
                obj = get_object_or_404(Papers,id=kwargs.get("id"))
                papers_count = 0 
                if StudentPayments.objects.filter(student = request.user, papers = Papers.objects.get(id = kwargs.get("id"))).exists():
                    is_repay = True
            case "competitive-exam":
                obj = get_object_or_404(CompetitiveExam,id=kwargs.get("id"))
                papers_count = obj.assigned_papers.all().count()
                if StudentPayments.objects.filter(student = request.user, competitive_exam = CompetitiveExam.objects.get(id = kwargs.get("id"))).exists():
                    is_repay = True
            case "competitive-paper":
                obj = get_object_or_404(Papers,id=kwargs.get("id"))
                papers_count = 0 
                if StudentPayments.objects.filter(student = request.user, competitive_paper = Papers.objects.get(id = kwargs.get("id"))).exists():
                    is_repay = True
            case "olympiad-exam":
                obj = get_object_or_404(OlympiadExam,id=kwargs.get("id"))
                papers_count = 0
                if StudentPayments.objects.filter(student = request.user, olympiad_exam = OlympiadExam.objects.get(id = kwargs.get("id"))).exists():
                    is_repay = True
            case _:
                return redirect("application:index-page")
        print(is_repay)
        context = {
            "obj":obj,
            "papers_count":papers_count,
            "is_repay": is_repay
        }
        return render(request,"checkout.html",context)

class MakePayment(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        forWhat = request.GET.get("type")
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        match forWhat:
            case "class":
                obj = Classes.objects.get(id=kwargs.get("id"))
                if StudentPayments.objects.filter(student = request.user, classes = Classes.objects.get(id = kwargs.get("id"))).exists():
                    resp = client.order.create(
                        {"amount": float(obj.repay_price) * 100, "currency": "INR", "payment_capture": "1"}
                    )
                else:
                    resp = client.order.create(
                        {"amount": float(obj.price) * 100, "currency": "INR", "payment_capture": "1"}
                    )
            case "subject":
                obj = Subjects.objects.get(id=kwargs.get("id"))
                if StudentPayments.objects.filter(student = request.user, subjects = Subjects.objects.get(id = kwargs.get("id"))).exists():
                    resp = client.order.create(
                        {"amount": float(obj.repay_price) * 100, "currency": "INR", "payment_capture": "1"}
                    )
                else:
                    resp = client.order.create(
                        {"amount": float(obj.price) * 100, "currency": "INR", "payment_capture": "1"}
                    )
            case "paper":
                obj = Papers.objects.get(id=kwargs.get("id"))
                if StudentPayments.objects.filter(student = request.user, papers = Papers.objects.get(id = kwargs.get("id"))).exists():
                    resp = client.order.create(
                        {"amount": float(obj.repay_price) * 100, "currency": "INR", "payment_capture": "1"}
                    )
                else:
                    resp = client.order.create(
                        {"amount": float(obj.price) * 100, "currency": "INR", "payment_capture": "1"}
                    )
            case "competitive-exam":
                obj = CompetitiveExam.objects.get(id=kwargs.get("id"))
                if StudentPayments.objects.filter(student = request.user, competitive_exam = CompetitiveExam.objects.get(id = kwargs.get("id"))).exists():
                    resp = client.order.create(
                        {"amount": float(obj.repay_price) * 100, "currency": "INR", "payment_capture": "1"}
                    )
                else:
                    resp = client.order.create(
                        {"amount": float(obj.price) * 100, "currency": "INR", "payment_capture": "1"}
                    )
            case "competitive-paper":
                obj = Papers.objects.get(id=kwargs.get("id"))
                if StudentPayments.objects.filter(student = request.user, competitive_paper = Papers.objects.get(id = kwargs.get("id"))).exists():
                    resp = client.order.create(
                        {"amount": float(obj.repay_price) * 100, "currency": "INR", "payment_capture": "1"}
                    )
                else:
                    resp = client.order.create(
                        {"amount": float(obj.price) * 100, "currency": "INR", "payment_capture": "1"}
                    )
            case "olympiad-exam":
                obj = OlympiadExam.objects.get(id=kwargs.get("id"))
                resp = client.order.create(
                    {"amount": float(obj.paper.price) * 100, "currency": "INR", "payment_capture": "1"}
                )
            case _:
                return redirect("application:index-page")
            

        callBackUrl = reverse("callback",kwargs={"id":obj.id,"uid":request.user.id})
        callBackUrl = request.build_absolute_uri(f"{callBackUrl}?type={forWhat}")
        print(callBackUrl)
        con = {
            "callback_url":callBackUrl,
            "objId":obj.id,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "order_id": resp["id"],
            "price":resp["amount"]
            }
        return render(request,"payment.html",con)


@csrf_exempt
def callback(request,*args, **kwargs):
    ObjId = kwargs.get("id")
    fromWhere = request.GET.get("type")
    
    # fromWhere variable is used to find the obj that where its coming from.
    # if the payment is for class that it should add to classes field of StudentPayments model.

    user = CustomUser.objects.get(id=kwargs.get("uid"))

    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        b = client.utility.verify_payment_signature(response_data)
        return b
     
    # Success
    if "razorpay_signature" in request.POST:
        if verify_signature(request.POST):
            payment_id = request.POST.get("razorpay_payment_id")
            order_id = request.POST.get("razorpay_order_id")
            signature_id = request.POST.get("razorpay_signature")
            is_repay = False
            match fromWhere:
                case "class":
                    obj = Classes.objects.get(id=ObjId)
                    obj.purchase_count = obj.purchase_count+1
                    obj.save()
                    if StudentPayments.objects.filter(student = user, classes = obj).exists():
                        is_repay = True
                case "subject":
                    obj = Subjects.objects.get(id=ObjId)
                    if StudentPayments.objects.filter(student = user, subjects = obj).exists():
                        is_repay = True
                case "paper":
                    obj = Papers.objects.get(id=ObjId)
                    if StudentPayments.objects.filter(student = user, papers = obj).exists():
                        is_repay = True
                case "competitive-exam":
                    obj = CompetitiveExam.objects.get(id=ObjId)
                    obj.purchase_count = obj.purchase_count+1
                    obj.save()
                    if StudentPayments.objects.filter(student = user, competitive_exam = obj).exists():
                        is_repay = True
                case "competitive-paper":
                    obj = Papers.objects.get(id=ObjId)
                    if StudentPayments.objects.filter(student = user, competitive_paper = obj).exists():
                        is_repay = True
                case "olympiad-exam":
                    obj = OlympiadExam.objects.get(id=ObjId)
                    is_repay = False
                case _:
                    messages.error(request, "Payment Failure")
                    return redirect("application:index-page")
            if is_repay:
                price = obj.repay_price
                OBJ = StudentPayments.objects.create(
                    student = user,
                    order_id = order_id,
                    payment_id = payment_id,
                    signature_id = signature_id,
                    price = obj.repay_price,
                    enrolled_type=fromWhere, 
                    is_repay = is_repay
                )
            elif fromWhere != "olympiad-exam":
                price = obj.price
                OBJ = StudentPayments.objects.create(
                    student = user,
                    order_id = order_id,
                    payment_id = payment_id,
                    signature_id = signature_id,
                    price = obj.price,
                    enrolled_type=fromWhere, 
                    is_repay = is_repay
                )
            else:
                price = obj.paper.price
                OBJ = StudentPayments.objects.create(
                    student = user,
                    order_id = order_id,
                    payment_id = payment_id,
                    signature_id = signature_id,
                    price = price,
                    enrolled_type=fromWhere,
                    is_repay = is_repay,
                    olympiad_exam = obj
                )

            obj_title = ""
            match fromWhere:
                case "class":
                    OBJ.classes = obj
                case "subject":
                    OBJ.subjects = obj
                case "paper":
                    OBJ.papers = obj
                case "competitive-exam":
                    OBJ.competitive_exam = obj
                    obj_title = obj.exam_name
                case "competitive-paper":
                    OBJ.competitive_paper = obj
                case "olympiad-exam":
                    obj_title = obj.paper.title
            if obj_title == "":
                obj_title = obj.title
            
            OBJ.save()
            subject = f'Firststepedu payment success'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            print(recipient_list)
            plaintext = get_template('email_templates/payment_success.txt')
            htmly     = get_template('email_templates/payment_success.html')

            d = { 
                'obj_type': fromWhere,
                "title": obj_title,
                "amount": price,
            }

            text_content = plaintext.render(d)
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return redirect('application:enrolled_classes')
                
    #  payment error
    else:            
        # subject = f'Firststepedu payment failed'
        # email_from = settings.EMAIL_HOST_USER
        # recipient_list = [user.email]
        # print(recipient_list)
        # plaintext = get_template('email_templates/payment_failed.txt')
        # htmly     = get_template('email_templates/payment_failed.html')

        # d = { 

        # }

        # text_content = plaintext.render(d)
        # html_content = htmly.render(d)
        # msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
        # msg.attach_alternative(html_content, "text/html")
        # msg.send()
        redirectUrl = reverse("application:checkout",kwargs={"id":ObjId})
        redirectUrl = request.build_absolute_uri(f"{redirectUrl}?type={fromWhere}")
        messages.error(request, "Payment Failure")
        return redirect(redirectUrl)
    
@csrf_exempt
def eventcallback(request,*args, **kwargs):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        b = client.utility.verify_payment_signature(response_data)
        return b
     
    # Success
    if "razorpay_signature" in request.POST:
        if verify_signature(request.POST):
            event = Events.objects.get(id = kwargs["id"])
            student = CustomUser.objects.get(id=kwargs["uid"])
            RegisterdEvents.objects.create(student = student, event = event)
            return redirect('application:registered_events')
                
    #  payment error
    else:
        redirectUrl = reverse("application:index-page")
        redirectUrl = request.build_absolute_uri(f"{redirectUrl}")
        messages.error(request, "Payment Failure")
        return redirect(redirectUrl)

class ImportanceOfExam(TemplateView):
    template_name="importance_of_exam.html"

class TermsConditions(TemplateView):
    template_name="terms_conditions.html"