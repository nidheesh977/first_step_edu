
import json
from datetime import datetime

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
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, TemplateView, View

from utils.constants import EmailContents, TextConstants
from utils.functions import OTP_Gen, is_ajax, str_to_timedelta

from .models import *


class SignUpView(View):
    def get(self,request, *args, **kwargs):
        return render(request, "sign-up.html")
    
    def post(self,request, *args, **kwargs):
        is_agreed = request.POST.get("flexCheckDefault2")
        if is_agreed == "agreed":
            user_obj = CustomUser.objects.create(
                first_name = request.POST.get("first_name"),
                last_name = request.POST.get("last_name"),
                email = request.POST.get("email"),
                mobile_number = request.POST.get("mobile_number"),
                parent_name = request.POST.get("parent_name"),
                class_name = request.POST.get("class"),
                school_name = request.POST.get("school_name"),
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
                    # FIXME -> send OTP
                    generated_otp = OTP_Gen()
                    send_email = EmailMessage(
                        EmailContents.forget_password_title,
                        EmailContents.forget_password_subject.format(generated_otp),
                        to=[email]
                    )
                    send_email.send(fail_silently=True)
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
        obj.city = request.POST.get("city",obj.city)
        obj.school_name = request.POST.get("school_name",obj.school_name)
        obj.class_name = request.POST.get("class_name",obj.class_name)
        obj.save()
        return redirect("application:account-dashboard")

class IndexView(View):
    def get(self,request, *args, **kwargs):
        bannerObj = HomeBanners.objects.all()
        classesObj = Classes.objects.all()[:6]
        competitiveExamObj = CompetitiveExam.objects.all()[:6]
        results = ResultAnnouncements.objects.all()[:6]
        news=News.objects.all()[:6]
        blogs = Blogs.objects.all().order_by("created_on")[:3]
        testimonials = Testimonials.objects.all()[:6]
        events = Events.objects.all()[:3]
        context = {
            "bannerObj":bannerObj,
            "classesObj":classesObj,
            "competitiveExamObj":competitiveExamObj,
            "resultsObj":results,
            "news":news,
            "blogs":blogs,
            "testimonials":testimonials,
            "events":events,
           
        }
        return render(request, "index.html",context)

class AboutUs(TemplateView):
    template_name="about-us.html"

class WhyChooseUs(TemplateView):
    template_name="why-choose-us.html"


class OurTeam(TemplateView):
    template_name="our-team.html"


class BlogsList(ListView):
    template_name = "blog.html"
    model = Blogs
    paginate_by = 6
    ordering = "created_on"

    def get_context_data(self,**kwargs):
        env = environ.Env()
        blog_url = env.get_value("blog_url")
        context = super(BlogsList,self).get_context_data(**kwargs)
        context["blog_url"] = blog_url
        return context

    def post(self, request, *args, **kwargs):
        blog_count = request.POST.get("blogCount")
        start_num = int(blog_count)+1
        end_num = start_num + self.paginate_by
        list_exam = Blogs.objects.all().order_by("created_on").defer("id","title","image","description","url","image_alt_name")
        objs = list_exam[start_num:end_num]
        data = serializers.serialize('json', objs, fields=("id","title","image","description","url","image_alt_name"))
        res = {"data":data, "media_url":settings.MEDIA_URL}
        return JsonResponse(res)

class BlogView(View):
    def get(self, request, *args, **kwargs):
        blogsObj = Blogs.objects.all()[:6]
        context = {
            "objs":blogsObj,
        }
        return render(request,"blog.html",context)

    def post(self, request,*arg, **kwargs):
        return render(request,"blog.html")
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


class Announcement(TemplateView):
    template_name="announcement.html"


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
        obj = CompetitiveExam.objects.all()
        context = {
            "objs":obj
        }
        return render(request, "competitive.html",context)
    
    def post(self, request, *args, **kwargs):
        objId = request.POST.get("choosedClass")
        classes_obj = CompetitiveExam.objects.get(id=objId)

        buyPaperWise = reverse("application:school_paper_wise")
        buyPaperWise = request.build_absolute_uri(f"{buyPaperWise}?competitive={objId}")
       
        # FIXME -> CHECKOUT
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
        
        return JsonResponse(toReturn)



class EventsPage(ListView):
    template_name = "events.html"
    model = Events
    paginate_by = 3
    ordering = "created_on"

    def get_registeredEvents(self):
        try:
            registerdEvents = RegisterdEvents.objects.get(student__id = self.request.user.id)
            events = registerdEvents.event.all()
            return events

        except ObjectDoesNotExist as e:
            events = []
            return events

    def get_context_data(self,**kwargs):
        context = super(EventsPage,self).get_context_data(**kwargs)
        context["registered_events"] = self.get_registeredEvents()
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get("action") == "register":
            eventId = request.POST.get("eventId")
            evnt = Events.objects.get(id=eventId)
            obj,created = RegisterdEvents.objects.get_or_create(student = request.user)
            obj.event.add(evnt)
            res = {"msg":"Event Registered"}
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
    

class RegisterdEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            registerdEvents = RegisterdEvents.objects.get(student = self.request.user)
            events = registerdEvents.event.all()
        except ObjectDoesNotExist as e:
            events = []
        finally:
            context = {
                "events":events,
            }
            return render(request,"dash-events.html", context)


class EnrolledClassesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        board_exams = StudentPayments.objects.filter(student=request.user)
        context = {
            "board_exams":board_exams.exclude(enrolled_type__in=["competitive-exam","competitive-paper"]),
            "competitive_exams":board_exams.exclude(enrolled_type__in=["class","subject","paper"])
        }
        return render(request,"enrolled.html",context)
    


class EnrolledSubjectsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        obj = StudentPayments.objects.get(id=kwargs.get("id"))
        context = {
            "obj":obj
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
                    previous_el = previous_dict["questions_count"]
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
            context = {
            "competitive_exam_obj":competitive_exam_obj,
            "paper_obj":paper_obj,
            "section_details":SECTION_DETAILS,
            "total_ques":TOTAL_QUES,
            "all_ques":ALL_QUES,
            "tot_time":TIME_IN_MIN,

            }
        else:
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
        paper_id = kwargs.get("id")
        paper_obj = get_object_or_404(Papers,id=paper_id)

        if request.POST.get("action") == "getQues":
            question_id = request.POST.get("quesId")
            question_obj = get_object_or_404(Questions,id=question_id)
            time_limit = question_obj.section_time_limit.total_seconds()/60
            to_return = {
                "question":question_obj.question,
                "option1":question_obj.option1,
                "option2":question_obj.option2,
                "option3":question_obj.option3,
                "option4":question_obj.option4,
                "time_limit":time_limit,
                "section_name":question_obj.section,
            }
            return JsonResponse(to_return)
        
        if request.POST.get("action") == "submit_ques":

            question_id = request.POST.get("quesId")
            question_obj = get_object_or_404(Questions,id=question_id)
            answer = request.POST.get("ans")
            is_correct_ans = True if question_obj.correct_answer == answer else False
            submitted_time = request.POST.get("clicked_time")
            time_delta = str_to_timedelta(str_time=submitted_time)
            
            obj = StudentSubmittedAnswers.objects.create(
                student = request.user,
                question = question_obj,
                submitted_answer = answer,
                is_correct_answer = is_correct_ans,
                answered_time = time_delta,
            )

        return JsonResponse({})
    
class SchoolPage(View):
    def get(self, request, *args, **kwargs):
        classes_obj = Classes.objects.all().order_by("created_on")
        context = {
            "objs":classes_obj
        }
        return render(request, "school.html", context)

    def post(self, request, *args, **kwargs):
        objId = request.POST.get("choosedClass")
        classes_obj = Classes.objects.get(id=objId)

        buyPaperWise = reverse("application:school_paper_wise")
        buyPaperWise = request.build_absolute_uri(f"{buyPaperWise}?class={objId}")
        buySubjectWise = reverse("application:school_subject_wise",kwargs={"pk":objId})
        buySubjectWise = request.build_absolute_uri(buySubjectWise)

        # FIXME -> CHECKOUT
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
        
        return JsonResponse(toReturn)
class SchoolSubjectWise(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        choosed_class = Classes.objects.get(id = kwargs.get("pk"))
        context = {
            "subjects":choosed_class.assigned_subjects.all(),
        }
        return render(request,"subject.html",context)
    
    def post(self, request, *args, **kwargs):
        objId = request.POST.get("choosedClass")
        classes_obj = Subjects.objects.get(id=objId)

        buyPaperWise = reverse("application:school_paper_wise")
        buyPaperWise = request.build_absolute_uri(f"{buyPaperWise}?subject={objId}")
        
        # FIXME -> CHECKOUT
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

        if classId != None:
            choosed_class = get_object_or_404(Classes, id = classId)
            data = choosed_class.assigned_subjects.all()
            listOfQuerySet = []
            for d in data:
                listOfQuerySet.extend(d.assigned_papers.all())
            context = {
                "papers":listOfQuerySet,
            }
        
        if subjectId != None:
            choosed_subject = get_object_or_404(Subjects, id = subjectId)
            context = {
                "papers":choosed_subject.assigned_papers.all(),
            }
        if competitive != None:
            choosed_subject = get_object_or_404(CompetitiveExam, id = competitive)
            context = {
                "papers":choosed_subject.assigned_papers.all(),
            }
        
        return render(request,"paper.html",context)
    
    def post(self, request, *args, **kwargs):
        objId = request.POST.get("choosedClass")
        classes_obj = Papers.objects.get(id=objId)
        competitive = request.GET.get("competitive")
        
        # FIXME -> CHECKOUT
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
        
        match request.GET.get("type"):
            case "class":
                obj = get_object_or_404(Classes,id=kwargs.get("id"))
                subjects = obj.assigned_subjects.all()
                papers_count = 0
                for i in subjects:
                    papers_count+=i.assigned_papers.all().count()
            case "subject":
                obj = get_object_or_404(Subjects,id=kwargs.get("id"))
                papers_count = obj.assigned_papers.all().count()
            case "paper":
                obj = get_object_or_404(Papers,id=kwargs.get("id"))
                papers_count = 0 
            case "competitive-exam":
                obj = get_object_or_404(CompetitiveExam,id=kwargs.get("id"))
                papers_count = obj.assigned_papers.all().count()
            case "competitive-paper":
                obj = get_object_or_404(Papers,id=kwargs.get("id"))
                papers_count = 0 
            case _:
                return redirect("application:index-page")
                
        context = {
            "obj":obj,
            "papers_count":papers_count,
        }
        return render(request,"checkout.html",context)





class MakePayment(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        forWhat = request.GET.get("type")
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        match forWhat:
            case "class":
                obj = Classes.objects.get(id=kwargs.get("id"))
                resp = client.order.create(
                    {"amount": float(obj.price) * 100, "currency": "INR", "payment_capture": "1"}
                )
            case "subject":
                obj = Subjects.objects.get(id=kwargs.get("id"))
                resp = client.order.create(
                    {"amount": float(obj.price) * 100, "currency": "INR", "payment_capture": "1"}
                )
            case "paper":
                obj = Papers.objects.get(id=kwargs.get("id"))
                resp = client.order.create(
                    {"amount": float(obj.price) * 100, "currency": "INR", "payment_capture": "1"}
                )
            case "competitive-exam":
                obj = CompetitiveExam.objects.get(id=kwargs.get("id"))
                resp = client.order.create(
                    {"amount": float(obj.price) * 100, "currency": "INR", "payment_capture": "1"}
                )
            case "competitive-paper":
                obj = Papers.objects.get(id=kwargs.get("id"))
                resp = client.order.create(
                    {"amount": float(obj.price) * 100, "currency": "INR", "payment_capture": "1"}
                )
            case _:
                return redirect("application:index-page")
            

        callBackUrl = reverse("callback",kwargs={"id":obj.id,"uid":request.user.id})
        callBackUrl = request.build_absolute_uri(f"{callBackUrl}?type={forWhat}")
        
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

            match fromWhere:
                case "class":
                    obj = Classes.objects.get(id=ObjId)
                case "subject":
                    obj = Subjects.objects.get(id=ObjId)
                case "paper":
                    obj = Papers.objects.get(id=ObjId)
                case "competitive-exam":
                    obj = CompetitiveExam.objects.get(id=ObjId)
                case "competitive-paper":
                    obj = Papers.objects.get(id=ObjId)
                case _:
                    messages.error(request, "Payment Failure")
                    return redirect("application:index-page")
            
            OBJ = StudentPayments.objects.create(
                student = user,
                order_id = order_id,
                payment_id = payment_id,
                signature_id = signature_id,
                price = obj.price,
                enrolled_type=fromWhere, 
            )
            match fromWhere:
                case "class":
                    OBJ.classes = obj
                case "subject":
                    OBJ.subjects = obj
                case "paper":
                    OBJ.papers = obj
                case "competitive-exam":
                    OBJ.competitive_exam = obj
                case "competitive-paper":
                    OBJ.competitive_paper = obj
            
            OBJ.save()
            return redirect('application:enrolled_classes')
                
    #  payment error
    else:            
        redirectUrl = reverse("application:checkout",kwargs={"id":ObjId})
        redirectUrl = request.build_absolute_uri(f"{redirectUrl}?type={fromWhere}")
        messages.error(request, "Payment Failure")
        return redirect(redirectUrl)
     
