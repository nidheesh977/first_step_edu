
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.conf.urls.static import static
from application.views import callback

urlpatterns = [
    path('summernote/', include('django_summernote.urls')),
    # re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('db/', admin.site.urls),
    path('',include(('application.urls',"application"), namespace='application')),
    path('admin/',include(('admin_dashboard.urls',"admin_dashboard"), namespace='custom_admin')),
    path("razorpay/callback/<str:id>/<str:uid>", callback, name="callback"),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)