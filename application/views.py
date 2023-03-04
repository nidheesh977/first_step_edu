
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail.message import EmailMessage

from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView, TemplateView, View

from utils.constants import EmailContents, TextConstants
from utils.functions import OTP_Gen, is_ajax
from django.core import serializers
from .models import *
from django.conf import settings
import environ
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
        print(user_type)
        logout(request)
        if user_type:
            return redirect("admin_dashboard:admin-login")
        else:
            return redirect("application:index-page")

class AccountDashboard(View):
    def get(self,request, *args, **kwargs):
        return render(request, "account.html")

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
        return render(request, "competitive.html")

class SchoolPage(View):
    def get(self, request, *args, **kwargs):
        return render(request, "school.html")
    
class PapersView(ListView):
    def get(self,request, *args,**kwargs):
        choosed_class = Classes.objects.get(id = kwargs.get("id"))
        context = {
            "obj":choosed_class
        }
        return render(request,"paper.html", context )