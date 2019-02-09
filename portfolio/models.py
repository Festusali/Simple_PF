from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, UserManager

from .tools import pic_path, pro_pho_path



GENDERS = (
    ("M", "Male"),
    ("F", "Female"),
    ("T", "Transgender"),
    ("O", "Other"),
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

    Without this, PORTfolio, Portfolio and portfolio are all different names but with this,
    PortFolio, PORTfolio and portfolio are all the same."""

    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class UserModel(AbstractUser):
    """Swaps the default UserManager to UserModelManager."""

    objects = UserModelManager()


class TempUser(models.Model):
    """Holds temporal user details upon registration while waiting for user email to be confirmed."""
    
    username = models.CharField(unique=True, max_length=120, help_text="Username")
    email = models.EmailField(unique=True, max_length=200, help_text="Valid Email address")
    password = models.CharField(max_length=200,  help_text="Password")
    code = models.IntegerField(unique=True, help_text="Verification code")
    date = models.DateTimeField("Date registered", auto_now_add=True)
    
    
    def __str__(self):
        return self.username



class UserData(models.Model):
    """
    Adds more fields to the user object by allowing to include extra
    required fields.

    This model is just a basic extention of the Default User model.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="user_data", help_text="More user data")
    other_name = models.CharField(max_length=30, help_text="Other names",
        blank=True)
    bio = models.TextField(help_text="About User", max_length=1000, blank=True)
    tags = models.CharField(max_length=255, help_text="#hash tags", blank=True)
    target = models.CharField(max_length=200, help_text="Target Audience/Clients", blank=True)
    action = models.CharField(max_length=200, help_text="Call to action (Convince potential clients)",
        blank=True)
    mod = models.BooleanField(help_text="Is the user a moderator", default=False)
    gender = models.CharField(max_length=2, choices=GENDERS, help_text="Gender", blank=True)
    status = models.CharField(max_length=2, choices=STATUSES,
        help_text="Marital Status", blank=True)
    phone = models.IntegerField(help_text="Mobile Number", blank=True, null=True)
    address = models.CharField(max_length=150, help_text="Contact address", 
        blank=True)
    facebook = models.URLField(help_text="Facebook Account", blank=True)
    twitter = models.URLField(help_text="Twitter Account", blank=True)
    linkedin = models.URLField(help_text="LinkedIn Account", blank=True)
    github = models.URLField(help_text="Github Account", blank=True)
    avatar = models.ImageField(upload_to=pic_path, help_text="Profile Picture",
        blank=True)
    joined = models.DateTimeField(auto_now_add=True, help_text="Join date")
    modified = models.DateTimeField(auto_now=True, help_text="Last modifield")


    def __str__(self):
        return self.user.username

    
    def full_name(self):
        return self.user.get_full_name()+self.other_name or self.user.username

    
    def get_avatar(self):
        try:
            return self.avatar.url
        except:
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

    user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name="project", 
        help_text="User project")
    title = models.CharField(max_length=200, help_text="Short description")
    details = models.TextField(max_length=1000, help_text="Detailed description")
    tags = models.CharField(max_length=200, help_text="Hash tags", blank=True)
    image1 = models.ImageField(upload_to=pro_pho_path, help_text="Project photo",
        blank=True)
    image2 = models.ImageField(upload_to=pro_pho_path, help_text="Project photo",
        blank=True)
    image3 = models.ImageField(upload_to=pro_pho_path, help_text="Project photo",
        blank=True)
    start_date = models.DateField(help_text="Date initiated. In this form; yyyy-mm-dd (i.e, 2018-12-31)", blank=True)
    end_date = models.DateField(help_text="Due/end date. In this form; yyyy-mm-dd (i.e, 2018-12-31)", blank=True)


    def __str__(self):
        return self.title



class Vote(models.Model):
    """Allows for voting user's projects up/down."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE,
        related_name="projet", help_text="Vote project")
    user = models.ForeignKey(UserData, on_delete=models.CASCADE,
        related_name="user_vote", help_text="User Voting")
    vote = models.BooleanField(help_text="Vote up/down")
    date = models.DateField(help_text="Date voted")


    def __str__(self):
        return self.vote



class Certificate(models.Model):
    """Represents certificates acquired by user over time."""

    user = models.ForeignKey(UserData, on_delete=models.CASCADE,
        related_name="certificate", help_text="User certificate")
    title = models.CharField(max_length=200, help_text="Short description")
    detail = models.TextField(max_length=1000, help_text="Long description")
    tags = models.CharField(max_length=200, help_text="Hash tags", blank=True)
    date = models.DateField(help_text="Date acquired", blank=True)


    def __str__(self):
        self.title



class Experience(models.Model):
    """Experience gathered during projects and studies."""

    user = models.ForeignKey(UserData, on_delete=models.CASCADE,
        related_name="experience", help_text="User experience")
    title = models.CharField(max_length=200, help_text="Short description")
    detail = models.TextField(max_length=1000, help_text="Long description")
    tags = models.CharField(max_length=200, help_text="Hash tags", blank=True)
    start_date = models.DateField(help_text="Beginning date", blank=True)
    end_date = models.DateField(help_text="End date", blank=True)


    def __str__(self):
        return self.title



class Message(models.Model):
    """Represents messages received by users.

    Sent messages are not stored anywhere. It is best to use your email server or other dedicated messaging system to send and receive messages."""
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name="messages", help_text="Receiver")
    sender = models.CharField(max_length=100, help_text="Sender")
    email = models.EmailField(help_text="Email address", null=False)
    phone = models.IntegerField(help_text="Phone Number")
    message = models.TextField(max_length=1000, help_text="Message body", null=False)
    date = models.DateTimeField(auto_now_add=True, help_text="Sent date")


    def __str__(self):
        return "Message from: %s"%self.sender
    

@receiver(post_save, sender=UserModel)
def create_userdata(sender, instance, created, **kwargs):
    if created:
        UserData.objects.create(user=instance)
    

@receiver(post_save, sender=UserModel)
def save_userdata(sender, instance, **kwargs):
    instance.user_data.save()

