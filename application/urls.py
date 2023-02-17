from django.urls import path
from . import views
urlpatterns = [
    path("",views.IndexView.as_view(),name="index-page"),
    path("about-us",views.AboutUs.as_view(),name="about-us"),
    path("why-choose-us",views.WhyChooseUs.as_view(),name="why-choose-us"),
    path("our-team",views.OurTeam.as_view(),name="our-team"),
    path("announcement",views.Announcement.as_view(),name="announcement"),
    path("contact-us",views.ContactUsView.as_view(),name="contact-us"),
]