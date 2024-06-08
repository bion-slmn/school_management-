from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser, Staffs, Students, AdminHOD
from typing import Dict
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from rest_framework.permissions import IsAuthenticated


def contact(request: HttpRequest)-> HttpResponse:
    """
    Renders the contact page.

    Args:
        request: HttpRequest object representing the request made.

    Returns:
        HttpResponse object representing the response.
    """ 
    return render(request, 'contact.html')


class LoginUser(APIView):
    def post(self, request, *args, **kwargs):
        email_id = request.data.get('email')
        password = request.data.get('password')

        if not (email_id and password):
            return Response('Provide Email and Password',
                            status=status.HTTP_400_BAD_REQUEST)

        username = email_id.split('@')[0].split('.')[0]
        user = authenticate(username=username, password=password)
        if not user:
            return Response('Invalid Login Credentials!!',
                            status=status.HTTP_400_BAD_REQUEST) 

        login(request, user)

        return Response(f'{user.id} Successfull logged in') 



class RegisterUser(APIView):
    
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new user.

        Args:
            request: The request object containing user data.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response indicating the outcome of the user creation process.

        Raises:
            None
        """

        params = ['first_name','last_name', 'email', 'password', 'confirm_password']
        user_data = {param: request.data.get(param) for param in params}
        
        if not (user_data['email'] and user_data['password'] and 
                user_data['confirm_password']):
            return Response('Please provide all details', status=400)
        if user_data['password']  != user_data['confirm_password']:
            return Response('Password dont match', status=400)
        if self.user_exists(user_data['email']):
            return Response('User with Email exists', status=400)

        user_type = self.get_user_type_from_email(user_data['email']) 
        if not user_type:
            email_format = '<username>.<staff|student|hod>@<college_domain>'
            return Response(f"Use Invalid format:{email_format}'", status=400)
            
        username = user_data['email'].split('@')[0].split('.')[0] 
        if self.username_exists(username): 
            return Response('Usernames exists, change email', status=400)
        
        user_data['username'] = username
        self.create_user(user_data, user_type)       
        return Response('Sucesfully Registered')


    def username_exists(self, username: str) -> bool:
        """
        Checks if a user with the provided username already exists.

        Args:
            username: String representing the username to check.

        Returns:
            bool indicating whether a user with the
            given username exists (True) or not (False).
        """
        
        return CustomUser.objects.filter(username=username).exists()

    def user_exists(self, email_id: str) -> bool:
        """
        Checks if a user with the provided email, password, and confirm password exists.

        Args:

            email_id: String representing the user's email address.

        Returns:
            bool indicating whether a user with the given details exists (True) or not (False).
        """
    
        return CustomUser.objects.filter(email=email_id).exists()


    def create_user(self, user_data: Dict[str, str], user_type: str) -> bool:
        """
        Creates a new user based on the provided parameters and user type.

        Args:
            user_data: Dictionary containing user data parameters.
            user_type: String representing the type of user to create.

        Returns:
            bool indicating success (True) or failure (False) of user creation.
        """

        user = CustomUser()
        user.user_type = user_type

        for key, value in user_data.items():
            if key == 'password':
                user.set_password(value)
            elif key != 'confirm_password':
                setattr(user, key, value)
        user.save()

        user_object = {
            CustomUser.STUDENT : Students,
            CustomUser.STAFF: Staffs,
            CustomUser.HOD: AdminHOD,
        }

        if user_obj := user_object.get(user_type):
            user_obj.objects.create(admin=user)
            return True
        return False
    def get_user_type_from_email(self, email_id: str): 
        """ 
        Returns CustomUser.user_type corresponding to the given email address 
        email_id should be in following format: 
        '<username>.<staff|student|hod>@<college_domain>' 
        eg.: 'abhishek.staff@jecrc.com' 
        """
    
        try: 
            email_id = email_id.split('@')[0] 
            email_user_type = email_id.split('.')[1] 
            return CustomUser.EMAIL_TO_USER_TYPE_MAP[email_user_type] 
        except Exception : 
            return None


class LogoutView(APIView):
    """
    A simple View to log out a user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Logs out the user and redirects to the homepage.

        Args:
            request: HttpRequest object representing the request made.

        Returns:
            HttpResponseRedirect object redirecting to the homepage.
        """

        logout(request) 
        return Response({"message": "Successfully logged out"})

