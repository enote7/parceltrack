from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views  # Import auth_views


urlpatterns = [
    path('', index, name='index'),
    path('signup/', signup, name='signup'),
    path('confirm_email/<str:uidb64>/<str:token>/', confirm_email, name='confirm_email'),
    path('email_confirmation/', email_confirmation, name='email_confirmation'),
    path('email_confirmed/', email_confirmed, name='email_confirmed'),
    path('email_confirmation_invalid/', email_confirmation_invalid, name='email_confirmation_invalid'),
    path('login/', login_view, name='login'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="reset.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name='password_reset_complete'),
    path('logout/', logout_view, name='logout'),
    path('register_parcel/', register_parcel_detail, name='register_parcel'),
    path('parceldetailhistory/', parceldetailhistory, name='parceldetailhistory'),
    path('edit/<int:parcel_id>/', edit_parcel, name='edit_parcel'),
    path('download-parcel-report/', download_parcel_report, name='download_parcel_report'),
    path('track-status/', track_status, name='track_status'),
    path('about_us/', about_us, name='about_us'),
    path('home/', home, name='home'),
]
 