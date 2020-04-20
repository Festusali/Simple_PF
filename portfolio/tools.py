# -*- coding: utf-8 -*-
import random, secrets
from smtplib import SMTPException
from django.core.mail import send_mail, BadHeaderError


# Permissions
def can_modify(request, creator):
    """Returns True if request.user is same as the creator."""
    
    if request.user.is_superuser:
        return True
    elif request.user.id == creator and request.user.is_active:
        return True
    return False


def can_add(request):
    """Returns True if request.user can create new data"""

    if request.user.is_superuser:
        return True
    elif request.user.is_active:
        return True
    return False



# Upload paths
def pic_path(instance, filename):
    """Generates the path where user profile picture will be saved."""

    return "images/users/%s.%s"%(instance.user, filename.split('.')[-1])


def pro_pho_path(instance, filename):
    """Generates the path where user project pictures will be saved."""
    return "images/projects/%s_%s.%s"%(instance.user, 
        filename.split('.')[0], filename.split('.')[-1])


def cert_pho_path(instance, filename):
    """Generates the path where user certificate images will be saved."""
    return "images/certificates/%s_%s.%s"%(instance.user, 
        filename.split('.')[0], filename.split('.')[-1])


def exp_pho_path(instance, filename):
    """Generates the path where user experience images will be saved."""
    return "images/experiences/%s_%s.%s"%(instance.user, 
        filename.split('.')[0], filename.split('.')[-1])




# Random URL safe tokens for email confirmation
def make_token():
    """Generates and returns random token code and URL safe token URL."""
    code = random.randint(100000, 600000)
    token = secrets.token_urlsafe(40)
    
    return {"code": code, "token": token}


# Send confirmation email
def send_confirm_mail(email, username):
    """Constructs and sends confirmation email message to given email address.
    
    All parameters are required.
    
    Upon success, returns token code."""
    token = make_token()
    subject = "Simple Portfolio: Confirm Account Registration"

    body = """Thank you for registering an account with us. \n
    This email address ({email}) was used to register a new account at https://simpleportfolio.pythonanywhere.com/ Simple Portfolio.\n
    Please click this link to confirm your registration http://simpleportfolio.pythonanywhere.com/u/verify/{username}/{token}/{code}/Confirm Email.\n
    Alternatively, if the link above is not clickable, you can visit https://simpleportfolio.pythonanywhere.com/u/verify/{username}/ and enter {code} as your verification code.\n\n
    Note: This link expires automatically in 48hrs and becomes invalid after the specified period.\n
    If you received this mail in error, please disregard it and we will never contact you again.\n
    This is an automatically generated email and hence should not be replied.\n
    If you need further information, please visit https://simpleportfolio.pythonanywhere.com/contact%20us/ or better still send a mail to isfestus@gmail.com.\n\n
    Kind regards,\n
    Simple Portfolio.\n
    """.format(username=username, email=email, token=token["token"], code=token["code"])

    html = """This email address ({email}) was used to register a new account at <a href="https://simpleportfolio.pythonanywhere.com/">Simple Portfolio</a>.<br>
    <p>Please click this link to confirm your registration <a href="http://simpleportfolio.pythonanywhere.com/u/verify/{username}/{token}/{code}/">Confirm Email</a> </p>
    <p>Alternatively, if the link above is not clickable, you can visit https://simpleportfolio.pythonanywhere.com/u/verify/{username}/ and enter <b>{code}</b> as your verification code. </p>
    <p><b>Note:</b> This link expires automatically in 48hrs and becomes invalid after the specified period.</p>
    <p>If you received this mail in error, please disregard it and we will never contact you again.</p>
    <p>This is an automatically generated email and hence should not be replied.<br>
    If you need further information, please visit https://simpleportfolio.pythonanywhere.com/contact%20us/ or better still send a mail to isfestus@gmail.com.</p>
    <p>Kind regards,<br>
    Simple Portfolio.</p>
    """.format(username=username, email=email, token=token["token"], code=token["code"])
    
    try:
        send_mail(subject, body, "isfestus@gmail.com", [email], html_message=html)
    except (SMTPException, BadHeaderError) as e:
        raise e
        
    return token["code"]

    

# Get email domain/server address
def get_email_domain(email):
    """Generates email domain from given email address."""

    return "www."+email.split("@")[-1]


