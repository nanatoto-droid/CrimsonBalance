from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser
#     list_display = ['username', 'email', 'user_type', 'is_staff', 'is_verified']
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('user_type', 'phone_number', 'blood_group', 
#                           'date_of_birth', 'address', 'city', 
#                           'is_verified', 'profile_picture')}),
#     )
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         (None, {'fields': ('user_type', 'phone_number', 'blood_group', 
#                           'date_of_birth', 'address', 'city', 
#                           'is_verified', 'profile_picture')}),
#     )

# admin.site.register(CustomUser, CustomUserAdmin)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'is_staff', 'is_verified']
    fieldsets = (
        (None, {'fields': (
            'username', 'password', 'email',
            'first_name', 'last_name',
            'user_type', 'phone_number', 'blood_group',
            'date_of_birth', 'address', 'city',
            'is_verified', 'profile_picture'
        )}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'user_type', 'phone_number', 'blood_group',
                'date_of_birth', 'address', 'city',
                'is_verified', 'profile_picture'
            ),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)