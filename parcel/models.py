from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.is_active = True  # Automatically activate the user
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=150, unique=True)
    profile_picture = models.ImageField(_('profile picture'), upload_to='profile_pics/', blank=True, null=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    email_confirmed = models.BooleanField(_('email confirmed'), default=False)

    # Updated fields for user types
    is_client = models.BooleanField(_('is client'), default=False)
    is_parcel_staff = models.BooleanField(_('is parcel staff'), default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def is_client_user(self):
        return self.is_client

    def is_parcel_staff_user(self):
        return self.is_parcel_staff



class Client(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='client_profile')
    # Add any additional fields specific to clients

class Parcelstaff(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    # Add any additional fields specific to parcel staff


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ParcelDetail(models.Model):
    client_name = models.ForeignKey(User, on_delete=models.CASCADE)
    client_contact = models.CharField(max_length=15)
    description = models.TextField()
    
    VALUE_CHOICES = (
        ('Fragile', 'Fragile'),
        ('Durable', 'Durable'),
        ('Perishable', 'Perishable'),
    )
    value = models.CharField(max_length=10, choices=VALUE_CHOICES)
    
    DESTINATION_CHOICES = (
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
    destination = models.CharField(max_length=50, choices=DESTINATION_CHOICES)
    
    receiver_name = models.CharField(max_length=100)
    receiver_contact = models.CharField(max_length=15)
    delivery_date = models.DateField()
    
    DELIVERY_TIME_CHOICES = (
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
    delivery_time = models.CharField(max_length=50, choices=DELIVERY_TIME_CHOICES)
    
    sender_email = models.EmailField()
    tracking_number = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='parcel_images/')
    
    STATUS_CHOICES = (
        ('Delayed', 'Delayed'),
        ('Arrived', 'Arrived'),
        ('Transporting', 'Transporting'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return self.tracking_number
