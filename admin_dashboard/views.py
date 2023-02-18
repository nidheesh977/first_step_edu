from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail.message import EmailMessage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, UpdateView, View

from application.models import *
from utils.constants import EmailContents
from utils.functions import OTP_Gen, is_ajax


class AdminLogin(View):
    def get(self,request,*args, **kwargs):
        admin_email = request.POST.get("admin_email")
        admin_password = request.POST.get("admin_password")
        user = authenticate(request, username=admin_email, password=admin_password)
        if user is not None:
            pass

        return render(request,"login.html")
    
    def post(self,request,*args, **kwargs):
        admin_email = request.POST.get("admin_email")
        admin_password = request.POST.get("admin_password")
        user = authenticate(request, username=admin_email, password=admin_password)
        if user is not None and user.is_superuser:
            return redirect("admin_dashboard:dashboard")
        else:
            messages.error(request,"Invalid Credentials")
            return redirect("admin_dashboard:admin-login")


class AdminForgetPassword(View):
    def get(self,request, *args, **kwargs):
        return render(request, "admin-forgot-password.html")
    
    def post(self,request, *args, **kwargs):
        if is_ajax(request):
            if request.POST.get("action") == "sendOtp":
                email = request.POST.get("emailId")
                is_exists = CustomUser.objects.filter(email=email, is_superuser=True).exists()
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
                        "title":"Entered email is not an admin account",
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
                    return redirect("admin_dashboard:admin-login")
                else:
                    messages.error(request,"Invalid OTP")
            else:
                messages.warning(request,"OTP is not generated for submitted email please click send OTP")
            return redirect("admin_dashboard:admin-forget-password")

class AdminDashboard(View):
    def get(self,request,*args, **kwargs):
        return render(request,"admin_dashboard_base.html")



class BannerView(View):
    def get(self,request,*args, **kwargs):
        objs = HomeBanners.objects.all().order_by("created_on")
        context = {"objs":objs}
        return render(request,"banner-view.html",context)


class AddBanner(View):
    def get(self,request,*args, **kwargs):
        return render(request,"banner-add.html")
    
    def post(self,request,*args, **kwargs):
        obj = HomeBanners.objects.create(
            title = request.POST.get("title"),
            main_title = request.POST.get("main_title"),
            description = request.POST.get("description"),
            button_name = request.POST.get("button_name"),
            button_url = request.POST.get("button_url"),
            image = request.FILES.get("upload_image"),
        )
        return redirect("admin_dashboard:home-banner")


class EditBanner(View):
    def get(self,request,*args, **kwargs):
        obj = get_object_or_404(HomeBanners,id=kwargs.get("id"))
        context = {"obj":obj}
        return render(request,"banner-edit.html",context)
    
    def post(self,request,*args, **kwargs):
        obj = get_object_or_404(HomeBanners,id=kwargs.get("id"))
        obj.title = request.POST.get("title",obj.title)
        obj.main_title = request.POST.get("main_title",obj.main_title)
        obj.description = request.POST.get("description",obj.description)
        obj.button_name = request.POST.get("button_name",obj.button_name)
        obj.button_url = request.POST.get("button_url",obj.button_url)
        obj.image = request.FILES.get("upload_image",obj.image)
        obj.save()
        return redirect("admin_dashboard:home-banner")

class MarqueeText(View):
    def get(self,request,*args, **kwargs):
        return render(request,"admin_dashboard_base.html")



class ClassManagement(View):
    def get(self,request,*args, **kwargs):
        return render(request,"admin_dashboard_base.html")


class CompetitiveManagement(View):
    def get(self,request,*args, **kwargs):
        return render(request,"admin_dashboard_base.html")


class Blog(View):
    def get(self,request,*args, **kwargs):
        return render(request,"admin_dashboard_base.html")


class Events(View):
    def get(self,request,*args, **kwargs):
        return render(request,"admin_dashboard_base.html")


class News(View):
    def get(self,request,*args, **kwargs):
        return render(request,"admin_dashboard_base.html")


class Testimonials(View):
    def get(self,request,*args, **kwargs):
        return render(request,"admin_dashboard_base.html")
    
class ResultAnnouncement(View):
    def get(self,request,*args, **kwargs):
        return render(request,"admin_dashboard_base.html")


class ContactEnquiry(View):
    def get(self,request,*args, **kwargs):
        data = ContactUs.objects.all().order_by("created_on")
        context = {
            "objs":data,
        }
        return render(request,"contact-enquiry.html", context)


class RegistredUsers(View):
    def get(self,request,*args, **kwargs):
        return render(request,"admin_dashboard_base.html")