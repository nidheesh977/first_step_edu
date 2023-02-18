from django.urls import path
from . import views
urlpatterns = [
    path("",views.IndexView.as_view(),name="index-page"),

    path("signup",views.SignUpView.as_view(),name="signup"),
    path("signin",views.SignInView.as_view(),name="signin"),
    path("forget-password",views.ForgetPassword.as_view(),name="forget-password"),
    path("logout",views.LogoutView.as_view(),name="logout"),

    path("dashboard",views.AccountDashboard.as_view(),name="account-dashboard"),

    path("about-us",views.AboutUs.as_view(),name="about-us"),
    path("why-choose-us",views.WhyChooseUs.as_view(),name="why-choose-us"),
    path("our-team",views.OurTeam.as_view(),name="our-team"),
    path("announcement",views.Announcement.as_view(),name="announcement"),
    path("contact-us",views.ContactUsView.as_view(),name="contact-us"),
    

]