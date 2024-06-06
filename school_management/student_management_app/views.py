from django.shortcuts import (
    render, 
    HttpResponse, 
    HttpRequest, 
    redirect, 
    HttpResponseRedirect
    )
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser, Staffs, Students, AdminHOD

# Create your views here.

def home(request: HttpRequest) -> HttpResponse:
    """
    A view that renders the home page.

    Args:
        request: HttpRequest object representing the request made.

    Returns:
        HttpResponse object representing the response.

    Examples:
        render(request, 'home.html')
    """

    return render(request, 'home.html')

def contact(request: HttpRequest)-> HttpResponse:
   """
    Renders the contact page.

    Args:
        request: HttpRequest object representing the request made.

    Returns:
        HttpResponse object representing the response.
    """ 
    return render(request, 'contact.html')


def loginUser(request: HttpRequest) ->HttpResponse:
    """
    Renders the login page.

    Args:
        request: HttpRequest object representing the request made.

    Returns:
        HttpResponse object representing the response.
    """

    return render(request, 'login_page.html')


def doLogin(request: HttpRequest) -> HttpResponse:
    """
    Processes user login information and redirects based on user type.

    Args:
        request: HttpRequest object representing the request made.

    Returns:
        HttpResponse object representing the response.
    """

    email_id = request.GET.get('email')
    password = request.GET.get('password')

    if not (email_id and password):
        messages.error(request, "Please provide all the details")
        return render(request, 'login_page.html')

    user = CustomUser.objects.filter(email=email_id, password=password).first()
    if not user:
        messages.error(request, 'Invalid Login Credentials!!') 
        return render(request, 'login_page.html')

    login(request, user)

    if home_page := get_homepage(user):
        return redirect(home_page)
    return render(request, 'home.html') 

def get_homepage(user: CustomUser) -> str:
    """
    Determines the homepage URL to redirect based on the user's type.

    Args:
        user: CustomUser object representing the user.

    Returns:
        str with the homepage URL to redirect to,
         or None if user type is not found.
    """

    home_pages = {
        CustomUser.STUDENT : 'student_home/',
        CustomUser.STAFF: 'staff_home/',
        CustomUser.HOD: 'admin_home/',
    }

    if user_home_page := home_pages.get(user.user_type):
        return user_home_page 
    return None
    

def registration(request: HttpRequest) ->HttpResponse:
    """
    Renders the registration page.

    Args:
        request: HttpRequest object representing the request made.

    Returns:
        HttpResponse object representing the response.
    """

    return render(request, 'registration.html')



def doRegistration(request: HttpRequest) ->HttpResponse:
    """
    Processes user registration data and creates a new user if all validations pass.

    Args:
        request: HttpRequest object representing the request made.

    Returns:
        HttpResponse object representing the response.
    """

    params = ['first_name', 'last_name', 'email', 'password',
              'confirm_password']
    user_data = {param: request.GET.get(param) for param in params}

    email_id = user_data.get('email')
    password = user_data.get('password')
    confirm_password = user_data.get('confirm_password')

    if user_exists(email_id, password, confirm_password)
        return render(request, 'registration.html')

    user_type = get_user_type_from_email(email_id) 
    if not user_type:
        email_format = '<username>.<staff|student|hod>@<college_domain>'
        messages.error(request,
                       f"Please use valid Email format: '{email_foramt}'")
        return render(request, 'registration.html')

    username = email_id.split('@')[0].split('.')[0] 
    if username_exists(username): 
        return render(request, 'registration.html')

    create_user(request, params, user_type)
    
    return render(request, 'login_page.html')


def username_exists(username: str) -> bool:
    """
    Checks if a user with the provided username already exists.

    Args:
        username: String representing the username to check.

    Returns:
        bool indicating whether a user with the
        given username exists (True) or not (False).
    """
    
    if CustomUser.objects.filter(username=username).exists(): 
        messages.error(
            request,
            'Username already exists. Please use different username')
        return True
    return False

def user_exists(
    email_id: str,
    password: str,
    confirm_password: str,
) ->bool:
    """
    Checks if a user with the provided email, password, and confirm password exists.

    Args:

        email_id: String representing the user's email address.
        password: String representing the user's password.
        confirm_password: String representing the confirmed password.

    Returns:
        bool indicating whether a user with the given details exists (True) or not (False).
    """
    
    if not (email_id and password and confirm_password):
        messages.error(request, 'Please provide all the details!!')
        return True

    if password != confirm_password:
        messages.error(request, 'Both passwords should match!!')
        return True
    
    if CustomUser.objects.filter(email=email_id).exists():
        messages.error(request, 
                       'Email id already exists. Please proceed to login!!')
        return True

    return False


def create_user(
    request: HttpRequest,
    params: Dict[str, str],
    user_type: str
) -> bool:
    """
    Creates a new user based on the provided parameters and user type.

    Args:
        request: HttpRequest object representing the request made.
        params: Dictionary containing user data parameters.
        user_type: String representing the type of user to create.

    Returns:
        bool indicating success (True) or failure (False) of user creation.
    """

    user = CustomUser()
    user.user_type = user_type

    for key, value in params.items():
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



def logout_user(request: HttpRequest) ->HttpResponse:
    """
    Logs out the user and redirects to the homepage.

    Args:
        request: HttpRequest object representing the request made.

    Returns:
        HttpResponseRedirect object redirecting to the homepage.
    """

    logout(request) 
    return HttpResponseRedirect('/')

def get_user_type_from_email(email_id): 
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