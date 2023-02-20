from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views



urlpatterns = [
    path("", views.AdminLogin.as_view(),name="admin-login"),
    path("forget-password", views.AdminForgetPassword.as_view(),name="admin-forget-password"),

    path("dashboard", views.AdminDashboard.as_view(),name="admin-dashboard"),

    # Assets
    path("banner-view", views.BannerView.as_view(),name="home-banner"),
    path("banner-view/add", views.AddBanner.as_view(),name="home-banner-add"),
    path("banner-view/edit/<str:id>", views.EditBanner.as_view(),name="home-banner-edit"),
    path("marquee", views.MarqueeText.as_view(),name="marquee"),
    
    # Blogs
    path("blogs", views.BlogsList.as_view(),name="blogs-list"),
    path("blogs/add", views.AddBlog.as_view(),name="blogs-add"),
    path("blogs/edit/<str:id>", views.EditBlog.as_view(),name="blogs-edit"),



    path("contact-enquiry", views.ContactEnquiry.as_view(),name="contact-enquiry"),

]

admin.autodiscover()
admin.site.login = login_required(views.AdminLogin)