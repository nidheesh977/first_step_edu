from django.urls import path
from . import views
urlpatterns = [
    path("", views.AdminLogin.as_view(),name="admin-login"),
    path("forget-password", views.AdminForgetPassword.as_view(),name="admin-forget-password"),

    path("dashboard", views.AdminDashboard.as_view(),name="dashboard"),

    path("banner-view", views.BannerView.as_view(),name="home-banner"),
    path("banner-view/add", views.AddBanner.as_view(),name="home-banner-add"),
    path("banner-view/edit", views.BannerView.as_view(),name="home-banner-edit"),

    path("contact-enquiry", views.ContactEnquiry.as_view(),name="contact-enquiry"),

]