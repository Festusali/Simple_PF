from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse, get_object_or_404

from portfolio.models import (
    UserData, Project, Experience, Certificate, Message, TempUser, UserModel
)
from portfolio.forms import (
    CreateUserForm, VerifyUserForm, EditUserDataForm, EditUserForm,
    ProjectForm, ExperienceForm, CertificateForm, MessageForm
)

from portfolio.tools import (
    can_modify, can_add, send_confirm_mail
)


def index(request):
    """Return the contents of the home page."""
    return render(request, "portfolio/index.html", {})


def profile(request, username):
    """Returns information about given user or raises HTTP Error 404."""

    userdata = get_object_or_404(UserData, user__username__iexact=username)
    msg_form = MessageForm()
    return render(request, "portfolio/profile.html", {
        'userdata': userdata, "msg_form": msg_form
    })


@login_required
def edit_profile(request, username):
    """Modifies user data and redirects to user profile upon success."""

    user = get_object_or_404(UserModel, username__iexact=username)
    userdata = user.user_data

    if not can_modify(request, user.id):
        raise PermissionDenied

    if request.method == "POST":
        form1 = EditUserForm(request.POST, instance=user)
        form2 = EditUserDataForm(
            request.POST, request.FILES, instance=userdata
        )
        if form1.is_valid() and form2.is_valid():
            form1.save()
            form2.save()
            return redirect("profile", username=user)
    else:
        form1 = EditUserForm(instance=user)
        form2 = EditUserDataForm(instance=userdata)

    return render(request, "portfolio/edit_profile.html", context={
        "form1": form1, "form2": form2, "userdata": userdata
    })


def register(request):
    """Registers new user into the temporal user model."""

    if request.method == 'POST':
        # Create new temporal user.
        form = CreateUserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            code = send_confirm_mail(data.get('email'), data.get('username'))
            if code:
                new_user = TempUser.objects.create(
                    username=data.get('username'), email=data.get('email'),
                    password=data.get('password1'), code=code
                )
                return redirect(reverse("verify_user", kwargs={
                    "username": new_user.username
                }))
    else:
        form = CreateUserForm()
    return render(request, "portfolio/register.html", {"form": form})


def verify_user(request, username):
    """This view manually verifies temporal user.

    If the verification is successful, the user will be registered into the
    main user table."""

    try:
        user = TempUser.objects.get(username__iexact=username)
    except TempUser.DoesNotExist:
        return render(request, "portfolio/verify_user.html", {
            "user_error": True
        })
    if request.method == 'POST':
        form = VerifyUserForm(request.POST)
        if form.is_valid():
            if int(form.cleaned_data.get("code")) != user.code:
                return render(request, "portfolio/verify_user.html", {
                    "form": form, "code_error": True
                })
            new_user = UserModel.objects.create_user(
                user.username, user.email, user.password
            )
            user.delete()
            return redirect(
                f"{settings.LOGIN_URL}?next=/user/{new_user.username}/"
            )
    else:
        form = VerifyUserForm()
    return render(request, "portfolio/verify_user.html", {"form": form})


def auto_verify(request, username, token, code):
    """Automatic verification of temporal user.

    If verification fails, the user is automatically redirected to manual
    verification page."""

    try:
        user = TempUser.objects.get(username__iexact=username)
    except TempUser.DoesNotExist:
        return render(request, "portfolio/verify_user.html", {
            "user_error": True
        })
    if int(code) == user.code:
        new_user = UserModel.objects.create_user(
            user.username, user.email, user.password
        )
        user.delete()
        return redirect(
            f"{settings.LOGIN_URL}?next=/user/{new_user.username}/"
        )
    else:
        return redirect("verify_user", username=user.username)


@login_required
def add_project(request, username):
    """Adds new project."""

    userdata = get_object_or_404(
        UserData, user=UserModel.objects.get(username__iexact=username)
    )
    if not can_add(request):
        raise PermissionDenied
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = userdata
            project.save()
            form.save_m2m()
            return redirect(
                f"""{reverse(
                    'projects', kwargs={'username': userdata}
                )}#pro-{project.pk}"""
            )
    else:
        form = ProjectForm()
    return render(request, "portfolio/add.html", context={
        "form": form, "userdata": userdata, "btn_value": "Create Project",
        "title": "Create New Project",
        "desc": "Use the form below to add new project you worked/working on "
        "to include it in your portfolio."
    })


def projects(request, username):
    """Returns list of user projects.

    Makes use of get_projects() method of Userdata model instead of accessing
    projects directly."""

    userdata = get_object_or_404(
        UserData, user=UserModel.objects.get(username__iexact=username)
    )
    projects = userdata.get_projects()
    return render(request, "portfolio/projects.html", {
        "userdata": userdata, "projects": projects
    })


@login_required
def edit_project(request, pk):
    """View for modifying given project."""

    project = get_object_or_404(Project, pk=pk)
    userdata = project.user

    if not can_modify(request, project.user.id):
        raise PermissionDenied
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect(
                f"""{reverse(
                    'projects', kwargs={'username': userdata}
                )}#pro-{project.pk}"""
            )
    else:
        form = ProjectForm(instance=project)
    return render(request, "portfolio/add.html", context={
        "form": form, "userdata": userdata, "title": "Edit Project",
        "desc": f"Modify this project; {project.title}",
        "btn_value": "Save Changes"
    })


@login_required
def del_project(request, pk):
    """Deletes giving project."""

    project = get_object_or_404(Project, pk=pk)

    if not can_modify(request, project.user.id):
        raise PermissionDenied

    if request.method == "POST":
        project.delete()
        return redirect("projects", request.user)
    return render(request, "portfolio/confirm.html", context={
        "title": "Delete Project", "userdata": project.user,
        "desc": "You are about to delete this project with title: <strong>"
        f"{project.title}</strong>. Proceed?", "btn_value": "Yes Delete!"
    })


@login_required
def add_experience(request, username):
    """Adds new user experience."""

    userdata = get_object_or_404(
        UserData, user=UserModel.objects.get(username__iexact=username)
    )
    if not can_add(request):
        raise PermissionDenied
    if request.method == "POST":
        form = ExperienceForm(request.POST, request.FILES)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = userdata
            exp.save()
            form.save_m2m()
            return redirect(
                f"""{reverse(
                    'experiences', kwargs={'username': userdata}
                )}#exp-{exp.pk}"""
            )
    else:
        form = ExperienceForm()
    return render(request, "portfolio/add.html", context={
        "form": form, "userdata": userdata, "btn_value": "Add Experience",
        "title": "Add New Experience",
        "desc": "Use the form below to add (new) experience you acquired to "
        "include it in your portfolio."
    })


def experiences(request, username):
    """Returns list of user experiences.

    Makes use of get_experiences() method of Userdata model instead of
    accessing experiences directly."""

    userdata = get_object_or_404(
        UserData, user=UserModel.objects.get(username__iexact=username)
    )
    experiences = userdata.get_experiences()
    return render(request, "portfolio/experiences.html", {
        "userdata": userdata, "experiences": experiences
    })


@login_required
def edit_experience(request, pk):
    """View for modifying given experience."""

    exp = get_object_or_404(Experience, pk=pk)
    userdata = exp.user

    if not can_modify(request, exp.user.id):
        raise PermissionDenied
    if request.method == "POST":
        form = ExperienceForm(request.POST, request.FILES, instance=exp)
        if form.is_valid():
            form.save()
            return redirect(
                f"""{reverse(
                    'experiences', kwargs={'username': userdata}
                )}#exp-{exp.pk}"""
            )
    else:
        form = ExperienceForm(instance=exp)
    return render(request, "portfolio/add.html", context={
        "form": form, "userdata": userdata, "title": "Edit Experience",
        "desc": f"Modify this experience; {exp.title}",
        "btn_value": "Save Changes"
    })


@login_required
def del_experience(request, pk):
    """Deletes giving experience."""

    exp = get_object_or_404(Experience, pk=pk)

    if not can_modify(request, exp.user.id):
        raise PermissionDenied

    if request.method == "POST":
        exp.delete()
        return redirect("experiences", request.user)

    return render(request, "portfolio/confirm.html", context={
        "title": "Delete Experience", "userdata": exp.user,
        "desc": "You are about to delete this experience with title: "
        f"<strong>{exp.title}</strong>. Proceed?", "btn_value": "Yes Delete!"
    })


@login_required
def add_certificate(request, username):
    """Adds new user certificate."""

    userdata = get_object_or_404(
        UserData, user=UserModel.objects.get(username__iexact=username)
    )
    if not can_add(request):
        raise PermissionDenied
    if request.method == "POST":
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.user = userdata
            cert.save()
            form.save_m2m()
            return redirect(
                f"""{reverse(
                    'certificates', kwargs={'username': userdata}
                )}#cert-{cert.pk}"""
            )
    else:
        form = CertificateForm()
    return render(request, "portfolio/add.html", context={
        "form": form, "userdata": userdata, "btn_value": "Add Certificate",
        "title": "Add New Certificate",
        "desc": "Use the form below to add (new) certificate you acquired to "
        "include them in your portfolio."
    })


def certificates(request, username):
    """Returns list of user crtificates.

    Makes use of get_certificates() method of Userdata model instead of
    accessing certificates directly."""

    userdata = get_object_or_404(
        UserData, user=UserModel.objects.get(username__iexact=username)
    )
    certificates = userdata.get_certificates()
    return render(request, "portfolio/certificates.html", {
        "userdata": userdata, "certificates": certificates
    })


@login_required
def edit_certificate(request, pk):
    """View for modifying given certificate."""

    cert = get_object_or_404(Certificate, pk=pk)
    userdata = cert.user

    if not can_modify(request, cert.user.id):
        raise PermissionDenied
    if request.method == "POST":
        form = CertificateForm(request.POST, request.FILES, instance=cert)
        if form.is_valid():
            form.save()
            return redirect(
                f"""{reverse(
                    'certificates', kwargs={'username': userdata}
                )}#cert-{cert.pk}"""
            )
    else:
        form = CertificateForm(instance=cert)
    return render(request, "portfolio/add.html", context={
        "form": form, "userdata": userdata, "title": "Edit Certificate",
        "desc": f"Modify this certificate; {cert.title}",
        "btn_value": "Save Changes"
    })


@login_required
def del_certificate(request, pk):
    """Deletes giving certificate."""

    cert = get_object_or_404(Certificate, pk=pk)

    if not can_modify(request, cert.user.id):
        raise PermissionDenied

    if request.method == "POST":
        cert.delete()
        return redirect("certificates", request.user)
    return render(request, "portfolio/confirm.html", context={
        "title": "Delete Certificate", "userdata": cert.user,
        "desc": "You are about to delete this certificate with title: "
        f"<strong>{cert.title}</strong>. Proceed?", "btn_value": "Yes Delete!"
    })


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
    """Sends message to system administrator."""

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            send_mail(
                f"Simple Portfolio: New Message From {data.get('sender')}",
                f"{data.get('sender')} with phone number: "
                f"{data.get('phone')} said:\n\n{data.get('message')}",
                data.get('email'), ["isfestus@gmail.com"]
            )
            return redirect("message_sent")
    else:
        form = MessageForm()
    return render(request, "portfolio/contact.html", {"form": form})


@login_required
def messages(request, username):
    """Returns user messages.

    Uses get_messages() method of Userdata model instead of accessing
    messages directly."""

    userdata = get_object_or_404(
        UserData, user=UserModel.objects.get(username__iexact=username)
    )
    if not can_modify(request, userdata.id):
        raise PermissionDenied
    messages = userdata.get_messages()
    return render(request, "portfolio/messages.html", context={
        "userdata": userdata, "messages": messages
    })


@login_required
def del_message(request, pk):
    """Deletes giving message."""

    msg = get_object_or_404(Message, pk=pk)

    if not can_modify(request, msg.user.id):
        raise PermissionDenied

    if request.method == "POST":
        msg.delete()
        return redirect("messages", request.user)

    return render(request, "portfolio/confirm.html", context={
        "title": "Delete Message?", "userdata": msg.user,
        "desc": "You are about to delete this message from: <strong>"
        f"{msg.sender}</strong>. Proceed?", "btn_value": "Yes Delete!"
    })


def message(request, username):
    """Sends a message to given user."""

    userdata = get_object_or_404(
        UserData, user=UserModel.objects.get(username__iexact=username)
    )

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = userdata
            message.save()
            send_mail(
                f"Simple Portfolio: {message.sender} Sent A Mail.",
                f"""{message.sender} with phone number: {message.phone} Sent
                You A Mail.\n\n{message.message}""", message.email,
                [userdata.user.email]
            )
            return redirect(f"{reverse('message_sent')}?user_id={userdata}")
    else:
        form = MessageForm()
    return render(request, "portfolio/add.html", context={
        "form": form, "userdata": userdata, "btn_value": "Message Me",
        "title": f"send Message To {userdata}",
        "desc": f"Send {userdata} a message"
    })


def message_sent(request):
    """Shows success message after sending message."""

    return render(request, "portfolio/message_sent.html", {
        "userdata": request.GET.get("user_id", False)
    })
