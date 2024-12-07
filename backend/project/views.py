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
from dotenv import load_dotenv
import os
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponse
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
import json


load_dotenv()


SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


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
# @login_required
# def dashboard(request):
#     if request.user.is_superuser:
#         return render(request, 'admin.html', {'admin_dashboard': True})
#     try:
#         user_email = request.user.email
#         response = supabase.table('users').select('balance').eq('email', user_email).execute()
#         balance = response.data[0]['balance'] if response.data else 0
#         context = {
#             'user_dashboard': True,
#             'current_balance': balance
#         }
#         return render(request, 'dashboard.html', context)

#     except Exception as e:
#         print(f"Error fetching balance from Supabase: {str(e)}")
#         return render(request, 'dashboard.html', {
#             'user_dashboard': True,
#             'error': 'Unable to load balance'
#         })

@login_required
def account(request):
    try:
        # Fetch the user's balance
        user_email = request.user.email
        response = supabase.table('users').select('balance').eq('email', user_email).execute()
        balance = response.data[0]['balance'] if response.data else 0

        return render(request, 'account.html', {'current_balance': balance})
    except Exception as e:
        print(f"Error fetching balance for account page: {str(e)}")
        return render(request, 'account.html', {'error': 'Unable to load balance'})


# Dashboard View
@login_required
def dashboard(request):
    if request.user.is_superuser:
        return render(request, 'admin.html', {'admin_dashboard': True})
    else:
        return render(request, 'dashboard.html', {'user_dashboard': True})

# Dashboard's My Account View
# @login_required
# def account(request):
#     return render(request, 'account.html')


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

def homepage(request):
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
    try:
        # Fetch the specific listing
        result = supabase.table('listings').select('*').eq('id', id).execute()
        listing = result.data[0] if result.data else None

        return render(request, 'listing.html', {'listing': listing})
    except Exception as e:
        print(f"Error fetching listing from Supabase: {str(e)}")
        return render(request, 'listing.html', {'error': 'Unable to load listing'})
@login_required
def manage_funds(request):
    user_email = request.user.email
    new_balance = 0

    try:
        response = supabase.table('users').select('balance').eq('email', user_email).execute()

        # Validate the response and extract balance
        if response.data and len(response.data) > 0:
            raw_balance = response.data[0].get('balance')

            try:
                current_balance = float(raw_balance) if raw_balance is not None else 0.0
            except ValueError as ve:
                messages.error(request, "Error parsing balance. Please try again.")
                return redirect('accounts')
        else:
            messages.error(request, "No balance data found. Please contact support.")
            return redirect('accounts')

        if request.method == "POST":
            action = request.POST.get('action')
            amount = float(request.POST.get('amount', 0))

            if amount > 0:
                if action == "deposit":
                    new_balance = current_balance + amount
                    supabase.table('users').update({'balance': new_balance}).eq('email', user_email).execute()
                    messages.success(request, f"${amount} deposited successfully!")

                elif action == "withdraw":
                    print(f"Action: {action}, Amount: {amount}, Current Balance: {current_balance}")
                    if current_balance >= amount:
                        new_balance = current_balance - amount
                        update_response = supabase.table('users').update({'balance': new_balance}).eq('email', user_email).execute()
                        messages.success(request, f"${amount} withdrawn successfully!")
                    else:
                        messages.error(request, "Insufficient balance.")
                        print("Error: Insufficient balance.")
                else:
                    messages.error(request, "Invalid action.")
            else:
                messages.error(request, "Amount must be greater than 0.")

            return redirect('accounts')
        else:
            new_balance = current_balance

    except Exception as e:
        messages.error(request, f"Error fetching balance: {str(e)}")

    return render(request, 'account.html', {'current_balance': new_balance})

@csrf_exempt
def submit_complaint(request):
    if request.method == "POST":
        try:
            # Parse JSON request body
            data = json.loads(request.body)

            # Validate the data (you can add more validation here)
            complainant_user_id = data.get('complainant_user_id')
            defendant_user_id = data.get('defendant_user_id')
            complaint_text = data.get('complaint_text')
            status = "pending"  # Default status for new complaints

            if not complainant_user_id or not defendant_user_id or not complaint_text:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Insert into Supabase
            complaint_data = {
                "complainant_user_id": complainant_user_id,
                "defendant_user_id": defendant_user_id,
                "complaint_text": complaint_text,
                "status": status
            }

            # Insert data into the Supabase table
            response = supabase.from_("complaints").insert([complaint_data]).execute()

            if response.error:
                return JsonResponse({"error": response.error.message}, status=500)

            # Return success response
            return JsonResponse({"message": "Complaint submitted successfully!"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Invalid request method. Only POST is allowed."}, status=405)


