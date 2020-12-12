from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, UserManager

from .tools import (
    cover_path, pic_path, pro_pho_path, cert_pho_path, exp_pho_path,
    resume_path
)


GENDERS = (
    ("M", "Male"),
    ("F", "Female"),
    ("T", "Transgender"),
    ("O", "Others"),
)


STATUSES = (
    ("M", "Married"),
    ("S", "Single"),
    ("E", "Engaged"),
    ("D", "Divorced"),
    ("O", "Others"),
)


class UserModelManager(UserManager):
    """Extends the UserManager to enable case-insensitive username.

    Without this, PORTfolio, Portfolio and portfolio are all different names
    but with this, PortFolio, PORTfolio and portfolio are all the same."""

    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(
            self.model.USERNAME_FIELD
        )
        return self.get(**{case_insensitive_username_field: username})


class UserModel(AbstractUser):
    """Swaps the default UserManager to UserModelManager."""

    objects = UserModelManager()


class TempUser(models.Model):
    """Temporal user model for registration verification.

    Holds temporal user details upon registration while waiting for user email
    to be confirmed."""

    username = models.CharField(
        unique=True, max_length=120, help_text="Username"
    )
    email = models.EmailField(
        unique=True, max_length=200, help_text="Valid email address"
    )
    password = models.CharField(max_length=200,  help_text="Password")
    code = models.IntegerField(unique=True, help_text="Verification code")
    date = models.DateTimeField("Date registered", auto_now_add=True)

    def __str__(self):
        return self.username


class UserData(models.Model):
    """Extends default user model to include extra fields."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="user_data", help_text="More user data"
    )
    other_name = models.CharField(
        max_length=30, help_text="Other names", blank=True
    )
    bio = models.TextField(
        help_text="About User", max_length=1000, blank=True
    )
    tags = models.CharField(
        max_length=255, help_text="Skills. Seperated by comma", blank=True
    )
    target = models.CharField(
        max_length=200, help_text="Target Audience/Clients", blank=True
    )
    action = models.CharField(
        max_length=200, blank=True,
        help_text="Call to action (Convince potential clients)"
    )
    gender = models.CharField(
        max_length=2, choices=GENDERS, help_text="Gender",  blank=True
    )
    status = models.CharField(
        max_length=2, choices=STATUSES, help_text="Marital Status", blank=True
    )
    phone = models.IntegerField(
        help_text="Mobile number (icluding country code [234 810 0383 180])",
        blank=True, null=True
    )
    address = models.CharField(
        max_length=150, help_text="Contact address",  blank=True
    )
    facebook = models.URLField(help_text="Facebook Account", blank=True)
    twitter = models.URLField(help_text="Twitter Account", blank=True)
    linkedin = models.URLField(help_text="LinkedIn Account", blank=True)
    github = models.URLField(help_text="Github Account", blank=True)
    avatar = models.ImageField(
        upload_to=pic_path, help_text="Profile Picture", blank=True
    )
    cover_image = models.ImageField(
        upload_to=cover_path, help_text="Cover Image",  blank=True
    )
    resume = models.FileField(
        upload_to=resume_path, help_text="Upload Your Resume", blank=True
    )
    modified = models.DateTimeField(auto_now=True, help_text="Last modifield")

    def __str__(self):
        return self.user.username

    def full_name(self):
        full_name = (
            self.user.first_name + " " + self.other_name + " " +
            self.user.last_name
        ).strip()
        if full_name:
            return full_name
        else:
            return self.user.username

    def get_avatar(self):
        try:
            return self.avatar.url
        except ValueError:
            return None

    def get_cover(self):
        try:
            return self.cover_image.url
        except ValueError:
            return None

    def get_projects(self):
        return Project.objects.filter(user=self.id) or []

    def get_certificates(self):
        return Certificate.objects.filter(user=self.id) or []

    def get_experiences(self):
        return Experience.objects.filter(user=self.id) or []

    def get_messages(self):
        return Message.objects.filter(user=self.id) or []


class Project(models.Model):
    """A representation of user's projects. Completed or Initiated."""

    user = models.ForeignKey(
        UserData, on_delete=models.CASCADE,  related_name="project",
        help_text="User project"
    )
    title = models.CharField(max_length=200, help_text="Short description")
    detail = models.TextField(
        max_length=1000, help_text="Detailed description"
    )
    tags = models.CharField(
        max_length=200, help_text="Hash tags. Seperated by comma", blank=True
    )
    image1 = models.ImageField(
        upload_to=pro_pho_path, help_text="Project photo", blank=True
    )
    image1_desc = models.CharField(
        max_length=150, help_text='Image one description', blank=True
    )
    image2 = models.ImageField(
        upload_to=pro_pho_path, help_text="Project photo", blank=True
    )
    image2_desc = models.CharField(
        max_length=150, help_text='Image two description', blank=True
    )
    image3 = models.ImageField(
        upload_to=pro_pho_path, help_text="Project photo", blank=True
    )
    image3_desc = models.CharField(
        max_length=150, help_text='Image three description', blank=True
    )
    start_date = models.DateField(
        help_text="Date initiated. In the form: yyyy-mm-dd (i.e, 2018-12-31)",
        blank=True
    )
    end_date = models.DateField(
        help_text="Due/end date. In the form;:yyyy-mm-dd (i.e, 2018-12-31)",
        blank=True
    )

    def __str__(self):
        return self.title


class Certificate(models.Model):
    """Represents certificates acquired by user."""

    user = models.ForeignKey(
        UserData, on_delete=models.CASCADE, related_name="certificate",
        help_text="User certificate"
    )
    title = models.CharField(max_length=200, help_text="Short description")
    detail = models.TextField(max_length=1000, help_text="Long description")
    tags = models.CharField(
        max_length=200, help_text="Hash tags. Seperated by comma", blank=True
    )
    image = models.ImageField(
        upload_to=cert_pho_path, help_text="Certificate image", blank=True
    )
    image_desc = models.CharField(
        max_length=150, help_text='Image description', blank=True
    )
    date = models.DateField(help_text="Date acquired", blank=True)
    end_date = models.DateField(
        help_text="Certificate end date", blank=True, null=True
    )

    def __str__(self):
        return self.title


class Experience(models.Model):
    """Experience gathered during projects and studies."""

    user = models.ForeignKey(
        UserData, on_delete=models.CASCADE, related_name="experience",
        help_text="User experience"
    )
    title = models.CharField(max_length=200, help_text="Short description")
    detail = models.TextField(max_length=1000, help_text="Long description")
    tags = models.CharField(
        max_length=200, help_text="Hash tags. Seperated by comma", blank=True
    )
    image = models.ImageField(
        upload_to=exp_pho_path, help_text="Experience photo", blank=True
    )
    image_desc = models.CharField(
        max_length=150, help_text='Image description', blank=True
    )
    start_date = models.DateField(help_text="Beginning date", blank=True)
    end_date = models.DateField(help_text="End date", blank=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    """Represents message received by user.

    Sent messages are stored in user private inbox which may not be safe and a
    copy forwarded to user registered email address. Therefore, It is best to
    use your email provider or other dedicated messaging system to send and
    receive messages."""

    user = models.ForeignKey(
        UserData, on_delete=models.CASCADE, related_name="messages",
        help_text="Receiver"
    )
    sender = models.CharField(max_length=100, help_text="Your name")
    email = models.EmailField(help_text="Email address", null=False)
    phone = models.IntegerField(help_text="Phone Number")
    message = models.TextField(
        max_length=1000, help_text="Message body", null=False
    )
    date = models.DateTimeField(auto_now_add=True, help_text="Sent date")

    def __str__(self):
        return "Message from: %s" % self.sender


@receiver(post_save, sender=UserModel)
def create_userdata(sender, instance, created, **kwargs):
    if created:
        UserData.objects.create(user=instance)


@receiver(post_save, sender=UserModel)
def save_userdata(sender, instance, **kwargs):
    instance.user_data.save()
