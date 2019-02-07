from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),


    path('privacy policy/', views.privacy, name='privacy'),
    path('about/', views.about, name='about'),
    path('disclaimer/', views.disclaimer, name="disclaimer"),
    path('contact us/', views.contact, name="contact"),

    
    path('u/', include('django.contrib.auth.urls')),
    path('u/register/', views.register, name="register"),
    path('u/verify/<username>/', views.verify_user, name="verify_user"),
    path('u/verify/<username>/<slug:token>/<int:code>/', views.auto_verify,
        name="auto_verify"),
    
    
    path('user/<username>/', views.profile, name='profile'),
    path('user/<username>/<int:basic>/edit/', views.edit_profile, name='edit_profile'),


    path('user/<username>/projects/', views.projects, name='projects'),
    path('user/<username>/projects/add/', views.add_project, name='add_project'),
    path('projects/<int:pk>/', views.project, name='project'),
    path('projects/<int:pk>/edit/', views.edit_project, name='edit_project'),
    path('projects/<int:pk>/delete/', views.del_project, name='del_project'),


    path('user/<username>/experiences/', views.experiences, name='experiences'),
    path('user/<username>/experiences/add/', views.add_experience, name='add_experience'),
    path('experiences/<int:pk>/', views.experience, name='experience'),
    path('experiences/<int:pk>/edit/', views.edit_experience, name='edit_experience'),
    path('experiences/<int:pk>/delete/', views.del_experience, name='del_experience'),
    

    path('user/<username>/certificates/', views.certificates, name='certificates'),
    path('user/<username>/certificates/add/', views.add_experience, name='add_certificate'),
    path('certificates/<int:pk>/', views.certificate, name='certificate'),
    path('certificates/<int:pk>/edit/', views.edit_certificate, name='edit_certificate'),
    path('certificates/<int:pk>/delete/', views.del_certificate, name='del_certificate'),
    

    path('user/<username>/messages/', views.messages, name="messages"),
    path('message/<username>/', views.message, name="message"),
    path('messages/<int:pk>/delete/', views.del_message, name="del_message"),
    path('message sent/', views.message_sent, name="message_sent"),

    
    #
]