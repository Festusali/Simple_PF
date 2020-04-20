import datetime

from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.test import RequestFactory, TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Project, UserData, UserModel
from .views import projects, add_project



"""
class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

    def test_details(self):
        # Create an instance of a GET request.
        request = self.factory.get('/customer/details')

        # Recall that middleware are not supported. You can simulate a
        # logged-in user by setting request.user manually.
        request.user = self.user

        # Or you can simulate an anonymous user by setting request.user to
        # an AnonymousUser instance.
        request.user = AnonymousUser()

        # Test my_view() as if it were deployed at /customer/details
        response = my_view(request)
        # Use this syntax for class-based views.
        response = MyView.as_view()(request)
        self.assertEqual(response.status_code, 200)
"""

class ProjectViewTests(TestCase):
    """
    Test that projects are created and only by logged in users.
    """
    def setUp(self):
        """Set up all things necessary for the test to pass or fail."""
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = UserModel.objects.create_user(
            username='portfolio', email='port@folio', password='port_secret')

    def new_project(self, user, title, details, start_date="2018-12-31",
            end_date="2019-01-15"):
        """
        Create a project with the given parameters.
        """
        return Project.objects.create(user=user, title=title, details=details,
            start_date=start_date, end_date=end_date)

    def test_no_projects(self):
        """
        If no projects exist, an appropriate message is displayed.
        """
        response = self.client.get('/user/%s/projects/'%self.user.username)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Projects")

    def test_loggedin_can_add_project(self):
        """
        Test that adding new question by logged in user passess.
        AnonymousUser must be redirected to login page.
        """
        # Create an instance of a GET request.
        request = self.factory.get("/")

        # Set request.user to instance of AnonymousUser.
        request.user = AnonymousUser()
        # Try to access login protected view to verify it redirects to login_url.
        response = self.client.get('/user/portfolio/projects/add/', follow=True)
        self.assertRedirects(response,
            '/u/login/?next=%2Fuser%2Fportfolio%2Fprojects%2Fadd%2F')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login to your Account")

        # Log in user manually in the absence of middleware.
        request.user = self.user

        # Test add_project() view can be accessed by logged in user.
        response = add_project(request, username=self.user)
        self.assertEqual(response.status_code, 200)
        
        # add new project by currently logged in user.
        response = self.new_project(self, user=self.user.user_data,
            title='My Project.', details='This is my project')
        #response = self.client.post('/user/portfolio/projects/add/', {
        #    'user': self.user.user_data, 'title': 'My Project.',
        #    'details': 'This is my project', 'start_date': '2018-12-31',
        #    'end_date': '2019-01-15'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Project.")
        
'''
    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

'''
