
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

from application.models import *
from utils.constants import EmailContents, ImageSizes
from utils.functions import OTP_Gen, is_ajax, reterive_request_data


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
        Events.objects.get(id=request.POST.get("objId")).delete()
        to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
        return JsonResponse(to_return,safe=True,)

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
        objs = CustomUser.objects.all().exclude(is_superuser=True)
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
            obj.save()
            return redirect("admin_dashboard:clsm-classes-list")
        else:
            Classes.objects.create(
                title = request.POST.get("class_title"),
                description = request.POST.get("class_description"),
                price = request.POST.get("price"),
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
            obj.meta_title = request.POST.get("meta_title",obj.meta_title)
            obj.meta_description = request.POST.get("meta_description",obj.meta_description)
            obj.meta_keywords = request.POST.get("meta_keywords",obj.meta_keywords)
            obj.save()
            return redirect("admin_dashboard:clsm-subjects-list",class_id=cls_obj.id)
        else:
            sub_obj = Subjects.objects.create(
                title = request.POST.get("subject_title"),
                description = request.POST.get("subject_description"),
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
        objs = sub_obj.assigned_papers.filter(is_competitive=False)
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
            obj.save()
            return redirect("admin_dashboard:clsm-papers-list",class_id=CLASS_ID,subject_id=SUBJECT_ID)
        else:
            paper_obj = Papers.objects.create(
                title = request.POST.get("paper_title"),
                description = request.POST.get("paper_description"),
                instructions = request.POST.get("general_instructions"),
            )
            sub_obj.assigned_papers.add(paper_obj)
            return redirect("admin_dashboard:clsm-papers-list",class_id=CLASS_ID,subject_id=SUBJECT_ID)

class CMQuestionsList(View):
    def get(self,request,*args, **kwargs):
        print(kwargs)
        PAPER_ID = kwargs.get("paper_id")
        CLASS_ID = kwargs.get("class_id")
        SUBJECT_ID = kwargs.get("subject_id")
        paper_obj = get_object_or_404(Papers,id=PAPER_ID)

        if CLASS_ID and SUBJECT_ID:
            context = {
                "qus_obj":paper_obj.assigned_questions.all(),
                "cls_id":CLASS_ID,
                "sub_id":SUBJECT_ID,
                "paper_id":PAPER_ID,
            }
            return render(request,"class_management/papers/questions-list.html",context)
        else:
            context = {
                'exm_id':kwargs.get("exm_id"),
                "paper_id":PAPER_ID,
                "qus_obj":paper_obj.assigned_questions.all(),
            }
            return render(request,"competitive_management/competitve_qus_list.html",context)
    
    def post(self,request,*args, **kwargs):
        get_object_or_404(Questions,id=request.POST.get("objId")).delete()
        to_return = {
                        "title":"Deleted",
                        "icon":"success",
                    }
        return JsonResponse(to_return,safe=True,)

class CMAddQuestions(View):
    def get(self,request,*args, **kwargs):

        PAPER_ID = kwargs.get("paper_id")
        CLASS_ID = kwargs.get("class_id")
        SUBJECT_ID = kwargs.get("subject_id")
        paper_obj = get_object_or_404(Papers,id=PAPER_ID)
        if CLASS_ID and SUBJECT_ID:
            context = {
                "cls_id":CLASS_ID,
                "sub_id":SUBJECT_ID,
                "paper_id":PAPER_ID,
                "paper_name":paper_obj.title,
            }
            return render(request,"class_management/papers/questions-add.html",context)
        else:
            context = {
                'exm_id':kwargs.get("exm_id"),
                "paper_id":PAPER_ID,
                "paper_name":paper_obj.title,
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
            correct_answer = request.POST.get("correct_option"),
            )
            paper_obj = get_object_or_404(Papers,id=PAPER_ID)
            paper_obj.assigned_questions.add(qus_obj)

            if CLASS_ID and SUBJECT_ID:
                return redirect("admin_dashboard:clsm-questions-list", class_id=CLASS_ID, subject_id=SUBJECT_ID, paper_id=PAPER_ID)
            else:
                return redirect("admin_dashboard:comp_ques_list", paper_id=PAPER_ID)
            
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
            }
            return render(request,"class_management/papers/questions-edit.html",context)
        else:
            context = {
                "paper_id":PAPER_ID,
                "obj":qus_obj,
                "time_limit":TIME_LIMIT,
            }
            return render(request,"competitive_management/competitve_qus_edit.html",context)
    
    def post(self,request,*args, **kwargs):
        PAPER_ID = kwargs.get("paper_id")
        CLASS_ID = kwargs.get("class_id")
        SUBJECT_ID = kwargs.get("subject_id")
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
            qus_obj.save()

            if CLASS_ID and SUBJECT_ID:
                return redirect("admin_dashboard:clsm-questions-list", class_id=CLASS_ID, subject_id=SUBJECT_ID, paper_id=PAPER_ID)
            else:
                return redirect("admin_dashboard:comp_ques_list", paper_id=PAPER_ID)
        else:
            messages.error(request, "Invalid Time duration format")
            if CLASS_ID and SUBJECT_ID:
                return redirect("admin_dashboard:clsm-paper-qus-edit", class_id=CLASS_ID, subject_id=SUBJECT_ID, paper_id=PAPER_ID, qus_id =kwargs.get("qus_id"))
            else:
                return redirect("admin_dashboard:comp_ques_edit", paper_id=PAPER_ID, qus_id =kwargs.get("qus_id"))
            

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
            obj.save()
            return redirect("admin_dashboard:competitve_papers_list")
    
        else:
            com_obj = get_object_or_404(CompetitiveExam,id=kwargs.get("exm_id"))
            paper_obj = Papers.objects.create(
                title = request.POST.get("paper_title"),
                description = request.POST.get("paper_description"),
                instructions = request.POST.get("general_instructions"),
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
            )
            to_return = {"obj":list(obj)[0]}
            return JsonResponse(to_return,safe=True,)
        
        if request.POST.get("edit_form") != None:
            obj = get_object_or_404(CompetitiveExam,id=request.POST.get("id"))       
            obj.exam_name = request.POST.get("exam_title",obj.exam_name)
            obj.description = request.POST.get("exam_description",obj.description)
            obj.price = request.POST.get("exam_price",obj.price)
            obj.save()
            return redirect("admin_dashboard:competitve_exams_list")
    
        else:
            CompetitiveExam.objects.create(
                exam_name = request.POST.get("exam_title"),
                description = request.POST.get("exam_description"),
                price = request.POST.get("exam_price"),
            )
            return redirect("admin_dashboard:competitve_exams_list")