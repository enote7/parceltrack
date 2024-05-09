from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ParcelDetail
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'is_staff', 'is_superuser', 'email_confirmed', 'is_client', 'is_parcel_staff')  # Include new fields in list display
    search_fields = ('email', 'username')
    readonly_fields = ('last_login',)  # Remove 'date_joined'

    filter_horizontal = ()
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_client', 'is_parcel_staff')}),  # Include is_parcel_staff in Permissions fieldset
        ('Email Confirmation', {'fields': ('email_confirmed',)}),  # Add email_confirmed field
        ('Important dates', {'fields': ('last_login',)}),
        ('Profile Picture', {'fields': ('profile_picture',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_superuser', 'email_confirmed', 'profile_picture', 'is_client', 'is_parcel_staff')}  # Include new fields in add fieldsets
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)


class ParcelDetailAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'client_name', 'receiver_name', 'delivery_date', 'status')  # Display these fields in the admin list view
    search_fields = ('tracking_number', 'client_name__username', 'receiver_name')  # Add search functionality based on these fields
    list_filter = ('status',)  # Add filter option for status field

admin.site.register(ParcelDetail, ParcelDetailAdmin)