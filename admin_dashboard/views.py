from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail.message import EmailMessage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View

from application.models import *
from utils.constants import EmailContents
from utils.functions import OTP_Gen, is_ajax
from . import custom_mixins
from django.db import IntegrityError
from PIL import Image
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
            login(request, user)
            return redirect("admin_dashboard:admin-dashboard")
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

class AdminDashboard(custom_mixins.SuperUserCheck,View):
    def get(self,request,*args, **kwargs):
        return render(request,"admin_dashboard_base.html")


class BannerView(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        objs = HomeBanners.objects.all().order_by("created_on")
        context = {"objs":objs}
        return render(request,"banner-view.html",context)
    
    def post(self,request,*args, **kwargs):
        objs = HomeBanners.objects.get(id=request.POST.get("objId")).delete()
        to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
        return JsonResponse(to_return,safe=True,)


class AddBanner(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        return render(request,"banner-add.html")
    
    def post(self,request,*args, **kwargs):
        IMAGE_SCALE = (573,374)

        IMAGE = request.FILES.get("upload_image")
        imageImage = Image.open(IMAGE)
        scale = imageImage.size
        if IMAGE_SCALE == scale:
            obj = HomeBanners.objects.create(
            title = request.POST.get("title"),
            main_title = request.POST.get("main_title"),
            description = request.POST.get("description"),
            button_name = request.POST.get("button_name"),
            button_url = request.POST.get("button_url"),
            image = IMAGE,
            )
        else:
            messages.error(request,"Image scale is not acceptable")
            return redirect("admin_dashboard:home-banner-add")

        return redirect("admin_dashboard:home-banner")


class EditBanner(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        obj = get_object_or_404(HomeBanners,id=kwargs.get("id"))
        context = {"obj":obj}
        return render(request,"banner-edit.html",context)
    
    def post(self,request,*args, **kwargs):
        IMAGE_SCALE = (573,374)
        IMAGE = request.FILES.get("upload_image")
        if IMAGE != None:
            IMAGE = request.FILES.get("upload_image")
            imageImage = Image.open(IMAGE)
            scale = imageImage.size

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
        obj,created = MarqueeTexts.objects.get_or_create(id=1)
        context = {"obj":obj}
        return render(request,"marquee.html",context)

    def post(self,request,*args, **kwargs):
        obj,created = MarqueeTexts.objects.get_or_create(id=1)
        obj.text = request.POST.get("marquee_text")
        obj.save()
        return redirect("admin_dashboard:marquee")




class BlogsList(View):
    def get(self,request,*args, **kwargs):
        objs = Blogs.objects.all().order_by("created_on")
        context = {
            "objs":objs
        }
        return render(request,"blog-view.html",context)
    def post(self,request,*args, **kwargs):
        objs = Blogs.objects.get(id=request.POST.get("objId")).delete()
        to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
        return JsonResponse(to_return,safe=True,)

class AddBlog(View):
    def get(self,request,*args, **kwargs):
        return render(request,"blog-add.html")
    
    def post(self,request,*args, **kwargs):
        print(request.POST)
        try:
            obj = Blogs.objects.create(
                title = request.POST.get("title"),
                description = request.POST.get("description"),
                url = request.POST.get("url"),
                image = request.FILES.get("upload_image"),
                image_alt_name = request.POST.get("uploaded_image_alt_name"),
                overall_description = request.POST.get("overall_description"),
                meta_title = request.POST.get("meta_title"),
                meta_description = request.POST.get("meta_description"),
                meta_keywords = request.POST.get("meta_keywords"),
            )
            return redirect("admin_dashboard:blogs-list")
        except IntegrityError:
            messages.error(request, "URL must be unique")
            return redirect("admin_dashboard:blog-add")
        
        

class EditBlog(View):
    def get(self,request,*args, **kwargs):
        obj = get_object_or_404(Blogs,id=kwargs.get("id"))
        context = {"obj":obj}
        return render(request,"blog-edit.html",context)
    
    def post(self,request,*args, **kwargs):
        
        obj = get_object_or_404(Blogs,id=kwargs.get("id"))
        obj.title = request.POST.get("title",obj.title)
        obj.description = request.POST.get("description",obj.description)
        obj.url = request.POST.get("url",obj.url)
        obj.image = request.FILES.get("upload_image",obj.image)
        obj.image_alt_name = request.POST.get("uploaded_image_alt_name",obj.image_alt_name)
        obj.overall_description = request.POST.get("overall_description",obj.overall_description)
        obj.meta_title = request.POST.get("meta_title",obj.meta_title)
        obj.meta_description = request.POST.get("meta_description",obj.meta_description)
        obj.meta_keywords = request.POST.get("meta_keywords",obj.meta_keywords)
        obj.save()
        return redirect("admin_dashboard:blogs-list")



class ClassManagement(View):
    def get(self,request,*args, **kwargs):
        return render(request,"admin_dashboard_base.html")


class CompetitiveManagement(View):
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