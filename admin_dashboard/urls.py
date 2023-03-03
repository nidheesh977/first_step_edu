from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views



urlpatterns = [
    path("", views.AdminLogin.as_view(),name="admin-login"),
    path("forget-password", views.AdminForgetPassword.as_view(),name="admin-forget-password"),

    path("dashboard", views.AdminDashboard.as_view(),name="admin-dashboard"),
    path("change-password", views.AdminChangePassword.as_view(),name="admin_change_password"),

    # Assets
    path("banner-view", views.BannerView.as_view(),name="home-banner"),
    path("banner-view/add", views.AddBanner.as_view(),name="home-banner-add"),
    path("banner-view/edit/<str:id>", views.EditBanner.as_view(),name="home-banner-edit"),
    path("marquee", views.MarqueeText.as_view(),name="marquee"),
    
    # Blogs
    path("blogs", views.BlogsList.as_view(),name="blogs-list"),
    path("blog/add", views.AddBlog.as_view(),name="blog-add"),
    path("blog/edit/<str:id>", views.EditBlog.as_view(),name="blog-edit"),

    # Events
    path("events", views.EventsList.as_view(),name="events-list"),
    path("event/add", views.AddEvent.as_view(),name="event-add"),
    path("event/edit/<str:id>", views.EditEvent.as_view(),name="event-edit"),

    # News
    path("news", views.NewsList.as_view(),name="news-list"),
    path("news/add", views.AddNews.as_view(),name="news-add"),
    path("news/edit/<str:id>", views.EditNews.as_view(),name="news-edit"),

    # Testimonials
    path("testimonials", views.TestimonialsList.as_view(),name="testimonials-list"),
    path("testimonial/add", views.AddTestimonial.as_view(),name="testimonial-add"),
    path("testimonial/edit/<str:id>", views.EditTestimonial.as_view(),name="testimonial-edit"),


    # ResultAnnouncements
    path("result-announcements", views.ResultAnnouncementsList.as_view(),name="result_announcements-list"),
    path("result-announcement/add", views.AddResultAnnouncement.as_view(),name="result_announcement-add"),
    path("result-announcement/edit/<str:id>", views.EditResultAnnouncement.as_view(),name="result_announcement-edit"),


    # Class Management
    path("classes", views.CMClassListView.as_view(),name="clsm-classes-list"),
    path("class-<str:class_id>/subjects", views.CMSubjectsListView.as_view(),name="clsm-subjects-list"),
    path("class-<str:class_id>/subjects-<str:subject_id>/papers", views.CMPapersListView.as_view(),name="clsm-papers-list"),
    path("class-<str:class_id>/subjects-<str:subject_id>/paper-<str:paper_id>/questions", views.CMQuestionsList.as_view(),name="clsm-questions-list"),
    path("class-<str:class_id>/subjects-<str:subject_id>/paper-<str:paper_id>/add-question", views.CMAddQuestions.as_view(),name="clsm-paper-qus-add"),
    path("class-<str:class_id>/subjects-<str:subject_id>/paper-<str:paper_id>/edit-question/<str:qus_id>", views.CMEditQuestions.as_view(),name="clsm-paper-qus-edit"),


    path("contact-enquiry", views.ContactEnquiry.as_view(),name="contact-enquiry"),
    path("registered-users", views.RegistredUsers.as_view(),name="registered-users"),


    # Competitive management
    path("competitive-exams-list",views.CompetitiveExamsList.as_view(), name="competitve_exams_list"),
    path("competitive-exam-<str:exm_id>/competitive-papers-list",views.CompetitiveManagementPapersList.as_view(), name="competitve_papers_list"),
    path("competitive-exam-<str:exm_id>/paper-<str:paper_id>/questions", views.CMQuestionsList.as_view(),name="comp_ques_list"),
    path("competitive-exam-<str:exm_id>/paper-<str:paper_id>/questions/add-question", views.CMAddQuestions.as_view(),name="comp_ques_add"),
    path("competitive-exam-<str:exm_id>/paper-<str:paper_id>/edit-question/<str:qus_id>", views.CMEditQuestions.as_view(),name="comp_ques_edit"),

]

admin.autodiscover()
admin.site.login = login_required(views.AdminLogin)