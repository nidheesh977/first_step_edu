
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, View, TemplateView
from . models  import *
from django.contrib import messages
from utils.constants import  TextConstants
class IndexView(View):
    def get(self,request, *args, **kwargs):
        return render(request, "index.html")

class AboutUs(TemplateView):
    template_name="about-us.html"

class WhyChooseUs(TemplateView):
    template_name="why-choose-us.html"



class OurTeam(TemplateView):
    template_name="our-team.html"


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
