from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404, Http404




from .models import UserData, Project, Experience, Certificate, Message, TempUser, UserModel
from .forms import CreateUserForm, VerifyUserForm, EditUserDataForm, EditUserForm, ProjectForm, ExperienceForm, CertificateForm, MessageForm

from .tools import can_modify, can_add, send_confirm_mail, get_email_domain


def index(request):
    """Return the contents of the home page."""
    return render(request, "portfolio/index.html", {})



def profile(request, username):
    """Returns information about the user specified by username or raises HTTP Error 404
    if no matching user were found. The username must be of type int."""
    
    userdata = get_object_or_404(UserData, user__username__iexact=username)# UserModel.objects.get(username__iexact=username))
    msg_form = MessageForm()
    return render(request, "portfolio/profile.html", {'userdata': userdata, "msg_form": msg_form})


@login_required
def edit_profile(request, username, basic):
    """Modifies user data and redirects to user profile upon success."""
    if basic:
        user = get_object_or_404(UserModel, username__iexact=username)
        form = EditUserForm(instance=user)
    else:
        user = get_object_or_404(UserData, user__username__iexact=username)# =UserModel.objects.get(username__iexact=username))
        form = EditUserDataForm(instance=user)
    
    if not can_modify(request, user.id):
        return render(request, 'portfolio/perm.html', {"perm": "Sorry but you can't edit profile of another user"})
    
    elif request.method == "POST":
        if basic:
            form = EditUserForm(request.POST, instance=user)
        elif not basic:
            form = EditUserDataForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("profile", username=user)
    
    return render(request, "portfolio/edit_profile.html", {"form": form, "basic": basic})


def register(request):
    """Registers new user into the temporal user model."""
    #If POST request method.
    if request.method == 'POST':
        #Create a new temporal user.
        form = CreateUserForm(request.POST)
        if form.is_valid(): # Is all field valid?
            data = form.cleaned_data
            code = send_confirm_mail(data.get('email'), data.get('username'))
            if not code: return HttpResponse('<h1>We are unable to mail you confirmation code.<br>' + 
                'Did you enter a valid email address? if so, please try re-registering.</h1>')
            new_user = TempUser.objects.create(username=data.get('username'), email=data.get('email'), password=data.get('password1'), code=code)
            
            return render(request, "portfolio/register.html", {"domain": get_email_domain(new_user.email), "code": code})
    
    else:
        form = CreateUserForm() #Create empty temporal user form
    return render(request, "portfolio/register.html", {"form": form})
        

def verify_user(request, username):
    """This view manually verifies temporal user before registering the account into the main database."""
    try:
        user = TempUser.objects.get(username__iexact=username)
    except:
        return render(request, "portfolio/verify_user.html", {"username": username, "user_error": True, })
    if request.method == 'POST':
        form = VerifyUserForm(request.POST, instance=user)
        if form.is_valid():
            if not form.cleaned_data["code"] == user.code:
                return render(request, "portfolio/verify_user.html", {"username": username, "code_error": True, })
            
            new_user = UserModel.objects.create_user(user.username, user.email, user.password)
            #UserData.objects.create(user=new_user)
            user.delete()
            
            return redirect('%s?next=/user/%s/' %(settings.LOGIN_URL, new_user.username))
        
    else:
        form = VerifyUserForm()
        return render(request, "portfolio/verify_user.html", {"form": form, "username": username})


def auto_verify(request, username, token, code):
    """Automatic verification of temporal user before registering into main database.
    
    If verification fails, the user is automatically redirected to manual verification page."""
    try:
        user = TempUser.objects.get(username__iexact=username)
    except:
        return render(request, "portfolio/verify_user.html", {"username": username, "user_error": True, })
    if int(code) == user.code:
        new_user = UserModel.objects.create_user(user.username, user.email, user.password)
        #UserData.objects.create(user=new_user)
        user.delete()
        
        return redirect('%s?next=/user/%s/' %(settings.LOGIN_URL, new_user.username))
        
    else:
        return redirect("verify_user", username=new_user.username)




@login_required
def add_project(request, username):
    """Adds new project."""
    userdata = get_object_or_404(UserData, user=UserModel.objects.get(username__iexact=username))
    if not can_add(request):
        return render(request, "portfolio/perm.html", {"perm": "You don't have required permissions to add new projects."})
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = userdata
            project.save()
            form.save_m2m()
            
            return redirect("projects", username=userdata)
        
        return render(request, "portfolio/add.html", {"form": form, "btn_value": "Create Project", "title": "Create New Project", "desc": "Use the form below to add new project you worked/working on to include it in your portfolio."})
    
    form = ProjectForm()
    return render(request, "portfolio/add.html", {"form": form, "btn_value": "Create Project", "title": "Create New Project", "desc": "Use the form below to add new project you worked/working on to include it in your portfolio."})


def projects(request, username):
    """Returns list of user projects.
    
    It makes use of get_projects() method of Userdata model instead of accessing projects directly."""
    
    userdata = get_object_or_404(UserData, user=UserModel.objects.get(username__iexact=username))
    projects = userdata.get_projects()
    return render(request, "portfolio/projects.html", {"userdata": userdata, "projects": projects})


def project(request, pk):
    return render(request, "portfolio/NI.html", {})


@login_required
def edit_project(request, pk):
    """View for modifying given project."""
    project = get_object_or_404(Project, pk=pk)
    
    if not can_modify(request, project.user.id):
        return render(request, "portfolio/perm.html", {"perm": "You don't have permission to edit project of another user"})
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects", username=project.user)

        return render(request, "portfolio/add.html", {"form": form, "title": "Edit Project", "desc": "Modify this project; %s"%project.title, "btn_value": "Save Changes"})
    form = ProjectForm(instance=project)
    return render(request, "portfolio/add.html", {"form": form, "title": "Edit Project", "desc": "Modify this project; %s"%project.title, "btn_value": "Save Changes"})


@login_required
def del_project(request, pk):
    """Deletes giving project."""
    project = get_object_or_404(Project, pk=pk)

    if not can_modify(request, project.user.id):
        return render(request, "portfolio/perm.html", {"perm": "You don't have permission to delete project of another user"})
    
    if request.method == "POST":
        project.delete()
        return redirect("projects", request.user)
    return render(request, "portfolio/confirm.html", {"title": "Delete Project", "desc": "You are about to delete this project with title: <strong>%s</strong>. Proceed?"%project.title, "btn_value": "Yes Delete!"})



@login_required
def add_experience(request, username):
    """Adds new user experience."""
    userdata = get_object_or_404(UserData, user=UserModel.objects.get(username__iexact=username))
    if not can_add(request):
        return render(request, "portfolio/perm.html", {"perm": "You don't have required permissions to add an experience."})
    if request.method == "POST":
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = userdata
            exp.save()
            form.save_m2m()
            
            return redirect("experiences", username=userdata)
        
        return render(request, "portfolio/add.html", {"form": form, "btn_value": "Add Experience", "title": "Add New Experience", "desc": "Use the form below to add (new) experience you gathered to include it in your portfolio."})
    
    form = ExperienceForm()
    return render(request, "portfolio/add.html", {"form": form, "btn_value": "Add Experience", "title": "Add New Experience", "desc": "Use the form below to add (new) experience you gathered to include it in your portfolio."})


def experiences(request, username):
    """Returns list of user experiences.
    
    It makes use of get_experiences() method of Userdata model instead of accessing experiences directly."""
    
    userdata = get_object_or_404(UserData, user=UserModel.objects.get(username__iexact=username))
    experiences = userdata.get_experiences()
    return render(request, "portfolio/experiences.html", {"userdata": userdata, "experiences": experiences})


def experience(request, pk):
    return render(request, "portfolio/NI.html", {})


@login_required
def edit_experience(request, pk):
    """View for modifying given experience."""
    exp = get_object_or_404(Experience, pk=pk)
    
    if not can_modify(request, exp.user.id):
        return render(request, "portfolio/perm.html", {"perm": "You don't have permission to edit experience of another user"})
    if request.method == "POST":
        form = ExperienceForm(request.POST, instance=exp)
        if form.is_valid():
            form.save()
            return redirect("experiences", username=exp.user)

        return render(request, "portfolio/add.html", {"form": form, "title": "Edit Experience", "desc": "Modify this experience; %s"%exp.title, "btn_value": "Save Changes"})
    form = ExperienceForm(instance=exp)
    return render(request, "portfolio/add.html", {"form": form, "title": "Edit Experience", "desc": "Modify this experience; %s"%exp.title, "btn_value": "Save Changes"})


@login_required
def del_experience(request, pk):
    """Deletes giving experience."""
    exp = get_object_or_404(Experience, pk=pk)

    if not can_modify(request, exp.user.id):
        return render(request, "portfolio/perm.html", {"perm": "You don't have permission to delete experience of another user"})
    
    if request.method == "POST":
        exp.delete()
        return redirect("experiences", request.user)
    return render(request, "portfolio/confirm.html", {"title": "Delete Experience", "desc": "You are about to delete this experience with title: <strong>%s</strong>. Proceed?"%exp.title, "btn_value": "Yes Delete!"})



@login_required
def add_certificate(request, username):
    """Adds new user certificate."""
    userdata = get_object_or_404(UserData, user=UserModel.objects.get(username__iexact=username))
    if not can_add(request):
        return render(request, "portfolio/perm.html", {"perm": "You don't have required permissions to add certificates."})
    if request.method == "POST":
        form = CertificateForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.user = userdata
            cert.save()
            form.save_m2m()
            
            return redirect("certificates", username=userdata)
        
        return render(request, "portfolio/add.html", {"form": form, "btn_value": "Add Certificate", "title": "Add New Certificate", "desc": "Use the form below to add (new) certificate you acquired to include them in your portfolio."})
    
    form = ExperienceForm()
    return render(request, "portfolio/add.html", {"form": form, "btn_value": "Add Certificate", "title": "Add New Certificate", "desc": "Use the form below to add (new) certificate you acquired to include them in your portfolio."})


def certificates(request, username):
    """Returns list of user crtificates.
    
    It makes use of get_certificates() method of Userdata model instead of accessing certificates directly."""
    
    userdata = get_object_or_404(UserData, user=UserModel.objects.get(username__iexact=username))
    certificates = userdata.get_certificates()
    return render(request, "portfolio/certificates.html", {"userdata": userdata, "certificates": certificates})


def certificate(request, pk):
    return render(request, "portfolio/NI.html", {})


@login_required
def edit_certificate(request, pk):
    """View for modifying given certificate."""
    cert = get_object_or_404(Certificate, pk=pk)
    
    if not can_modify(request, cert.user.id):
        return render(request, "portfolio/perm.html", {"perm": "You don't have permission to edit certificate of another user"})
    if request.method == "POST":
        form = CertificateForm(request.POST, instance=cert)
        if form.is_valid():
            form.save()
            return redirect("certificates", username=cert.user)

        return render(request, "portfolio/add.html", {"form": form, "title": "Edit Certificate", "desc": "Modify this certificate; %s"%cert.title, "btn_value": "Save Changes"})
    form = CertificateForm(instance=cert)
    return render(request, "portfolio/add.html", {"form": form, "title": "Edit Certificate", "desc": "Modify this certificate; %s"%cert.title, "btn_value": "Save Changes"})


@login_required
def del_certificate(request, pk):
    """Deletes giving certificate."""
    cert = get_object_or_404(Certificate, pk=pk)

    if not can_modify(request, cert.user.id):
        return render(request, "portfolio/perm.html", {"perm": "You don't have permission to delete certificate of another user"})
    
    if request.method == "POST":
        cert.delete()
        return redirect("certificates", request.user)
    return render(request, "portfolio/confirm.html", {"title": "Delete Certificate", "desc": "You are about to delete this certificate with title: <strong>%s</strong>. Proceed?"%cert.title, "btn_value": "Yes Delete!"})



def privacy(request):
    """Returns privacy policy statement."""
    return render(request, "portfolio/privacy.html", {})


def about(request):
    """Returns about information."""
    return render(request, "portfolio/about.html", {})


def disclaimer(request):
    """Returns disclaimer statement."""
    return render(request, "portfolio/disclaimer.html", {})


def contact(request):
    """Return the contact form for messaging administrator."""
    form = MessageForm()
    return render(request, "portfolio/contact.html", {"form": form})



@login_required
def messages(request, username):
    """Returns user messages.
    
    It makes use of get_messages() method of Userdata model instead of accessing messages directly."""
    
    userdata = get_object_or_404(UserData, user=UserModel.objects.get(username__iexact=username))
    if not can_modify(request, userdata.id):
        return render(request, "portfolio/perm.html", {"perm": "You don't have permission to view another user's messages"})
    messages = userdata.get_messages()
    return render(request, "portfolio/messages.html", {"userdata": userdata, "messages": messages})


@login_required
def del_message(request, pk):
    """Deletes giving message."""
    msg = get_object_or_404(Message, pk=pk)

    if not can_modify(request, msg.user.id):
        return render(request, "portfolio/perm.html", {"perm": "You don't have permission to delete another user's message."})
    
    if request.method == "POST":
        msg.delete()
        return redirect("messages", request.user)
    return render(request, "portfolio/confirm.html", {"title": "Delete Message?", "desc": "You are about to delete this message from: <strong>%s</strong>. Proceed?"%msg.sender, "btn_value": "Yes Delete!"})


def message(request, username):
    """Sends a message to site admin or given user."""
    
    userdata = get_object_or_404(UserData, user=UserModel.objects.get(username__iexact=username))

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = userdata
            message.save()
            send_mail("Simple Portfolio: %s Sent A Mail."%message.sender,
                "%s with phone number: %s Sent You A Mail\n<br> %s"%(message.sender,
                message.phone, message.message), message.email, [userdata.user.email,], 
                fail_silently=True)

            return redirect("message_sent")

        return render(request, "portfolio/add.html", {"form": form, "btn_value": "Message Me", 
            "title": "send Message To %s"%userdata, "desc": "Send %s a message"%userdata})

    form = MessageForm()
    return render(request, "portfolio/add.html", {"form": form, "btn_value": "Message Me", 
            "title": "send Message To %s"%userdata, "desc": "Send %s a message"%userdata})


def message_sent(request):
    """Shows success message after sending message."""
    return render(request, "portfolio/message_sent.html", {})

