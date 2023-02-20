from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import View
from django.shortcuts import  redirect

class SuperUserCheck(UserPassesTestMixin, View):
    def test_func(self):
        if self.request.user.is_superuser:
            return self.request.user.is_superuser
        else:
            return redirect("admin_dashboard:admin-login")