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

    def post(self, request):
        print(request.POST)
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            login(request, user)
            return redirect('profile')
        else:
            print(form.errors)
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

class CustomLoginView(LoginView):
    def get_success_url(self):
        return reverse('profile')

# Homepage View
def homepage(request):
    return render(request, 'homepage.html')

# Profile View (Login Required)
@login_required
def profile(request):
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