import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail.message import EmailMessage
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from PIL import Image
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template

from application.models import *
from utils.constants import EmailContents, ImageSizes
from utils.functions import OTP_Gen, is_ajax, reterive_request_data
import pandas as pd
from django.core.exceptions import BadRequest


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

class AdminChangePassword(View):
    def get(self,request, *args, **kwargs):
        return render(request, "admin_change_password.html")
    
    def post(self,request, *args, **kwargs):
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        
        if new_password == confirm_password:
            is_valid_oldPassword=request.user.check_password(old_password)
            if is_valid_oldPassword:
                request.user.set_password(confirm_password)
                request.user.save()
                logout(request)
                messages.success(request,"password has been changed")
                return redirect("admin_dashboard:admin-login")
            else:
                messages.error(request,"Old password is not correct")
                return redirect("admin_dashboard:admin_change_password")
        else:
            messages.error(request,"password not matched")
            return redirect("admin_dashboard:admin_change_password")

class AdminDashboard(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        registerdUsers = CustomUser.objects.all().exclude(is_superuser=True)
        blogs = Blogs.objects.all().count()
        events = Events.objects.all().count()
        enquiry = ContactUs.objects.all().count()
        
        context = {
            "user_counts":registerdUsers.count(),
            "blogs_counts":blogs,
            "events_counts":events,
            "enquiry_counts":enquiry,
            "user_objs":registerdUsers,
        }
        return render(request,"admin_dashboard_base.html",context)

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
        context = {
            "image_size":ImageSizes.homepage_img_size_str,
        }
        return render(request,"banner-add.html",context)
    
    def post(self,request,*args, **kwargs):
        IMAGE_SCALE = ImageSizes.homepage_img_size
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
        context = {"obj":obj,"image_size":ImageSizes.homepage_img_size_str,}
        return render(request,"banner-edit.html",context)
    
    def post(self,request,*args, **kwargs):
        IMAGE_SCALE = ImageSizes.homepage_img_size
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
        Blogs.objects.get(id=request.POST.get("objId")).delete()
        to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
        return JsonResponse(to_return,safe=True,)

class AddBlog(View):
    def get(self,request,*args, **kwargs):
        context = {"img_size":ImageSizes.blog_img_size_str}
        return render(request,"blog-add.html",context)
    
    def post(self,request,*args, **kwargs):
        IMAGE_SCALE =ImageSizes.blog_img_size
        try:
            
            IMAGE = request.FILES.get("upload_image")
            imageImage = Image.open(IMAGE)
            scale = imageImage.size

            if IMAGE_SCALE == scale:
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
            else:
                messages.error(request,"Image scale is not acceptable")
                return redirect("admin_dashboard:blog-add")
        except IntegrityError:
            messages.error(request, "URL must be unique")
            return redirect("admin_dashboard:blog-add")
        
class EditBlog(View):
    def get(self,request,*args, **kwargs):
        obj = get_object_or_404(Blogs,id=kwargs.get("id"))
        context = {"obj":obj,"img_size":ImageSizes.blog_img_size_str}
        return render(request,"blog-edit.html",context)
    
    def post(self,request,*args, **kwargs):
        IMAGE_SCALE =ImageSizes.blog_img_size
        try:
            obj = get_object_or_404(Blogs,id=kwargs.get("id"))
            
            obj.title = request.POST.get("title",obj.title)
            obj.description = request.POST.get("description",obj.description)
            obj.url = request.POST.get("url",obj.url)
            obj.image_alt_name = request.POST.get("uploaded_image_alt_name",obj.image_alt_name)
            obj.overall_description = request.POST.get("overall_description",obj.overall_description)
            obj.meta_title = request.POST.get("meta_title",obj.meta_title)
            obj.meta_description = request.POST.get("meta_description",obj.meta_description)
            obj.meta_keywords = request.POST.get("meta_keywords",obj.meta_keywords)

            IMAGE = request.FILES.get("upload_image")
            if IMAGE != None:
                imageImage = Image.open(IMAGE)
                scale = imageImage.size
                if IMAGE_SCALE == scale:
                    obj.image = request.FILES.get("upload_image",obj.image)
                    obj.save()
                    return redirect("admin_dashboard:blogs-list")
                else:
                    messages.error(request,"Image scale is not acceptable")
                    return redirect("admin_dashboard:blog-edit", id=kwargs.get("id"))
            else:
                obj.save()
                return redirect("admin_dashboard:blogs-list")
        except IntegrityError:
            messages.error(request, "URL must be unique")
            return redirect("admin_dashboard:blog-edit", id=kwargs.get("id"))

class EventsList(View):
    def get(self,request,*args, **kwargs):
        objs = Events.objects.all().order_by("created_on")
        context = {"objs":objs}
        return render(request,"event-view.html",context)
    
    def post(self,request,*args, **kwargs):
        method = request.POST.get("method")
        id = request.POST.get("objId")
        event = Events.objects.get(id=id)
        if method == "delete":
            event.delete()
            to_return = {
                            "title":"Deleted",
                            "icon":"success",
                        }
        else:
            registered_events = RegisterdEvents.objects.filter(event = event)
            recipient_list = []
            for i in registered_events:
                recipient_list.append(i.student.email)
            print(recipient_list)
            if len(recipient_list) >= 1:
                subject = f'Event alert'
                email_from = settings.EMAIL_HOST_USER
                plaintext = get_template('email_templates/event_notification.txt')
                htmly     = get_template('email_templates/event_notification.html')

                d = {
                    'title': event.title,
                    'date': event.event_date,
                }

                text_content = plaintext.render(d)
                html_content = htmly.render(d)
                msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
                msg.attach_alternative(html_content, "text/html")
                msg.send()

            to_return = {
                            "title":"Notification send successfully",
                            "icon":"success",
                        }
        return JsonResponse(to_return,safe=True,)
    
class EditDetails(View):
    def get(self, request, *args, **kwargs):
        objs = RegisterdEvents.objects.filter(event = Events.objects.get(id = kwargs["id"]))
        context = {"objs":objs}
        return render(request,"event-detail.html",context)

class AddEvent(View):
    def get(self,request,*args, **kwargs):
        context = {"img_size":ImageSizes.events_img_size_str}
        return render(request,"event-add.html",context)
    
    def post(self,request,*args, **kwargs):
        IMAGE_SCALE = ImageSizes.events_img_size
        IMAGE = request.FILES.get("upload_image")
        imageImage = Image.open(IMAGE)
        scale = imageImage.size
        if IMAGE_SCALE == scale:
            obj = Events.objects.create(
                title = request.POST.get("title"),
                label = request.POST.get("label"),
                event_date = request.POST.get("event_date"),
                event_meeting_link = request.POST.get("meeting_link"),
                image = request.FILES.get("upload_image"),
                image_alt_name = request.POST.get("upload_image_alt_name"),
                event_fee = request.POST.get("event_fee"),
            )
            return redirect("admin_dashboard:events-list")
        else:
            messages.error(request,"Image scale is not acceptable")
            return redirect("admin_dashboard:event-add")

class EditEvent(View):
    def get(self,request,*args, **kwargs):
        obj = get_object_or_404(Events,id=kwargs.get("id"))
        context = {"obj":obj, "img_size":ImageSizes.events_img_size_str}
        return render(request,"event-edit.html", context)
        
    def post(self,request,*args, **kwargs):
        obj = get_object_or_404(Events,id=kwargs.get("id"))
        obj.title = request.POST.get("title",obj.title)
        obj.label = request.POST.get("label",obj.label)
        obj.event_date = request.POST.get("event_date",obj.event_date)
        obj.event_meeting_link = request.POST.get("event_meeting_link",obj.event_meeting_link)
        obj.image_alt_name = request.POST.get("image_alt_name",obj.image_alt_name)


        IMAGE_SCALE = ImageSizes.events_img_size
        IMAGE = request.FILES.get("upload_image")
    
        if IMAGE != None:
            imageImage = Image.open(IMAGE)
            scale = imageImage.size
            if IMAGE_SCALE == scale:
                obj.image = request.FILES.get("upload_image",obj.image)
                obj.save()
                return redirect("admin_dashboard:events-list")
            else:
                messages.error(request,"Image scale is not acceptable")
                return redirect("admin_dashboard:event-edit",id=kwargs.get("id"))
        else:
            obj.save()
            return redirect("admin_dashboard:events-list")

class NewsList(View):
    def get(self,request,*args, **kwargs):
        objs = News.objects.all().order_by("created_on")
        context = {"objs":objs,"img_size":ImageSizes.news_img_size_img_size_str}
        return render(request,"news-view.html",context)
    
    def post(self,request,*args, **kwargs):
        News.objects.get(id=request.POST.get("objId")).delete()
        to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
        return JsonResponse(to_return,safe=True,)
    
class AddNews(View):
    def get(self,request,*args, **kwargs):
        context = {"img_size":ImageSizes.news_img_size_img_size_str}
        return render(request,"news-add.html",context)
    
    def post(self,request,*args, **kwargs):
        IMAGE_SCALE = ImageSizes.news_img_size
        IMAGE = request.FILES.get("upload_image")
        if IMAGE != None:
            imageImage = Image.open(IMAGE)
            scale = imageImage.size
            if IMAGE_SCALE == scale:
                News.objects.create(
                    event_date = request.POST.get("event_date"),
                    image = request.FILES.get("upload_image"),
                    image_alt_name = request.POST.get("upload_image_alt_name"),
                    description = request.POST.get("description"),
                )
                return redirect("admin_dashboard:news-list")
            else:
                messages.error(request,"Image scale is not acceptable")
                return redirect("admin_dashboard:news-add")
        else:
            News.objects.create(
                    event_date = request.POST.get("event_date"),
                    image_alt_name = request.POST.get("upload_image_alt_name"),
                    description = request.POST.get("description"),
                )
            return redirect("admin_dashboard:news-list")

class EditNews(View):
    def get(self,request,*args, **kwargs):
        obj = get_object_or_404(News,id=kwargs.get("id"))
        context = {"obj":obj,"img_size":ImageSizes.news_img_size_img_size_str}
        return render(request,"news-edit.html",context)
    
    def post(self,request,*args, **kwargs):
        obj = get_object_or_404(News,id=kwargs.get("id"))
        obj.event_date = request.POST.get("event_date",obj.event_date)
        
        obj.image_alt_name = request.POST.get("upload_image_alt_name",obj.image_alt_name)
        obj.description = request.POST.get("description",obj.description)
        
        IMAGE_SCALE = ImageSizes.news_img_size
        IMAGE = request.FILES.get("upload_image")
        
        if IMAGE != None:
            imageImage = Image.open(IMAGE)
            scale = imageImage.size
            if IMAGE_SCALE == scale:
                obj.image = request.FILES.get("upload_image",obj.image)
                obj.save()
                return redirect("admin_dashboard:news-list")
            else:
               messages.error(request,"Image scale is not acceptable") 
               return redirect("admin_dashboard:news-edit",id=kwargs.get("id"))
        else:
            obj.save()
            return redirect("admin_dashboard:news-list")


class TestimonialsList(View):
    def get(self,request,*args, **kwargs):
        objs = Testimonials.objects.all().order_by("created_on")
        context = {"objs":objs}
        return render(request,"testimonials-view.html",context)
    
    def post(self,request,*args, **kwargs):
        Testimonials.objects.get(id=request.POST.get("objId")).delete()
        to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
        return JsonResponse(to_return,safe=True,)
    
class AddTestimonial(View):
    def get(self,request,*args, **kwargs):
        context = {"img_size":ImageSizes.testimonials_img_size_str}
        return render(request,"testimonials-add.html",context)
    
    def post(self,request,*args, **kwargs):
        IMAGE_SCALE = ImageSizes.testimonials_img_size
        IMAGE = request.FILES.get("upload_image")
        imageImage = Image.open(IMAGE)
        scale = imageImage.size
        if scale == IMAGE_SCALE:
            Testimonials.objects.create(
                client_name = request.POST.get("client_name"),
                client_role = request.POST.get("client_role"),
                image = request.FILES.get("upload_image"),
                image_alt_name = request.POST.get("upload_image_alt_name"),
                description = request.POST.get("description"),
                assigned_pages = request.POST.getlist("assigned_pages"),
            )
            return redirect("admin_dashboard:testimonials-list")
        else:
            messages.error(request,"Image scale is not acceptable")
            return redirect("admin_dashboard:testimonial-add")

class EditTestimonial(View):
    def get(self,request,*args, **kwargs):
        obj = get_object_or_404(Testimonials,id=kwargs.get("id"))
        context = {"obj":obj,"img_size":ImageSizes.testimonials_img_size_str}
        return render(request,"testimonials-edit.html",context)
    
    def post(self,request,*args, **kwargs):
        obj = get_object_or_404(Testimonials,id=kwargs.get("id"))        
        obj.client_name = request.POST.get("client_name",obj.client_name)
        obj.client_role = request.POST.get("client_role",obj.client_role)
        
        obj.image_alt_name = request.POST.get("upload_image_alt_name",obj.image_alt_name)
        obj.description = request.POST.get("description",obj.description)
        obj.assigned_pages = request.POST.getlist("assigned_pages",obj.assigned_pages)

        IMAGE_SCALE = ImageSizes.testimonials_img_size
        IMAGE = request.FILES.get("upload_image")
        if IMAGE != None:
            imageImage = Image.open(IMAGE)
            scale = imageImage.size
            if IMAGE_SCALE == scale:
                obj.image = request.FILES.get("upload_image",obj.image)
                obj.save()
                return redirect("admin_dashboard:testimonials-list")
            else:
                messages.error(request,"Image scale is not acceptable")
                return redirect("admin_dashboard:testimonial-edit",id=kwargs.get("id"))
        else:
            obj.save()
            return redirect("admin_dashboard:testimonials-list")


class ResultAnnouncementsList(View):
    def get(self,request,*args, **kwargs):
        objs = ResultAnnouncements.objects.all().order_by("created_on")
        context = {"objs":objs}
        return render(request,"announce-view.html",context)
    
    def post(self,request,*args, **kwargs):
        ResultAnnouncements.objects.get(id=request.POST.get("objId")).delete()
        to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
        return JsonResponse(to_return,safe=True,)


class AddResultAnnouncement(View):
    def get(self,request,*args, **kwargs):
        context = {
            "img_size":ImageSizes.result_announce_img_size_str
        }
        return render(request,"announce-add.html", context)
    
    def post(self,request,*args, **kwargs):
        IMAGE_SCALE =ImageSizes.result_announce_img_size
        IMAGE = request.FILES.get("upload_image")
        imageImage = Image.open(IMAGE)
        scale = imageImage.size
        if scale == IMAGE_SCALE:
            ResultAnnouncements.objects.create(
                title = request.POST.get("title"),
                winner_name = request.POST.get("winner_name"),
                winner_mark = request.POST.get("winner_mark"),
                winner_image = request.FILES.get("upload_image"),
                winner_image_alt_name = request.POST.get("uploaded_image_alt_name"),
                winner_description = request.POST.get("description"),
            )
            return redirect("admin_dashboard:result_announcements-list")
        else:
            messages.error(request,"Image scale is not acceptable")
            return redirect("admin_dashboard:result_announcement-add")

class EditResultAnnouncement(View):
    def get(self,request,*args, **kwargs):
        obj = get_object_or_404(ResultAnnouncements,id=kwargs.get("id"))
        context = {
            "obj":obj,
            "img_size":ImageSizes.result_announce_img_size_str
        }
        return render(request,"announce-edit.html",context)
    
    def post(self,request,*args, **kwargs):
        obj = get_object_or_404(ResultAnnouncements,id=kwargs.get("id"))        
        
        obj.title = request.POST.get("title",obj.title)
        obj.winner_name = request.POST.get("winner_name",obj.winner_name)
        obj.winner_mark = int(request.POST.get("winner_mark",obj.winner_mark))
        
        obj.winner_image_alt_name = request.POST.get("uploaded_image_alt_name",obj.winner_image_alt_name)
        obj.winner_description = request.POST.get("description",obj.winner_description)
        
        obj.save()
        IMAGE_SCALE = (80,80)
        IMAGE = request.FILES.get("upload_image")

        if IMAGE != None:
            imageImage = Image.open(IMAGE)
            scale = imageImage.size
            if IMAGE_SCALE == scale:
                obj.winner_image = request.FILES.get("upload_image",obj.winner_image)
                obj.save()
                return redirect("admin_dashboard:result_announcements-list")
            else:
                messages.error(request,"Image scale is not acceptable")
                return redirect("admin_dashboard:result_announcement-edit",id=kwargs.get("id"))
        else:
            obj.save()
            return redirect("admin_dashboard:result_announcements-list")


class ContactEnquiry(View):
    def get(self,request,*args, **kwargs):
        data = ContactUs.objects.all().order_by("created_on")
        context = {
            "objs":data,
        }
        return render(request,"contact-enquiry.html", context)

class RegistredUsers(View):
    def get(self,request,*args, **kwargs):
        objs = CustomUser.objects.all().exclude(is_superuser=True).order_by("created_on")
        context = {"objs":objs}
        return render(request,"registration.html",context)


# CM - Class Management
class CMClassListView(View):
    def get(self,request,*args, **kwargs):
        objs = Classes.objects.all()
        context = {
            "objs":objs,
        }
        return render(request,"class_management/classes/class-list.html",context)
    
    def post(self,request,*args, **kwargs):
        if request.POST.get("action") == "delete":
            Classes.objects.get(id=request.POST.get("objId")).delete()
            to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
            return JsonResponse(to_return,safe=True,)
        if request.POST.get("action") == "retrieve":
            obj = Classes.objects.filter(id=request.POST.get("objId")).values(
                "id",
                "title",
                "price",
                "repay_price",
                "description",
                "meta_title",
                "meta_description",
                "meta_keywords",
            )
            to_return = {"obj":list(obj)[0]}
            return JsonResponse(to_return,safe=True,)

        if request.POST.get("edit_form") != None:
            obj = get_object_or_404(Classes,id=request.POST.get("id"))       
            obj.title = request.POST.get("class_title",obj.title)
            obj.description = request.POST.get("class_description",obj.description)
            obj.meta_title = request.POST.get("meta_title",obj.meta_title)
            obj.meta_description = request.POST.get("meta_description",obj.meta_description)
            obj.meta_keywords = request.POST.get("meta_keywords",obj.meta_keywords)
            obj.price = request.POST.get("price",obj.price)
            obj.repay_price = request.POST.get("repay_price",obj.repay_price)
            obj.save()
            return redirect("admin_dashboard:clsm-classes-list")
        else:
            Classes.objects.create(
                title = request.POST.get("class_title"),
                description = request.POST.get("class_description"),
                price = request.POST.get("price"),
                repay_price = request.POST.get("repay_price"),
                meta_title = request.POST.get("meta_title"),
                meta_description = request.POST.get("meta_description"),
                meta_keywords = request.POST.get("meta_keywords"), 
            )
        return redirect("admin_dashboard:clsm-classes-list")


class CMSubjectsListView(View):
    def get(self,request,*args, **kwargs):
        cls_obj = get_object_or_404(Classes,id=kwargs.get("class_id")) 
        context = {
            "cls_id":kwargs.get("class_id"),
            "subjects":cls_obj.assigned_subjects.all()
        }
        return render(request,"class_management/subjects/subjects-list.html",context)
    

    def post(self,request,*args, **kwargs):
        cls_obj = get_object_or_404(Classes,id=kwargs.get("class_id")) 
        if request.POST.get("action") == "delete":
            obj = get_object_or_404(Subjects,id=request.POST.get("objId")) 
            obj.delete()
            to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
            return JsonResponse(to_return,safe=True,)
        if request.POST.get("action") == "retrieve":
            obj = Subjects.objects.filter(id=request.POST.get("objId")).values(
                "id",
                "title",
                "description",
                "price",
                "repay_price",
                "meta_title",
                "meta_description",
                "meta_keywords",
            )
            to_return = {"obj":list(obj)[0]}
            return JsonResponse(to_return,safe=True,)

        if request.POST.get("edit_form") != None:
            obj = get_object_or_404(Subjects,id=request.POST.get("id"))       
            obj.title = request.POST.get("subject_title",obj.title)
            obj.description = request.POST.get("subject_description",obj.description)
            obj.price = request.POST.get("price",obj.price)
            obj.repay_price = request.POST.get("repay_price",obj.repay_price)
            obj.meta_title = request.POST.get("meta_title",obj.meta_title)
            obj.meta_description = request.POST.get("meta_description",obj.meta_description)
            obj.meta_keywords = request.POST.get("meta_keywords",obj.meta_keywords)
            obj.save()
            return redirect("admin_dashboard:clsm-subjects-list",class_id=cls_obj.id)
        else:
            sub_obj = Subjects.objects.create(
                title = request.POST.get("subject_title"),
                description = request.POST.get("subject_description"),
                price = request.POST.get("price"),
                repay_price = request.POST.get("repay_price"),
                meta_title = request.POST.get("meta_title"),
                meta_description = request.POST.get("meta_description"),
                meta_keywords = request.POST.get("meta_keywords"),
            )
            cls_obj.assigned_subjects.add(sub_obj)
            return redirect("admin_dashboard:clsm-subjects-list",class_id=cls_obj.id)


class CMPapersListView(View):
    def get(self,request,*args, **kwargs):
        SUBJECT_ID = kwargs.get("subject_id")
        CLASS_ID = kwargs.get("class_id")
        sub_obj = get_object_or_404(Subjects,id=SUBJECT_ID)
        objs = sub_obj.assigned_papers.filter(is_competitive=False).order_by("created_on")
        context = {
            "cls_id":CLASS_ID,
            "sub_id":SUBJECT_ID,
            "objs":objs,
        }
        return render(request,"class_management/papers/papers-list.html",context)


    def post(self,request,*args, **kwargs):
        SUBJECT_ID = kwargs.get("subject_id")
        CLASS_ID = kwargs.get("class_id")
        sub_obj = get_object_or_404(Subjects,id=SUBJECT_ID)

        if request.POST.get("action") == "delete":
            obj = get_object_or_404(Papers,id=request.POST.get("objId")) 
            obj.delete()
            to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
            return JsonResponse(to_return,safe=True,)
        if request.POST.get("action") == "retrieve":
            obj = Papers.objects.filter(id=request.POST.get("objId")).values(
                "id",
                "title",
                "price",
                "description",
                "instructions",
                "section_details"
            ).order_by("created_on ")
            to_return = {"obj":list(obj)[0]}
            return JsonResponse(to_return,safe=True,)

        if request.POST.get("edit_form") != None:
            obj = get_object_or_404(Papers,id=request.POST.get("id"))
            obj.title = request.POST.get("paper_title",obj.title)
            obj.description = request.POST.get("paper_description",obj.description)
            obj.instructions = request.POST.get("general_instructions",obj.instructions)
            obj.price = request.POST.get("price",obj.price)
            obj.save()
            return redirect("admin_dashboard:clsm-papers-list",class_id=CLASS_ID,subject_id=SUBJECT_ID)
        else:
            section_name = request.POST.getlist("section_name")
            section_description = request.POST.getlist("section_description")
            final_list = []

            for i in range(0, len(section_name)):
                d = {
                    "name":section_name[i],
                    "description":section_description[i]
                }
                final_list.append(json.dumps(d))

            paper_obj = Papers.objects.create(
                title = request.POST.get("paper_title"),
                description = request.POST.get("paper_description"),
                instructions = request.POST.get("general_instructions"),
                price = request.POST.get("price"),
                section_details=final_list,
            )
            sub_obj.assigned_papers.add(paper_obj)
            return redirect("admin_dashboard:clsm-papers-list",class_id=CLASS_ID,subject_id=SUBJECT_ID)

class CMQuestionsList(View):
    def get(self,request,*args, **kwargs):
        PAPER_ID = kwargs.get("paper_id")
        CLASS_ID = kwargs.get("class_id")
        SUBJECT_ID = kwargs.get("subject_id")
        paper_obj = get_object_or_404(Papers,id=PAPER_ID)
        temp_images = TempImages.objects.filter(paper = paper_obj)

        if CLASS_ID and SUBJECT_ID:
            context = {
                "qus_obj":paper_obj.assigned_questions.all().order_by("created_on"),
                "cls_id":CLASS_ID,
                "sub_id":SUBJECT_ID,
                "paper_id":PAPER_ID,
                "temp_images": temp_images
            }
            return render(request,"class_management/papers/questions-list.html",context)
        else:
            context = {
                'exm_id':kwargs.get("exm_id"),
                "paper_id":PAPER_ID,
                "qus_obj":paper_obj.assigned_questions.all(),
                "temp_images": temp_images
            }
            return render(request,"competitive_management/competitve_qus_list.html",context)

    def post(self,request,*args, **kwargs):
        get_object_or_404(Questions,id=request.POST.get("objId")).delete()
        to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
        return JsonResponse(to_return,safe=True,)

class CMAddPaper(View):
    def get(self,request,*args, **kwargs):

        return render(request,"class_management/papers/add_paper.html")

    def post(self, request, *args, **kwargs):
        SUBJECT_ID = kwargs.get("subject_id")
        CLASS_ID = kwargs.get("class_id")
        section_name = request.POST.getlist("section_name")
        section_description = request.POST.getlist("section_description")
        final_list = []
        SUBJECT_OBJ = Subjects.objects.get(id=SUBJECT_ID)
        for i in range(0, len(section_name)):
            d = {
                "name":section_name[i],
                "description":section_description[i]
            }
            final_list.append(json.dumps(d))

        paper_obj = Papers.objects.create(
            title = request.POST.get("paper_title"),
            description = request.POST.get("paper_description"),
            instructions = request.POST.get("general_instructions"),
            price = request.POST.get("price"),
            section_details=final_list,
        )
        SUBJECT_OBJ.assigned_papers.add(paper_obj)
        return redirect("admin_dashboard:clsm-papers-list",class_id=CLASS_ID,subject_id=SUBJECT_ID)

class CMEditPaper(View):
    def get(self,request,*args, **kwargs):
        paper_id = kwargs.get("id")
        paper_obj = Papers.objects.get(id = paper_id)
        if paper_obj.section_details:
            SECTION_DETAILS = [json.loads(i) for i in paper_obj.section_details]
        else:
            SECTION_DETAILS = []
        context = {
            "obj":paper_obj,
            "section_details":SECTION_DETAILS,
        }
        return render(request,"class_management/papers/edit_paper.html", context)

    def post(self, request, *args, **kwargs):
        SUBJECT_ID = kwargs.get("subject_id")
        CLASS_ID = kwargs.get("class_id")
        paper_id = kwargs.get("id")
        paper_obj = Papers.objects.get(id=paper_id)
        section_name = request.POST.getlist("section_name")
        section_description = request.POST.getlist("section_description",paper_obj.section_details)
        final_list = []
        for i in range(0, len(section_name)):
            d = {
                "name":section_name[i],
                "description":section_description[i]
            }
            final_list.append(json.dumps(d))
        paper_obj.title = request.POST.get("paper_title",paper_obj.title)
        paper_obj.description = request.POST.get("paper_description",paper_obj.description)
        paper_obj.instructions = request.POST.get("general_instructions",paper_obj.instructions)
        paper_obj.price = request.POST.get("price",paper_obj.price)
        paper_obj.repay_price = request.POST.get("repay_price",paper_obj.repay_price)
        paper_obj.section_details=final_list
        paper_obj.save()

        return redirect("admin_dashboard:clsm-papers-list",class_id=CLASS_ID,subject_id=SUBJECT_ID)

class CMAddQuestions(View):
    def get(self,request,*args, **kwargs):

        PAPER_ID = kwargs.get("paper_id")
        CLASS_ID = kwargs.get("class_id")
        SUBJECT_ID = kwargs.get("subject_id")
        paper_obj = get_object_or_404(Papers,id=PAPER_ID)
        if paper_obj.section_details:
            SECTION_DETAILS = [json.loads(i) for i in paper_obj.section_details]
        else:
            SECTION_DETAILS = []
        if CLASS_ID and SUBJECT_ID:
            context = {
                "cls_id":CLASS_ID,
                "sub_id":SUBJECT_ID,
                "paper_id":PAPER_ID,
                "paper_obj":paper_obj,
                "section_details":SECTION_DETAILS,
            }
            return render(request,"class_management/papers/questions-add.html",context)
        else:
            context = {
                'exm_id':kwargs.get("exm_id"),
                "paper_id":PAPER_ID,
                "paper_obj":paper_obj,
                "section_details":SECTION_DETAILS,
            }
            return render(request,"competitive_management/competitive_qus_add.html",context)

    def post(self,request,*args, **kwargs):
        PAPER_ID = kwargs.get("paper_id")
        CLASS_ID = kwargs.get("class_id")
        SUBJECT_ID = kwargs.get("subject_id")
        time_limit = str(request.POST.get("section_time_limit")).split(":")
        SECONDS = int(time_limit[1])
        MINUTES = int(time_limit[0])
        if all([SECONDS<=60,MINUTES<=60]):
            section_time_limit = timedelta(seconds=SECONDS, minutes=MINUTES)
            qus_obj = Questions.objects.create(
            section = request.POST.get("section"),
            section_description = request.POST.get("section_description"),
            section_time_limit = section_time_limit,
            question = request.POST.get("question"),
            option1 = request.POST.get("option1"),
            option2 = request.POST.get("option2"),
            option3 = request.POST.get("option3"),
            option4 = request.POST.get("option4"),
            correct_answer = request.POST.get("correct_option")
            )
            if request.FILES.get("upload_image"):
                qus_obj.image = request.FILES.get("upload_image")
                qus_obj.save()
            paper_obj = get_object_or_404(Papers,id=PAPER_ID)
            paper_obj.assigned_questions.add(qus_obj)

            if CLASS_ID and SUBJECT_ID:
                return redirect("admin_dashboard:clsm-questions-list", class_id=CLASS_ID, subject_id=SUBJECT_ID, paper_id=PAPER_ID)
            else:
                Exam_ID = kwargs.get("exm_id")
                return redirect("admin_dashboard:comp_ques_list", exm_id = Exam_ID, paper_id=PAPER_ID)

        else:
            messages.error(request, "Invalid Time duration format")
            da = reterive_request_data(request.POST)
            
            if CLASS_ID and SUBJECT_ID:
                rr = reverse('admin_dashboard:clsm-paper-qus-add',kwargs={"class_id":CLASS_ID, "subject_id":SUBJECT_ID, "paper_id":PAPER_ID})+da
                return HttpResponseRedirect(redirect_to=rr)
            else:
                rr = reverse("admin_dashboard:comp_ques_add", kwargs={"paper_id":PAPER_ID})+da
                return HttpResponseRedirect(redirect_to=rr)


class CMEditQuestions(View):
    def get(self,request,*args, **kwargs):
        PAPER_ID = kwargs.get("paper_id")
        CLASS_ID = kwargs.get("class_id")
        SUBJECT_ID = kwargs.get("subject_id")
        qus_obj = get_object_or_404(Questions,id=kwargs.get("qus_id"))
        seconds = qus_obj.section_time_limit
        paper_obj = get_object_or_404(Papers,id=PAPER_ID)
        if paper_obj.section_details:
            SECTION_DETAILS = [json.loads(i) for i in paper_obj.section_details]
        else:
            SECTION_DETAILS = []
        if seconds != None:
            convert = str(timedelta(seconds = seconds.total_seconds()))
            OUTCOME = convert.split(":")
            TIME_LIMIT= f"{OUTCOME[1]}:{OUTCOME[2]}"
        else:
            TIME_LIMIT = None
        
        if CLASS_ID and SUBJECT_ID:
            context = {
                "cls_id":CLASS_ID,
                "sub_id":SUBJECT_ID,
                "paper_id":PAPER_ID,
                "obj":qus_obj,
                "time_limit":TIME_LIMIT,
                "section_details":SECTION_DETAILS,
            }
            return render(request,"class_management/papers/questions-edit.html",context)
        else:
            Exam_ID = kwargs.get("exm_id")
            context = {
                "paper_id":PAPER_ID,
                "obj":qus_obj,
                "time_limit":TIME_LIMIT,
                "section_details":SECTION_DETAILS,
                "exm_id": Exam_ID
            }
            return render(request,"competitive_management/competitve_qus_edit.html",context)

    def post(self,request,*args, **kwargs):
        PAPER_ID = kwargs.get("paper_id")
        CLASS_ID = kwargs.get("class_id")
        SUBJECT_ID = kwargs.get("subject_id")
        Exam_ID = kwargs.get("exm_id")
        qus_obj = get_object_or_404(Questions,id=kwargs.get("qus_id"))
        time_limit = str(request.POST.get("section_time_limit")).split(":")
        section_time_limit = timedelta(seconds=int(time_limit[1]), minutes=int(time_limit[0]))

        SECONDS = int(time_limit[1])
        MINUTES = int(time_limit[0])
        if all([SECONDS<=60,MINUTES<=60]):
            qus_obj.section = request.POST.get("section",qus_obj.section)
            qus_obj.section_description = request.POST.get("section_description",qus_obj.section_description)
            qus_obj.section_time_limit = section_time_limit if section_time_limit else qus_obj.section_time_limit
            qus_obj.question = request.POST.get("question",qus_obj.question)
            qus_obj.option1 = request.POST.get("option1",qus_obj.option1)
            qus_obj.option2 = request.POST.get("option2",qus_obj.option2)
            qus_obj.option3 = request.POST.get("option3",qus_obj.option3)
            qus_obj.option4 = request.POST.get("option4",qus_obj.option4)
            qus_obj.correct_answer = request.POST.get("correct_option",qus_obj.correct_answer)
            if request.FILES.get("upload_image"):
                qus_obj.image = request.FILES.get("upload_image")
            qus_obj.save()

            if CLASS_ID and SUBJECT_ID:
                return redirect("admin_dashboard:clsm-questions-list", class_id=CLASS_ID, subject_id=SUBJECT_ID, paper_id=PAPER_ID)
            else:
                return redirect("admin_dashboard:comp_ques_list", exm_id = Exam_ID, paper_id=PAPER_ID)
        else:
            messages.error(request, "Invalid Time duration format")
            if CLASS_ID and SUBJECT_ID:
                return redirect("admin_dashboard:clsm-paper-qus-edit", class_id=CLASS_ID, subject_id=SUBJECT_ID, paper_id=PAPER_ID, qus_id =kwargs.get("qus_id"))
            else:
                return redirect("admin_dashboard:comp_ques_edit", paper_id=PAPER_ID, qus_id =kwargs.get("qus_id"))


class CompetitiveManagementAddPaper(View):
    def get(self,request,*args, **kwargs):
        return render(request,"competitive_management/comp_add_paper.html")

    def post(self, request, *args, **kwargs):
        EXAM_ID = kwargs.get("exm_id")
        section_name = request.POST.getlist("section_name")
        section_description = request.POST.getlist("section_description")
        final_list = []
        SUBJECT_OBJ = CompetitiveExam.objects.get(id=EXAM_ID)
        for i in range(0, len(section_name)):
            d = {
                "name":section_name[i],
                "description":section_description[i]
            }
            final_list.append(json.dumps(d))

        paper_obj = Papers.objects.create(
            title = request.POST.get("paper_title"),
            description = request.POST.get("paper_description"),
            instructions = request.POST.get("general_instructions"),
            price = request.POST.get("price"),
            section_details=final_list,
        )
        SUBJECT_OBJ.assigned_papers.add(paper_obj)
        return redirect("admin_dashboard:competitve_papers_list",exm_id=EXAM_ID)


class CompetitiveManagementEditPaper(View):

    def get(self,request,*args, **kwargs):
        EXAM_ID = kwargs.get("exm_id")
        paper_id = kwargs.get("id")
        paper_obj = Papers.objects.get(id = paper_id)
        if paper_obj.section_details:
            SECTION_DETAILS = [json.loads(i) for i in paper_obj.section_details]
        else:
            SECTION_DETAILS = []
        context = {
            "exm_id":EXAM_ID,
            "obj":paper_obj,
            "section_details":SECTION_DETAILS,
        }
        return render(request,"competitive_management/comp_edit_paper.html", context)

    def post(self, request, *args, **kwargs):
        EXAM_ID = kwargs.get("exm_id")
        paper_id = kwargs.get("id")
        paper_obj = Papers.objects.get(id=paper_id)
        section_name = request.POST.getlist("section_name")
        section_description = request.POST.getlist("section_description",paper_obj.section_details)
        final_list = []
        for i in range(0, len(section_name)):
            d = {
                "name":section_name[i],
                "description":section_description[i]
            }
            final_list.append(json.dumps(d))
        paper_obj.title = request.POST.get("paper_title",paper_obj.title)
        paper_obj.description = request.POST.get("paper_description",paper_obj.description)
        paper_obj.instructions = request.POST.get("general_instructions",paper_obj.instructions)
        paper_obj.price = request.POST.get("price",paper_obj.price)
        paper_obj.repay_price = request.POST.get("repay_price",paper_obj.repay_price)
        paper_obj.section_details=final_list
        paper_obj.save()
        
        return redirect("admin_dashboard:competitve_papers_list",exm_id=EXAM_ID)

class CompetitiveManagementPapersList(View):
    def get(self,request,*args, **kwargs):
        com_obj = get_object_or_404(CompetitiveExam,id=kwargs.get("exm_id"))
        objs = com_obj.assigned_papers.all()
        context = {
            "objs":objs,
            "exm_id":kwargs.get("exm_id"),
        }
        return render(request,"competitive_management/competitive_papers_list.html",context)

    def post(self,request, *args, **kwargs):
        if request.POST.get("action") == "delete":
            obj = get_object_or_404(Papers,id=request.POST.get("objId")) 
            obj.delete()
            to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
            return JsonResponse(to_return,safe=True,)
        
        if request.POST.get("action") == "retrieve":
            obj = Papers.objects.filter(id=request.POST.get("objId")).values(
                "id",
                "title",
                "price",
                "description",
                "instructions"
            )
            to_return = {"obj":list(obj)[0]}
            return JsonResponse(to_return,safe=True,)
        
        if request.POST.get("edit_form") != None:
            obj = get_object_or_404(Papers,id=request.POST.get("id"))       
            obj.title = request.POST.get("paper_title",obj.title)
            obj.description = request.POST.get("paper_description",obj.description)
            obj.instructions = request.POST.get("general_instructions",obj.instructions)
            obj.price = request.POST.get("price",obj.price)
            obj.save()
            return redirect("admin_dashboard:competitve_papers_list",exm_id=kwargs.get("exm_id"))
    
        else:
            com_obj = get_object_or_404(CompetitiveExam,id=kwargs.get("exm_id"))
            paper_obj = Papers.objects.create(
                title = request.POST.get("paper_title"),
                description = request.POST.get("paper_description"),
                instructions = request.POST.get("general_instructions"),
                price = request.POST.get("price"),
                is_competitive=True,
            )
            com_obj.assigned_papers.add(paper_obj)
            return redirect("admin_dashboard:competitve_papers_list",exm_id=kwargs.get("exm_id"))


class CompetitiveExamsList(View):
    def get(self, request,*args, **kwargs):
        objs = CompetitiveExam.objects.all()
        context = {
            "objs":objs,
        }
        return render(request,"competitive_management/competitve_exams_list.html",context)

    def post(self,request, *args, **kwargs):
        if request.POST.get("action") == "delete":
            obj = get_object_or_404(CompetitiveExam,id=request.POST.get("objId"))
            obj.delete()
            to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
            return JsonResponse(to_return,safe=True,)

        if request.POST.get("action") == "retrieve":
            obj = CompetitiveExam.objects.filter(id=request.POST.get("objId")).values(
                "id",
                "exam_name",
                "description",
                "price",
                "repay_price"
            )
            to_return = {"obj":list(obj)[0]}
            return JsonResponse(to_return,safe=True,)

        if request.POST.get("edit_form") != None:
            obj = get_object_or_404(CompetitiveExam,id=request.POST.get("id"))
            obj.exam_name = request.POST.get("exam_title",obj.exam_name)
            obj.description = request.POST.get("exam_description",obj.description)
            obj.price = request.POST.get("exam_price",obj.price)
            obj.repay_price = request.POST.get("repay_price",obj.repay_price)
            obj.save()
            return redirect("admin_dashboard:competitve_exams_list")
        else:
            CompetitiveExam.objects.create(
                exam_name = request.POST.get("exam_title"),
                description = request.POST.get("exam_description"),
                price = request.POST.get("exam_price"),
                repay_price = request.POST.get("repay_price"), )
            return redirect("admin_dashboard:competitve_exams_list")

class CMBulkQuestions(View):
    def post(self, request, *args, **kwargs):
        try:
            PAPER_ID = kwargs.get("paper_id")
            paper_obj = get_object_or_404(Papers,id=PAPER_ID)
            to_dict = paper_obj.section_details
            df = pd.read_csv (request.FILES["file"])
            for i in df.iterrows():
                if str(i[1].question) != "nan":
                    time_limit = i[1].time_dutation.split(":")
                    SECONDS = int(time_limit[1])
                    MINUTES = int(time_limit[0])
                    section_time_limit = timedelta(seconds=SECONDS, minutes=MINUTES)
                    qus_obj = Questions.objects.create(
                        section_description = "",
                        section_time_limit = section_time_limit,
                        question = i[1].question,
                        option1 = i[1].optionA,
                        option2 = i[1].optionB,
                        option3 = i[1].optionC,
                        option4 = i[1].optionD,
                        correct_answer = i[1][i[1].answer],
                    )
                    if "image" in i[1] and str(i[1].image) != "nan":
                        print(str(i[1].image))
                        qus_obj.image_link = i[1].image
                        qus_obj.save()
                    if "section" in i[1] and str(i[1].section) != "nan":
                        qus_obj.section = i[1].section,
                        qus_obj.save()
                    paper_obj = get_object_or_404(Papers,id=PAPER_ID)
                    paper_obj.assigned_questions.add(qus_obj)
                    paper_obj.save()

            to_return = {"status": "Success"}
            return JsonResponse(to_return,safe=True)
        except:
            raise BadRequest('Invalid file.')

class CMBulkImageGenerateLink(View):
    def post(self, request, *args, **kwargs):
        try:
            PAPER_ID = kwargs.get("paper_id")
            paper = Papers.objects.get(id = PAPER_ID)
            image = request.FILES["file"]
            img_obj = TempImages.objects.create(paper = paper, image = image)
            print(image)
            to_return = {"link": img_obj.image.url}
            return JsonResponse(to_return,safe=True)
        except:
            raise BadRequest('Invalid files.')
        
class PaymentDetails(View):
    def get(self, request):
        payments = StudentPayments.objects.all()
        return render(request, "payment_details.html", context = {"payments": payments})
        
class UserPaymentDetails(View):
    def get(self, request, *args, **kwargs):
        payments = StudentPayments.objects.filter(student = CustomUser.objects.get(id =kwargs["id"]))
        return render(request, "user_payment_details.html", context = {"payments": payments})
    
# Olympiad

class OlympiadManagementAddExam(View):
    def get(self,request,*args, **kwargs):
        return render(request,"olympiad_management/olymp_add_exam.html")
    
    def post(self, request, *args, **kwargs):
        print(args)
        print(kwargs)
        print(request.POST)
        section_name = request.POST.getlist("section_name")
        section_description = request.POST.getlist("section_description")
        final_list = []
        for i in range(0, len(section_name)):
            d = {
                "name":section_name[i],
                "description":section_description[i]
            }
            final_list.append(json.dumps(d))
        paper_obj = Papers.objects.create(
            title = request.POST.get("paper_title"),
            description = request.POST.get("paper_description"),
            instructions = request.POST.get("general_instructions"),
            price = request.POST.get("price"),
            is_competitive=False,
            section_details = final_list
        )
        olymp_obj = OlympiadExam.objects.create(
            exam_date = request.POST.get("exam_date"),
            exam_time = request.POST.get("exam_time"),
            paper = paper_obj
        )
        return redirect("admin_dashboard:olympiad_exams_list")

class OlympiadManagementAddQuestion(View):
    def get(self,request,*args, **kwargs):
        olymp_id = kwargs["id"]
        return render(request,"olympiad_management/olymp_add_ques.html", context = {"olymp_id": olymp_id})
    
    def post(self,request,*args, **kwargs):
        olympiad_obj = OlympiadExam.objects.get(id = kwargs.get("id"))
        time_limit = str(request.POST.get("section_time_limit")).split(":")
        SECONDS = int(time_limit[1])
        MINUTES = int(time_limit[0])
        if all([SECONDS<=60,MINUTES<=60]):
            section_time_limit = timedelta(seconds=SECONDS, minutes=MINUTES)
            qus_obj = Questions.objects.create(
            section = request.POST.get("section"),
            section_description = request.POST.get("section_description"),
            section_time_limit = section_time_limit,
            question = request.POST.get("question"),
            option1 = request.POST.get("option1"),
            option2 = request.POST.get("option2"),
            option3 = request.POST.get("option3"),
            option4 = request.POST.get("option4"),
            correct_answer = request.POST.get("correct_option")
            )
            if request.FILES.get("upload_image"):
                qus_obj.image = request.FILES.get("upload_image")
                qus_obj.save()
            paper_obj = olympiad_obj.paper
            paper_obj.assigned_questions.add(qus_obj)
        return redirect("admin_dashboard:olympiad_ques_list", id = kwargs["id"])

class OlympiadManagementEditExam(View):
    def get(self,request,*args, **kwargs):
        olympiad = OlympiadExam.objects.get(id = kwargs.get("id"))
        paper_obj = olympiad.paper
        print(paper_obj.section_details)
        if paper_obj.section_details:
            SECTION_DETAILS = [json.loads(i) for i in paper_obj.section_details]
        else:
            SECTION_DETAILS = []
        return render(request,"olympiad_management/olymp_edit_exam.html", context = {"olympiad": olympiad, "section_details":SECTION_DETAILS})
    def post(self, request, *args, **kwargs):
        print(args)
        print(kwargs)
        print(request.POST)
        olympiad = OlympiadExam.objects.get(id = kwargs.get("id"))
        paper_obj = olympiad.paper
        paper_obj.title = request.POST.get("paper_title")
        paper_obj.description = request.POST.get("paper_description")
        paper_obj.instructions = request.POST.get("general_instructions")
        paper_obj.price = request.POST.get("price")
        paper_obj.is_competitive=False
        olympiad.exam_date = request.POST.get("exam_date")
        olympiad.exam_time = request.POST.get("exam_time")
        paper_obj.save()
        olympiad.save()
        return redirect("admin_dashboard:olympiad_exams_list")

class OlympiadManagementQuestionList(View):
    def get(self,request,*args, **kwargs):
        olympiad = OlympiadExam.objects.get(id = kwargs.get("id"))
        paper = olympiad.paper
        questions = paper.assigned_questions.all()
        return render(request,"olympiad_management/olymp_ques_list.html", context = {"qus_obj": questions, "olymp_id": olympiad.id})

    def post(self,request, *args, **kwargs):
        if request.POST.get("action") == "delete":
            print(request.POST.get("objId"))
            obj = Questions.objects.get(id=request.POST.get("objId"))
            obj.delete()
            to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
            return JsonResponse(to_return,safe=True,)
        
class OlympiadManagementEditQuestion(View):
    def get(self, request, *args, **kwargs):
        olympiad = OlympiadExam.objects.get(id = kwargs["olymp_id"])
        question = Questions.objects.get(id = kwargs["ques_id"])
        paper_obj = olympiad.paper
        seconds = question.section_time_limit
        print(question.section)
        if seconds != None:
            convert = str(timedelta(seconds = seconds.total_seconds()))
            OUTCOME = convert.split(":")
            TIME_LIMIT= f"{OUTCOME[1]}:{OUTCOME[2]}"
        else:
            TIME_LIMIT = None
        return render(request, "olympiad_management/olymp_edit_ques.html", context = {"olymp_id": olympiad.id, "obj": question, "time_limit":TIME_LIMIT,})
    
    def post(self,request,*args, **kwargs):
        olympiad_obj = OlympiadExam.objects.get(id = kwargs.get("olymp_id"))
        time_limit = str(request.POST.get("section_time_limit")).split(":")
        SECONDS = int(time_limit[1])
        MINUTES = int(time_limit[0])
        if all([SECONDS<=60,MINUTES<=60]):
            section_time_limit = timedelta(seconds=SECONDS, minutes=MINUTES)
            qus_obj = Questions.objects.get(id = kwargs["ques_id"])
            qus_obj.section = request.POST.get("section",qus_obj.section)
            qus_obj.section_description = request.POST.get("section_description",qus_obj.section_description)
            qus_obj.section_time_limit = section_time_limit if section_time_limit else qus_obj.section_time_limit
            qus_obj.question = request.POST.get("question",qus_obj.question)
            qus_obj.option1 = request.POST.get("option1",qus_obj.option1)
            qus_obj.option2 = request.POST.get("option2",qus_obj.option2)
            qus_obj.option3 = request.POST.get("option3",qus_obj.option3)
            qus_obj.option4 = request.POST.get("option4",qus_obj.option4)
            qus_obj.correct_answer = request.POST.get("correct_option",qus_obj.correct_answer)
            if request.FILES.get("upload_image"):
                qus_obj.image = request.FILES.get("upload_image")
            qus_obj.save()
            if request.FILES.get("upload_image"):
                qus_obj.image = request.FILES.get("upload_image")
                qus_obj.save()
        return redirect("admin_dashboard:olympiad_ques_list", id = kwargs["olymp_id"])

class OlympiadManagementListExams(View):
    def get(self,request,*args, **kwargs):
        olymp_list = OlympiadExam.objects.all().order_by("exam_date")
        context = {
            "olymp_list": olymp_list
        }
        return render(request,"olympiad_management/olymp_exam_list.html", context)

    def post(self, request, *args, **kwargs):
        if request.POST.get("action") == "delete":
            obj = OlympiadExam.objects.get(id=request.POST.get("objId"))
            obj.delete()
            to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
            return JsonResponse(to_return,safe=True,)
        elif request.POST.get("action") == "notification":
            olympiad = OlympiadExam.objects.get(id = request.POST.get("objId"))
            registrations = StudentPayments.objects.filter(olympiad_exam = olympiad)
            registered_users = []
            for registration in registrations:
                registered_users.append(registration.student.email)

            if len(registered_users) >= 1:
                subject = f'Olympiad alert'
                email_from = settings.EMAIL_HOST_USER
                plaintext = get_template('email_templates/olympiad_notification.txt')
                htmly     = get_template('email_templates/olympiad_notification.html')

                d = {
                    'title': olympiad.paper.title,
                    'date': olympiad.exam_date,
                    'time': olympiad.exam_time,
                }

                text_content = plaintext.render(d)
                html_content = htmly.render(d)
                msg = EmailMultiAlternatives(subject, text_content, email_from, registered_users)
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            to_return = {
                        "title":"Mail send successfully",
                        "icon":"success",
                    }
            return JsonResponse(to_return,safe=True,)
        else:
            print(args)
            print(kwargs)
            print(request.POST)
            paper_obj = Papers.objects.create(
                title = request.POST.get("paper_title"),
                description = request.POST.get("paper_description"),
                instructions = request.POST.get("general_instructions"),
                price = request.POST.get("price"),
                is_competitive=False,
            )
            olymp_obj = OlympiadExam.objects.create(
                exam_date = request.POST.get("exam_date"),
                exam_time = request.POST.get("exam_time"),
                paper = paper_obj
            )
            return redirect("admin_dashboard:olympiad_ques_list",id=olymp_obj.id)
        
class OlympiadRegistrations(View):
    def get(self, request, *args, **kwargs):
        olympiad = OlympiadExam.objects.get(id = kwargs["id"])
        registrations = StudentPayments.objects.filter(olympiad_exam = olympiad)
        return render(request, "olympiad_management/olymp_registrations.html", context = {"registrations": registrations})
        
class OlympiadResults(View):
    def get(self, request, *args, **kwargs):
        olympiad = OlympiadExam.objects.get(id = kwargs["id"])
        results = AttendedPapers.objects.filter(olympiad_exam=olympiad)
        return render(request, "olympiad_management/olymp_results.html", context = {"results": results})