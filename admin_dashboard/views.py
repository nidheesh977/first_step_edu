from django.shortcuts import render
from django.views.generic import View, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from application.models import  *

class AdminDashboard(View):
    def get(self,request,*args, **kwargs):
        return render(request,"admin_dashboard_base.html")



class BannerView(View):
    def get(self,request,*args, **kwargs):
        return render(request,"banner-view.html")


class AddBanner(View):
    def get(self,request,*args, **kwargs):
        return render(request,"banner-add.html")


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