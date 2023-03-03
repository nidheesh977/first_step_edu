from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _

from .models import *
from django_summernote.admin import SummernoteModelAdmin


class SomeModelAdmin(SummernoteModelAdmin):
    summernote_fields = ('instructions',)


class BlogModelAdmin(SummernoteModelAdmin):
    summernote_fields = ('overall_description',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    fieldsets = (
        (None, {'fields': ('email', 'mobile_number', 'password',)}),
        (_('Personal info'), {'fields': (
            'id', 
            'first_name', 
            'last_name',
            "profile_pic",
            "parent_name",
            "class_name",
            "school_name",
            "state",
            "city",
            "gender",
            )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff','is_superuser',)}),
        (_('Important dates'), {
         'fields': ('last_login', 'created_on', 'updated_on')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'first_name', 
                'last_name',
                'email', 
                'mobile_number', 
                "parent_name",
                "class_name",
                "school_name",
                "state",
                "city",
                "gender",
                'password1', 
                'password2',
                ), }),)
    list_display = ("id", 'email', "mobile_number",'is_active',)
    list_display_links = ("email",)

    readonly_fields = ("created_on", "updated_on", 'id')
    search_fields = ('email',)
    ordering = ('email',)



admin.site.register(Papers, SomeModelAdmin)
admin.site.register(ContactUs)
admin.site.register(Blogs,BlogModelAdmin)
admin.site.register(Events)
admin.site.register(RegisterdEvents)
admin.site.register(News)
admin.site.register(Testimonials)
admin.site.register(ResultAnnouncements)
admin.site.register(HomeBanners)
admin.site.register(MarqueeTexts)
admin.site.register(Questions)
admin.site.register(Subjects)
admin.site.register(Classes)
admin.site.register(CompetitiveExam)

