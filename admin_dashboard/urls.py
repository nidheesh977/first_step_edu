from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views



urlpatterns = [
    path("", views.AdminLogin.as_view(),name="admin-login"),
    path("forget-password", views.AdminForgetPassword.as_view(),name="admin-forget-password"),

    path("dashboard", views.AdminDashboard.as_view(),name="admin-dashboard"),

    path("banner-view", views.BannerView.as_view(),name="home-banner"),
    path("banner-view/add", views.AddBanner.as_view(),name="home-banner-add"),
    path("banner-view/edit/<str:id>", views.EditBanner.as_view(),name="home-banner-edit"),
    path("marquee", views.MarqueeText.as_view(),name="marquee"),
    
    path("contact-enquiry", views.ContactEnquiry.as_view(),name="contact-enquiry"),

]

admin.autodiscover()
admin.site.login = login_required(views.AdminLogin)