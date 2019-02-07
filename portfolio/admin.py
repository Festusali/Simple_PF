from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import UserData, Project, UserModel


UserAdmin.list_display = ('email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')

admin.site.register(UserModel, UserAdmin)
admin.site.register(UserData)
admin.site.register(Project)