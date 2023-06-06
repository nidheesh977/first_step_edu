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
    path("event/detail/<str:id>", views.EditDetails.as_view(),name="registered-events-detail"),

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
    path("class-<str:class_id>/subjects-<str:subject_id>/paper-<str:paper_id>/questions/add-bulk-question", views.CMBulkQuestions.as_view(),name="clsm-bulk-questions"),
    path("class-<str:class_id>/subjects-<str:subject_id>/paper-<str:paper_id>/questions/add-bulk-images", views.CMBulkImageGenerateLink.as_view(),name="clsm-bulk-images"),
    
    path("class-<str:class_id>/subjects-<str:subject_id>/add-paper", views.CMAddPaper.as_view(),name="clsm-add-paper"),
    path("class-<str:class_id>/subjects-<str:subject_id>/edit-paper-<str:id>", views.CMEditPaper.as_view(),name="clsm-edit-paper"),

    path("class-<str:class_id>/subjects-<str:subject_id>/paper-<str:paper_id>/add-question", views.CMAddQuestions.as_view(),name="clsm-paper-qus-add"),
    path("class-<str:class_id>/subjects-<str:subject_id>/paper-<str:paper_id>/edit-question/<str:qus_id>", views.CMEditQuestions.as_view(),name="clsm-paper-qus-edit"),


    path("contact-enquiry", views.ContactEnquiry.as_view(),name="contact-enquiry"),
    path("registered-users", views.RegistredUsers.as_view(),name="registered-users"),


    # Competitive management
    path("competitive-exams-list",views.CompetitiveExamsList.as_view(), name="competitve_exams_list"),
    path("competitive-exam-<str:exm_id>/competitive-papers-list",views.CompetitiveManagementPapersList.as_view(), name="competitve_papers_list"),
    path("competitive-exam-<str:exm_id>/add-paper",views.CompetitiveManagementAddPaper.as_view(), name="competitve_add_paper"),
    path("competitive-exam-<str:exm_id>/edit-paper-<str:id>",views.CompetitiveManagementEditPaper.as_view(), name="competitve_edit_paper"),

    
    path("competitive-exam-<str:exm_id>/paper-<str:paper_id>/questions", views.CMQuestionsList.as_view(),name="comp_ques_list"),
    path("competitive-exam-<str:exm_id>/paper-<str:paper_id>/questions/add-bulk-images", views.CMBulkImageGenerateLink.as_view(),name="comp-bulk-images"),
    path("competitive-exam-<str:exm_id>/paper-<str:paper_id>/questions/add-question", views.CMAddQuestions.as_view(),name="comp_ques_add"),
    path("competitive-exam-<str:exm_id>/paper-<str:paper_id>/questions/add-bulk-question", views.CMBulkQuestions.as_view(),name="comp-ques-bulk-questions"),
    path("competitive-exam-<str:exm_id>/paper-<str:paper_id>/edit-question/<str:qus_id>", views.CMEditQuestions.as_view(),name="comp_ques_edit"),
    path("payment-details", views.PaymentDetails.as_view(), name = "payment-details"),
    path("user-payment-details/user-<str:id>", views.UserPaymentDetails.as_view(), name = "user-payment-details"),

    # Olympiad management
    path("olympiad-add-exam", views.OlympiadManagementAddExam.as_view(), name = "olympiad_add_exam"),
    path("olympiad-add-question/olympiad-<str:id>", views.OlympiadManagementAddQuestion.as_view(), name = "olympiad_add_ques"),
    path("olympiad-edit-exam/olympiad-<str:id>", views.OlympiadManagementEditExam.as_view(), name = "olympiad_edit_exam"),
    path("olympiad-exams-list", views.OlympiadManagementListExams.as_view(), name = "olympiad_exams_list"),
    path("olympiad-question-list/olympiad-<str:id>", views.OlympiadManagementQuestionList.as_view(), name = "olympiad_ques_list"),
    path("olympiad-question-list/olympiad-<str:id>/add-bulk-images", views.OlympiadBulkImageGenerateLink.as_view(),name="olympiad-bulk-images"),
    path("olympiad-edit-question/olympiad-<str:olymp_id>/question-<str:ques_id>", views.OlympiadManagementEditQuestion.as_view(), name = "olympiad_edit_ques"),
    path("olympiad-registrations/olympiad-<str:id>", views.OlympiadRegistrations.as_view(), name = "olympiad_registrations"),
    path("olympiad-result/olympiad-<str:id>", views.OlympiadResults.as_view(), name = "olympiad_result"),
]

admin.autodiscover()
admin.site.login = login_required(views.AdminLogin)