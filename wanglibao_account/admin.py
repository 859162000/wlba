from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from wanglibao_margin.models import Margin
from wanglibao_profile.models import WanglibaoUserProfile


class ProfileInline(admin.StackedInline):
    model = WanglibaoUserProfile


class MarginInline(admin.StackedInline):
    model = Margin


class UserProfileAdmin(UserAdmin):
    inlines = [ProfileInline, MarginInline]
    list_display = ('wanglibaouserprofile', 'is_active', 'date_joined', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)