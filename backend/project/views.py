from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from .forms import CustomSignupForm
from .forms import CustomLoginForm
from django.contrib.auth import login
from .utils import superuser_access
from django.contrib.auth.views import LoginView
from supabase import create_client
from django.contrib import messages
from django.contrib.auth import authenticate
from django.urls import reverse


# Custom Signup View
class CustomSignupView(View):
    def get(self, request):
        form = CustomSignupForm()
        return render(request, 'signup.html', {'form': form})

    # def post(self, request):
    #     print(request.POST)
    #     form = CustomSignupForm(request.POST)
    #     if form.is_valid():
    #         user = form.save(request)
    #         login(request, user)
    #         return redirect('profile')
    #     else:
    #         print(form.errors)
    #     return render(request, 'signup.html', {'form': form, 'errors': form.errors})
    def post(self, request):
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save(request)  # This calls the overridden save method
            print(f"New user created: {user.username} ({user.id})")
            login(request, user)
            return redirect('profile')
        else:
            print(form.errors)  # Debug invalid form submissions
        return render(request, 'signup.html', {'form': form, 'errors': form.errors})

# class CustomLoginView(View):
#     def get(self, request):
#         if request.user.is_authenticated:
#             return redirect('profile')
#         return render(request, 'login.html')

#     def post(self, request):
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('profile')
#         else:
#             messages.error(request, 'Invalid username or password')
#             return render(request, 'login.html', {'error': 'Invalid credentials'})

# class CustomLoginView(LoginView):
#     def get_success_url(self):
#         return reverse('profile')

class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        print(f"Attempting login for: {request.POST.get('username')}")
        response = super().post(request, *args, **kwargs)
        print(f"Login successful for: {request.user.username if request.user.is_authenticated else 'None'}")
        return response

    def get_success_url(self):
        return reverse('profile')

# Homepage View
def homepage(request):
    return render(request, 'homepage.html')

# Profile View (Login Required)
@login_required
# def profile(request):
#     return render(request, 'profile.html', {'user': request.user})
def profile(request):
    print(f"Logged in user: {request.user.username} ({request.user.id})")
    return render(request, 'profile.html', {'user': request.user})

# Dashboard View
@login_required
def dashboard(request):
    if request.user.is_superuser:
        return render(request, 'admin.html', {'admin_dashboard': True})
    else:
        return render(request, 'dashboard.html', {'user_dashboard': True})

# Dashboard's My Account View
@login_required
def account(request):
    return render(request, 'account.html')

# Dashboard's View Bids
@login_required
def viewbids(request):
    return render(request, 'viewbids.html')

# Dashboard's Requests
@login_required
def requests(request):
    return render(request, 'requests.html')

# Admin Pages - For Superusers Only
@superuser_access
def adminPage(request):
    return render(request, 'admin.html')

@superuser_access
def applications(request):
    return render(request, 'applications.html')

@superuser_access
def complaints(request):
    return render(request, 'complaints.html')

@superuser_access
def users(request):
    return render(request, 'users.html')


from supabase import create_client
from django.conf import settings

def homepage(request):
    # Initialize Supabase client
    supabase = create_client('https://tocrntktnrrrcaxtnvly.supabase.co/', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvY3JudGt0bnJycmNheHRudmx5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzIxODA1NzksImV4cCI6MjA0Nzc1NjU3OX0.bTG7DuVYl8R-FhL3pW_uHJSYwSFClS1VO3--1eA6d-E')

    # Fetch listings grouped by category
    try:
        electronics = supabase.table('listings').select('*').eq('category', 'Electronics').execute()
        school_essentials = supabase.table('listings').select('*').eq('category', 'School Essentials').execute()
        fashion = supabase.table('listings').select('*').eq('category', 'Fashion & Apparel').execute()
        accessories = supabase.table('listings').select('*').eq('category', 'Accessories & Gadgets').execute()

        context = {
            'electronics': electronics.data,
            'school_essentials': school_essentials.data,
            'fashion': fashion.data,
            'accessories': accessories.data
        }

        return render(request, 'homepage.html', context)

    except Exception as e:
        print(f"Error fetching from Supabase: {str(e)}")
        return render(request, 'homepage.html', {'error': 'Unable to load listings'})

# visit listings
def listing(request, id):
    # Initialize Supabase client
    supabase = create_client('https://tocrntktnrrrcaxtnvly.supabase.co/', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvY3JudGt0bnJycmNheHRudmx5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzIxODA1NzksImV4cCI6MjA0Nzc1NjU3OX0.bTG7DuVYl8R-FhL3pW_uHJSYwSFClS1VO3--1eA6d-E')
    try:
        # Fetch the specific listing
        result = supabase.table('listings').select('*').eq('id', id).execute()
        listing = result.data[0] if result.data else None

        return render(request, 'listing.html', {'listing': listing})
    except Exception as e:
        print(f"Error fetching listing from Supabase: {str(e)}")
        return render(request, 'listing.html', {'error': 'Unable to load listing'})
