from django.contrib import admin
from .models import CustomUser, Confirm
from django.contrib.auth.admin import UserAdmin


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Confirm)