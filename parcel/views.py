from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .forms import SignupForm, LoginForm
from django.contrib.auth import get_user_model

User = get_user_model()
from .forms import ParcelDetailForm
from .models import ParcelDetail
from django.shortcuts import render, redirect
from .forms import *
from .models import *


# SIGNUP
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user_type = form.cleaned_data['user_type']
            if user_type == 'client':
                user.is_client = True
            elif user_type == 'parcelstaff':
                user.is_parcel_staff = True
            user.save()
            send_confirmation_email(request, user)  # Send confirmation email
            messages.success(request, 'Please check your email to confirm your account.')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def send_confirmation_email(request, user):
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    confirmation_link = request.build_absolute_uri(reverse('confirm_email', kwargs={'uidb64': uidb64, 'token': token}))
    subject = 'Confirm your email address'
    message = f"Please click the following link to confirm your email address: {confirmation_link}"
    send_mail(subject, message, 'enote7y@gmail.com', [user.email])

# LOGIN
@csrf_exempt  # Assuming you're using csrf_exempt for specific reasons
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.email_confirmed:
                    login(request, user)
                    # Check user type and redirect accordingly
                    if user.is_client:
                        return redirect('home')
                    elif user.is_parcel_staff:
                        return redirect('home')
                    else:
                        messages.error(request, 'Invalid user type.')
                else:
                    messages.error(request, 'Please confirm your email address to log in.')
            else:
                # Pass error message to the form
                form.add_error(None, 'Invalid email or password. Please try again.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

# EMAIL CONFIRMATION
def confirm_email(request, uidb64, token):
    try:
        uid = str(urlsafe_base64_decode(uidb64), 'utf-8')
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.email_confirmed = True
        user.save()
        return render(request, 'email_confirmed.html')
    else:
        return render(request, 'email_confirmation_invalid.html')

def email_confirmation(request):
    return render(request, 'confirmation_email.html')

def email_confirmed(request):
    return render(request, 'email_confirmed.html')

def email_confirmation_invalid(request):
    return render(request, 'email_confirmation_invalid.html')

def index(request):
    return render(request, 'index.html')

# PASSWORD RESET
def send_password_reset_email(request, email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'User with this email does not exist.')
        return None

    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    reset_url = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token}))
    email_subject = 'Password Reset'
    email_body = render_to_string('password_reset_email.html', {'reset_url': reset_url})
    send_mail(email_subject, email_body, 'enote7y@gmail.com', [email])

def csrf_failure_view(request, reason=""):
    return render(request, 'csrf_failure.html', {'reason': reason})

def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def register_parcel_detail(request):
    if not request.user.is_client:
        if request.method == 'POST':
            form = ParcelDetailForm(request.POST, request.FILES)
            if form.is_valid():
                parcel_detail = form.save()
                return redirect('parceldetailhistory')
        else:
            form = ParcelDetailForm()
        return render(request, 'regclientparcel.html', {'form': form})
    else:
        return HttpResponse("Permission denied")

def parceldetailhistory(request):
    if request.user.is_parcel_staff:
        parcel_details = ParcelDetail.objects.all()
        context = {
            'parcels': parcel_details
        }
        return render(request, 'parceldetailhistory.html', context)
    else:
        return HttpResponse("Permission denied")

import logging

logger = logging.getLogger(__name__)

def edit_parcel(request, parcel_id):
    if request.user.is_parcel_staff:
        parcel = get_object_or_404(ParcelDetail, pk=parcel_id)
        if request.method == 'POST':
            form = ParcelDetailForm(request.POST, instance=parcel)
            if form.is_valid():
                form.save()
                return redirect('parceldetailhistory')  # Redirect to the home page after saving
        else:
            form = ParcelDetailForm(instance=parcel)
        return render(request, 'edit_parcel.html', {'form': form})
    else:
        return HttpResponse("Permission denied")



@login_required
def download_parcel_report(request):
    if not request.user.is_parcel_staff:
        return HttpResponse("Permission denied")

    parcel_details = ParcelDetail.objects.all()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle('Parcel Detail Report')

    # Add Title
    pdf.drawString(50, 800, 'Parcel Detail Report')

    y_position = 750
    for record in parcel_details:
        pdf.drawString(100, y_position, f'Client Name: {record.client_name}')
        pdf.drawString(100, y_position - 20, f'Client Contact: {record.client_contact}')  
        pdf.drawString(100, y_position - 40, f'Description: {record.description}')
        pdf.drawString(100, y_position - 60, f'Value: {record.get_value_display()}')
        pdf.drawString(100, y_position - 80, f'Destination: {record.get_destination_display()}')
        pdf.drawString(100, y_position - 100, f'Receiver Name: {record.receiver_name}')
        pdf.drawString(100, y_position - 120, f'Receiver Contact: {record.receiver_contact}')
        pdf.drawString(100, y_position - 140, f'Delivery Date: {record.delivery_date}')
        pdf.drawString(100, y_position - 160, f'Delivery Time: {record.get_delivery_time_display()}')
        pdf.drawString(100, y_position - 180, f'Sender Email: {record.sender_email}')
        pdf.drawString(100, y_position - 200, f'Tracking Number: {record.tracking_number}')
        pdf.drawString(100, y_position - 220, f'Status: {record.get_status_display()}')
        y_position -= 240
        pdf.drawString(100, y_position, '-' * 100)  # Line to separate records
        y_position -= 20  # Space after the line

    pdf.save()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="parcel_detail_report.pdf"'
    buffer.seek(0)
    response.write(buffer.getvalue())

    return response

def track_status(request):
    if not request.user.is_authenticated:
        return HttpResponse("Permission denied")

    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')
        try:
            parcel = ParcelDetail.objects.get(tracking_number=tracking_number)
            context = {
                'found': True,
                'status': parcel.status,
                'receiver_name': parcel.receiver_name
            }
        except ParcelDetail.DoesNotExist:
            context = {
                'found': False,
                'message': 'No details found for the provided tracking number. Please check your input.'
            }
    else:
        context = {}
    return render(request, 'tracksatus.html', context)

def about_us(request):
    context = {
        'contacts': [
            {'name': 'Dero', 'image': 'q1.jpg', 'contact': 'dero@example.com'},
            {'name': 'Lyn', 'image': 'q2.jpg', 'contact': 'lyn@example.com'}
        ],
        'mission': 'Our mission is to provide efficient and reliable parcel tracking services.',
        'goal': 'Our goal is to ensure timely and secure delivery of goods from source to destination.',
        'purpose': 'The purpose of our system is to enhance transparency and customer satisfaction in parcel delivery.'
    }
    return render(request, 'about_us.html', context)


def home(request):
    return render(request, 'home.html')
