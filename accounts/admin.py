from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'name', 'role', 'is_staff', 'is_active', 'is_premium')
    list_filter = ('is_staff', 'is_active', 'is_premium', 'role')

    fieldsets = (
        (None, {'fields': ('email', 'auth0_id', 'password')}),
        ('Personal info', {'fields': ('name', 'profile_picture', 'phone_number', 'date_of_birth', 'bio', 'role')}),  # added role
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'is_premium')}),
    )
    readonly_fields = ('auth0_id',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)