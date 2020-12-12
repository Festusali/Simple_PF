# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


from portfolio.models import (
    UserData, Project, Experience, Certificate, TempUser, Message, UserModel
)


class CreateUserForm(UserCreationForm):
    """Extends UserCreationForm to enable caSe-InseSiTiVe validation of username"""

    def clean(self):
        cleaned_data = super(CreateUserForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        if username and UserModel.objects.filter(username__iexact=username).exists():
            self.add_error('username', 'A user with that username already exists.')
        if email and UserModel.objects.filter(email__iexact=email).exists():
            self.add_error('email', 'Email address already in use. If you are the owner please login instaed or request password reset.')
        
        return cleaned_data
    
    class Meta:
        model = UserModel
        fields = ["username", "email"]


# Register temporal user form
class RegisterUserForm(ModelForm):
    """Form for registering new users"""
    password = forms.CharField(max_length=200, min_length=6, help_text="Choose password", widget=forms.PasswordInput)
    verify_password = forms.CharField(max_length=200, min_length=6, help_text="Confirm password", widget=forms.PasswordInput)
    
    class Meta:
        model = TempUser
        exclude = ["code", "date"]
        
    
    def clean_verify_password(self):
        data = self.cleaned_data["verify_password"]
        user_pass = self.cleaned_data["password"]
        if not data == user_pass:
            raise forms.ValidationError(_("Invalid password: Password and Verify Password didn't match. Please enter the same password in both fields."))
        
        return data


# Verify temporal user form
class VerifyUserForm(forms.Form):
    """Form for verifying temporal user's email."""

    code = forms.IntegerField(
        max_value=999999, min_value=100000, help_text="Verification code"
    )


# Edit user data form
class EditUserDataForm(ModelForm):
    """Form for editing more user data."""
    class Meta:
        model = UserData
        exclude = ["user", "modified", "mod"]


# Edit main/basic user details
class EditUserForm(ModelForm):
    """Form for editing basic user details."""
    class Meta:
        model = UserModel
        fields = ["first_name", "last_name"]
    

# Create project form
class ProjectForm(ModelForm):
    """Form for creating projects"""
    class Meta:
        model = Project
        exclude = ["user"]



# Create experience form
class ExperienceForm(ModelForm):
    """Form for creating new user experience"""
    class Meta:
        model = Experience
        exclude = ["user"]


# Create user certificates
class CertificateForm(ModelForm):
    """Adds user certificate(s)"""
    class Meta:
        model = Certificate
        exclude = ["user"]
    

# Create new message form
class MessageForm(ModelForm):
    """Form for sending message to user."""
    class Meta:
        model = Message
        exclude = ["user"]