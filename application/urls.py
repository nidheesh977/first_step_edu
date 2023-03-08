from django.urls import path
import environ
from . import views
env = environ.Env()
blog_url = env.get_value("blog_url")


urlpatterns = [
    path("",views.IndexView.as_view(),name="index-page"),

    path("signup",views.SignUpView.as_view(),name="signup"),
    path("signin",views.SignInView.as_view(),name="signin"),
    path("forget-password",views.ForgetPassword.as_view(),name="forget-password"),
    path("logout",views.LogoutView.as_view(),name="logout"),

    path("dashboard",views.AccountDashboard.as_view(),name="account-dashboard"),
    path("dashboard/enrolls",views.EnrolledClassesView.as_view(),name="enrolled_classes"),
    path("dashboard/enrolls-<str:id>",views.EnrolledSubjectsView.as_view(),name="enrolled_subject"),
    path("dashboard/registered-events",views.RegisterdEventsView.as_view(),name="registered_events"),

    path("exam/paper-<str:id>",views.ExamView.as_view(),name="exam"),

    path("about-us",views.AboutUs.as_view(),name="about-us"),
    path("why-choose-us",views.WhyChooseUs.as_view(),name="why-choose-us"),
    path("our-team",views.OurTeam.as_view(),name="our-team"),
    path("blogs",views.BlogsList.as_view(),name="blogs-page"),
    path(f'{blog_url}/<slug:url>', views.BlogDetailView.as_view(), name='blog-detail'),

    path("announcement",views.Announcement.as_view(),name="announcement"),
    path("contact-us",views.ContactUsView.as_view(),name="contact-us"),
    path("competitive",views.CompetitivePage.as_view(),name="competitive_page"),
    path("school",views.SchoolPage.as_view(),name="school"),
    path("subject-<str:pk>",views.SchoolSubjectWise.as_view(),name="school_subject_wise"),
    path("papers",views.SchoolPageWise.as_view(),name="school_paper_wise"),
    path("events",views.EventsPage.as_view(),name="events"),

    path("make-payment-<str:id>",views.MakePayment.as_view(),name="makepayment"),

    # path("class-<str:id>/papers",views.PapersView.as_view(),name="class_papers"),

    path("checkout/<str:id>",views.Checkout.as_view(),name="checkout"),
    
]