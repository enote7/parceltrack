from django import forms
from django.core.mail import send_mail
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, ParcelDetail
from django.contrib.auth import get_user_model

User = get_user_model()

# Signup Form
class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_picture = forms.ImageField(label='Profile Picture', required=False)
    user_type = forms.ChoiceField(choices=[('client', 'Client'), ('parcelstaff', 'Parcel Staff')], label='User Type')

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2', 'profile_picture', 'user_type')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

# LOGIN FORM
class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=[('client', 'Client'), ('parcelstaff', 'Parcel Staff')], label='User Type')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Add any email validation logic here if needed
        return email

# USER MODEL
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username')


# PASSWORD RESET FORM
class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='Email')



  # Assuming CustomUser is in the 'parcel' app

class ParcelDetailForm(forms.ModelForm):
    # Get users for dropdown
    clients = CustomUser.objects.filter(is_client=True)

    client_name = forms.ModelChoiceField(queryset=clients, empty_label="Select Client")
    client_contact = forms.CharField(max_length=100, required=True)
    description = forms.CharField(widget=forms.Textarea)
    
    value_choices = (
        ('Fragile', 'Fragile'),
        ('Durable', 'Durable'),
        ('Perishable', 'Perishable'),
    )
    value = forms.ChoiceField(choices=value_choices, required=True)

    destination_choices = (
        ('Mbale', 'Mbale'),
        ('Bukedea', 'Bukedea'),
        ('Kumi', 'Kumi'),
        ('Mukura', 'Mukura'),
        ('Soroti', 'Soroti'),
        ('Ngora', 'Ngora'),
        ('Kalaki', 'Kalaki'),
        ('Kaberamaido', 'Kaberamaido'),
        ('Ochero', 'Ochero'),
        ('Namasale', 'Namasale'),
    )
    destination = forms.ChoiceField(choices=destination_choices, required=True)

    receiver_name = forms.CharField(max_length=100, required=True)
    receiver_contact = forms.CharField(max_length=100, required=True)
    delivery_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    delivery_time_choices = (
        ('9am', 'SINAI leaving at 9am'),
        ('11am', 'ZION leaving at 11am'),
        ('2pm', 'SINAI leaving at 2pm'),
        ('4pm', 'OLIVE leaving at 4pm'),
        ('6pm', 'JERICHO (SPECIFICALLY FOR CARGO) leaving at 6pm'),
        ('8pm', 'GALILEE leaving at 8pm'),
        ('10pm', 'JORDAN leaving at 10pm'),
        ('12am', 'CANNAN leaving at 12am'),
        ('2am', 'MOSES leaving at 2am'),
        ('4am', 'KAISARIA leaving at 4am'),
        ('6am', 'EXODUS leaving at 6am'),
        ('8am', 'REVELATION leaving at 8am'),
        ('10am', 'MARANATHA leaving at 10am'),
        ('12pm', 'SALVATION leaving at 12pm'),
        ('2pm', 'CASTA leaving at 2pm'),
        ('4pm', '695 leaving at 4pm'),
    )
    delivery_time = forms.ChoiceField(choices=delivery_time_choices, required=True)

    sender_email = forms.EmailField(required=True)

    tracking_number = forms.CharField(max_length=100, required=True)
    image = forms.ImageField()

    STATUS_CHOICES = (
        ('Delayed', 'Delayed'),
        ('Arrived', 'Arrived'),
        ('Transporting', 'Transporting'),
    )
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=True)

    def save(self, commit=True):
        instance = super(ParcelDetailForm, self).save(commit=False)
        if commit:
            instance.save()

            # Send email with parcel details
            subject = 'Parcel Details Submission'
            message = f'''Your parcel details have been Registered successfully Following --->>>
            
            Parcel Details:
            Description: {instance.description}
            Value: {instance.get_value_display()}
            Destination: {instance.get_destination_display()}
            Receiver Name: {instance.receiver_name}
            Delivery Date: {instance.delivery_date}
            Delivery Time: {instance.get_delivery_time_display()}
            Tracking Number: {instance.tracking_number}
            Status: {instance.get_status_display()}
            '''
            sender = 'enote7y@gmail.com'
            recipient = self.cleaned_data['sender_email']
            send_mail(subject, message, sender, [recipient])

        return instance

    class Meta:
        model = ParcelDetail
        fields = '__all__'



class ParcellDetailForm(forms.ModelForm):
    class Meta:
        model = ParcelDetail
        fields = '__all__'  # Include all fields for editing
