from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from .forms import CustomSignupForm
from .forms import CustomLoginForm
from django.contrib.auth import login
from .utils import superuser_access, visitor_access
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
import random
from datetime import datetime
from dashboard.models import Listing, Bid, User, Comment, VIPStatus, Complaint, UserApplication, Rating, Transaction
from django.views.decorators.http import require_POST
from django.db.models import Max
from decimal import Decimal
from django import forms


load_dotenv()


SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# Custom Signup View
# class CustomSignupView(View):
#     def get(self, request):
#         form = CustomSignupForm()
#         return render(request, 'signup.html', {'form': form})

#     def post(self, request):
#         form = CustomSignupForm(request.POST)
#         if form.is_valid():
#             user = form.save(request)  # This calls the overridden save method
#             print(f"New user created: {user.username} ({user.id})")
#             login(request, user)
#             return redirect('profile')
#         else:
#             print(form.errors)  # Debug invalid form submissions
#         return render(request, 'signup.html', {'form': form, 'errors': form.errors})

class CustomSignupView(View):
    def get(self, request):
        # Generate a random arithmetic question
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operators = ["+", "-", "*"]
        operator = random.choice(operators)

        # Calculate the correct answer
        if operator == "+":
            correct_answer = num1 + num2
        elif operator == "-":
            correct_answer = num1 - num2
        else:
            correct_answer = num1 * num2

        question = f"What is {num1} {operator} {num2}?"

        # Create the form and render the page
        form = CustomSignupForm()
        return render(request, 'signup.html', {
            'form': form,
            'arithmetic_question': question,
        })

    def post(self, request):
        form = CustomSignupForm(request.POST)
        arithmetic_answer = request.POST.get('arithmetic_answer')
        security_question = request.POST.get('security_question')

        # Validate the arithmetic answer
        try:
            num1, operator, num2 = security_question.split()
            num1, num2 = int(num1), int(num2)
            correct_answer = eval(f"{num1} {operator} {num2}")
        except Exception:
            return render(request, 'signup.html', {
                'form': form,
                'arithmetic_question': security_question,
                'error': "Invalid arithmetic question. Please try again."
            })

        if int(arithmetic_answer) != correct_answer:
            return render(request, 'signup.html', {
                'form': form,
                'arithmetic_question': security_question,
                'error': "Incorrect answer to the arithmetic question. Please try again."
            })

        # If form is valid, save the user and their data to Supabase
        if form.is_valid():
            user = form.save(request=request)  # Pass the request argument here
            print(f"New user created: {user.username} ({user.id})")

            # Save user data in Supabase
            response = supabase.table('user_applications').insert({
                'id': user.id,
                'arithmetic_question': security_question,
                'answer': correct_answer
            }).execute()

            print("Supabase insert response:", response)

            # Log the user in after successful signup
            login(request, user)

            # Redirect to the visitor message page instead of profile
            return redirect('visitor_message')  # Change this to the URL name for the visitor message page
        else:
            # If the form is invalid, render the page with errors
            return render(request, 'signup.html', {
                'form': form,
                'arithmetic_question': security_question,
                'errors': form.errors
            })


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
# @login_required
# def profile(request):
#     return render(request, 'profile.html', {'user': request.user})
@login_required
@visitor_access
def profile(request):
    print(f"Logged in user: {request.user.username} ({request.user.id})")
    user_id = request.user.id  # Get the current user's ID
    response = supabase.table('transactions').select('buyer_id, seller_id').eq('buyer_id', user_id).or_('seller_id.eq.' + str(user_id)).execute()
    total_transactions = len(response.data)  # Count the number of transactions

    # Combine context into a single dictionary
    context = {
        'user': request.user,
        'total_transactions': total_transactions
    }
    return render(request, 'profile.html', context)
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
    if request.method == 'POST':
        try:
            # Get form data
            listing_data = {
                'title': request.POST.get('title'),
                'description': request.POST.get('description'),
                'price': float(request.POST.get('price')),
                'category': request.POST.get('category'),
                'availability': request.POST.get('availability'),
                'deadline': request.POST.get('deadline') + 'T24:00:00',
                'user_id': request.user.id,
                'highest_bid': 0,
            }

            # Insert listing into Supabase
            listing_response = supabase.table('listings').insert(listing_data).execute()
            listing_id = listing_response.data[0]['id']

            # Handle multiple image uploads
            images = request.FILES.getlist('images')

            for image in images:
                try:
                    file_path = f"{request.user.id}/{listing_id}/{image.name}"
                    file_content = image.read()

                    print(f"Attempting to upload {file_path}")

                    # Upload to Supabase storage
                    upload_response = supabase.storage \
                        .from_('images') \
                        .upload(
                            path=file_path,
                            file=file_content,
                            file_options={"contentType": image.content_type}
                        )
                    print("Upload response:", upload_response)

                    # Get public URL
                    image_url = supabase.storage.from_('images').get_public_url(file_path)

                    # Create image record
                    image_data = {
                        'listing_id': listing_id,
                        'image_url': image_url
                    }

                    # Insert with explicit error handling
                    try:
                        image_response = supabase.table('listing_images') \
                            .insert(image_data) \
                            .execute()
                        print("Successfully created image record:", image_response.data)
                    except Exception as db_error:
                        print(f"Database error: {str(db_error)}")
                        print(f"Error type: {type(db_error)}")
                        import traceback
                        print(traceback.format_exc())

                except Exception as e:
                    print(f"Error in image upload process: {str(e)}")
                    import traceback
                    print(traceback.format_exc())

            return redirect('viewbids')

        except Exception as e:
            print(f"Error in listing creation: {str(e)}")
            return render(request, 'viewbids.html', {'error': 'Failed to create listing'})

    # Get all listings for display
    listings = supabase.table('listings').select('*').eq('user_id', request.user.id).execute()
    return render(request, 'viewbids.html', {'all_listings': listings.data})

# Dashboard's Requests
@login_required
def requests(request):
    try:
        # Fetch user's balance from Supabase
        balance_response = supabase.table('users')\
            .select('balance')\
            .eq('email', request.user.email)\
            .single()\
            .execute()

        user_balance = float(balance_response.data['balance']) if balance_response.data else 0
        user_balance = "{:.2f}".format(user_balance)

        return render(request, 'requests.html', {
            'user_balance': user_balance
        })
    except Exception as e:
        print(f"Error fetching user balance: {str(e)}")
        return render(request, 'requests.html', {
            'user_balance': '0.00'
        })

@login_required
def request_deactivation(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        user = User.objects.get(email=request.user.email)
        user.status = 'pending_deactivation'
        user.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Admin Pages - For Superusers Only
@superuser_access
def adminPage(request):
    return render(request, 'admin.html')

@superuser_access
def applications(request):
    # Fetch listings grouped by category
    try:
        pendingApplications = supabase.table('user_applications').select('*').execute()

        # Prepare the context with the required fields
        applications_data = []
        for application in pendingApplications.data:
            applications_data.append({
                'full_name': f"{application['first_name']} {application['last_name']}",
                'username': application['username'],
                'submission_date': application['application_date'],
                'arithmetic_question': application['arithmetic_question'],
                'user_answer': application['answer'],
            })

        context = {
            'pendingApplications': applications_data
        }

        return render(request, 'applications.html', context)

    except Exception as e:
        print(f"Error fetching from Supabase: {str(e)}")
        return render(request, 'applications.html', {'error': 'Unable to load listings'})

@superuser_access
def complaints(request):
    try:
        print("Fetching complaints...")

        # Updated query to use auth_user instead of users
        complaints_data = supabase.table('complaints')\
            .select(
                'id, complaint_text, status, created_at, resolved_at',
                'complainant:auth_user!complainant_user_id(first_name,last_name, email)',
                'defendant:auth_user!defendant_user_id(first_name,last_name, email)'
            )\
            .execute()

        print("Raw data:", complaints_data.data)

        formatted_complaints = []
        for complaint in complaints_data.data:
            try:
                formatted_complaints.append({
                    'id': complaint['id'],
                    'complainant': {
                        'name': f"{complaint['complainant']['first_name']} {complaint['complainant']['last_name']}",
                        'email': complaint['complainant']['email'],
                    },
                    'defendant': {
                        'name': f"{complaint['defendant']['first_name']} {complaint['defendant']['last_name']}",
                        'email': complaint['defendant']['email'],
                    },
                    'created_at': complaint['created_at'].split('T')[0] if complaint['created_at'] else '',
                    'status': complaint['status'],
                    'complaint_text': complaint['complaint_text']  # Add this line
                })
            except Exception as e:
                print(f"Error formatting complaint: {str(e)}")
                continue

        return render(request, 'complaints.html', {'complaints': formatted_complaints})
    except Exception as e:
        print(f"Error fetching complaints: {str(e)}")
        return render(request, 'complaints.html', {'error': str(e)})

@superuser_access
def users(request):
    try:
        current_user = User.objects.get(email=request.user.email)
        if current_user.role != 'super-user':
            return redirect('dashboard')

        # Get all users
        users_data = User.objects.all().values(
            'id', 'email', 'username', 'first_name', 'last_name',
            'created_at', 'status'
        )
        # Get active VIP users
        vip_users = VIPStatus.objects.filter(status='active').values_list('user_id', flat=True)
        # Add VIP status to users data
        for user in users_data:
            user['is_vip'] = user['id'] in vip_users
        context = {
            'users': users_data,
            'error': None
        }
    except Exception as e:
        context = {
            'users': [],
            'error': str(e)
        }
    return render(request, 'users.html', context)

@superuser_access
def update_user_status(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        user_id = request.POST.get('user_id')
        new_status = request.POST.get('status')
        # Update valid statuses to include pending_deactivation
        valid_statuses = ['active', 'suspended', 'deactivated', 'pending_deactivation']
        if new_status not in valid_statuses:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        # Update user status
        user = User.objects.get(id=user_id)
        user.status = new_status
        user.save()
        return JsonResponse({'success': True, 'status': new_status})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def homepage(request):
        # Fetch all listings by category, excluding sold items
        electronics = supabase.table('listings').select('id, title, price, availability, category').eq('category', 'Electronics').neq('availability', 'sold').execute()
        school_essentials = supabase.table('listings').select('id, title, price, availability, category').eq('category', 'School Essentials').neq('availability', 'sold').execute()
        fashion = supabase.table('listings').select('id, title, price, availability, category').eq('category', 'Fashion & Apparel').neq('availability', 'sold').execute()
        accessories = supabase.table('listings').select('id, title, price, availability, category').eq('category', 'Accessories & Gadgets').neq('availability', 'sold').execute()

        # Fetch all images
        images = supabase.table('listing_images').select('*').execute()

        # Create mapping of listing_id to first image URL
        listing_images = {}
        for image in images.data:
            listing_id = image['listing_id']
            if listing_id not in listing_images:  # Only take the first image for each listing
                listing_images[listing_id] = image['image_url']

        # Function to add image URLs to listings
        def add_images_to_listings(listings):
            processed = []
            for listing in listings:
                listing_copy = listing.copy()
                listing_copy['image_url'] = listing_images.get(listing['id'])
                processed.append(listing_copy)
            return processed

        context = {
            'electronics': add_images_to_listings(electronics.data),
            'school_essentials': add_images_to_listings(school_essentials.data),
            'fashion': add_images_to_listings(fashion.data),
            'accessories': add_images_to_listings(accessories.data),
        }

        return render(request, 'homepage.html', context)

    # except Exception as e:
    #     print(f"Error: {str(e)}")
    #     return render(request, 'homepage.html', {'error': 'Unable to load listings'})

# visit listings

def listing(request, id):
    try:
        # Fetch listing with seller information
        listing = supabase.table('listings')\
            .select(
                '*',
                'users(first_name,last_name)'
            )\
            .eq('id', id)\
            .execute()

        if not listing.data or len(listing.data) == 0:
            return render(request, 'error.html', {'message': 'Listing not found'})

        listing_data = listing.data[0]
        try:
            images = supabase.table('listing_images').select('*').eq('listing_id', id).execute()
            images_data = images.data if images and images.data else []
        except Exception as e:
            print(f"Error fetching images: {str(e)}")
            images_data = []

        try:
            comments = supabase.table('comments')\
                .select(
                    'comment',
                    'created_at',
                    'commenter:users(first_name,last_name)'
                )\
                .eq('listing_id', id)\
                .order('created_at', desc=True)\
                .execute()

            formatted_comments = []
            for comment in (comments.data or []):

                if comment.get('commenter') is None:
                    user_info = {
                        'first_name': 'Visitor',
                        'last_name': ''
                    }
                else:
                    user_info = {
                        'first_name': comment['commenter'].get('first_name', 'Anonymous'),
                        'last_name': comment['commenter'].get('last_name', '')
                    }

                formatted_comments.append({
                    'user': user_info,
                    'comment': comment.get('comment', '')
                })
        except Exception as e:
            print(f"Error fetching comments: {str(e)}")
            formatted_comments = []

        try:
            bids = supabase.table('bids')\
                .select(
                    'id',
                    'amount',
                    'status',
                    'created_at',
                    'bidder:users!user_id(first_name,last_name)'
                )\
                .eq('listing_id', id)\
                .eq('status', 'pending')\
                .order('amount', desc=True)\
                .execute()

            formatted_bids = []
            for bid in (bids.data or []):
                bidder = bid.get('bidder', {})
                formatted_bids.append({
                    'id': bid.get('id'),
                    'user': {
                        'first_name': bidder.get('first_name', 'Anonymous'),
                        'last_name': bidder.get('last_name', '')
                    },
                    'amount': bid.get('amount', 0),
                    'status': bid.get('status', 'unknown')
                })
        except Exception as e:
            print(f"Error fetching bids: {str(e)}")
            formatted_bids = []

        try:
            if 'users' in listing_data and listing_data['users']:
                seller_info = listing_data['users']
            else:

                user_response = supabase.table('users')\
                    .select('first_name,last_name')\
                    .eq('id', listing_data.get('user_id'))\
                    .execute()
                seller_info = user_response.data[0] if user_response.data else {}
        except Exception as e:
            print(f"Error fetching seller info: {str(e)}")
            seller_info = {}

        safe_listing_data = {
            'id': listing_data.get('id'),
            'title': listing_data.get('title', 'Untitled Listing'),
            'description': listing_data.get('description', 'No description available'),
            'price': listing_data.get('price', 0),
            'category': listing_data.get('category', 'Uncategorized'),
            'created_at': listing_data.get('created_at', ''),
            'seller_id': listing_data.get('user_id'),
            'availability': listing_data.get('availability', 'for-sale'),
            'seller': {
                'first_name': seller_info.get('first_name', 'Anonymous'),
                'last_name': seller_info.get('last_name', 'Seller')
            }
        }

        bids_response = supabase.table('bids')\
            .select(
                'amount',
                'user_id',
                'users(first_name,last_name)'
            )\
            .eq('listing_id', id)\
            .execute()

        # Find the highest bid
        highest_bid = 0
        highest_bidder = None
        if bids_response.data:
            for bid in bids_response.data:
                if float(bid['amount']) > highest_bid:
                    highest_bid = float(bid['amount'])
                    highest_bidder = {
                        'id': bid['user_id'],
                        'name': f"{bid['users']['first_name']} {bid['users']['last_name']}"
                    }

        # If no bids, use listing price as starting bid
        if highest_bid == 0:
            highest_bid = float(listing_data.get('price', 0))

        # Format the highest bid to 2 decimal places
        highest_bid = "{:.2f}".format(highest_bid)

        # Debug user authentication
        print(f"User authenticated: {request.user.is_authenticated}")
        print(f"User email: {request.user.email if request.user.is_authenticated else 'Not logged in'}")

        # Get user's balance if authenticated
        user_balance = 0
        if request.user.is_authenticated:
            balance_response = supabase.table('users')\
                .select('balance')\
                .eq('email', request.user.email)\
                .execute()

            print(f"Balance response: {balance_response.data}")  # Debug print

            if balance_response.data:
                user_balance = float(balance_response.data[0].get('balance', 0))
            print(f"Final user balance: {user_balance}")  # Debug print

        # Add user_balance to context and print it
        context = {
            'listing': safe_listing_data,
            'images': images_data,
            'comments': formatted_comments,
            'bids': formatted_bids,
            'highest_bid': highest_bid,
            'highest_bidder': highest_bidder,
            'user': request.user,
            'user_balance': user_balance,
        }
        return render(request, 'listing.html', context)

    except Exception as e:
        print(f"Error in listing view: {str(e)}")
        return render(request, 'error.html', {'message': 'Error loading listing'})

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

@require_POST
def update_status(request):
    try:
        data = json.loads(request.body)
        complaint_id = data.get('complaint_id')
        new_status = data.get('status')

        # Update Supabase
        supabase.table('complaints')\
            .update({'status': new_status})\
            .eq('id', complaint_id)\
            .execute()
        return JsonResponse({'success': True})
    except Exception as e:
        print(f"Error updating status: {str(e)}")  # For debugging
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def deposit_money(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = float(data.get('amount', 0))

            if amount <= 0:
                return JsonResponse({'error': 'Invalid amount'}, status=400)

            # Get current user's balance
            user_data = supabase.table('users').select('balance').eq('id', request.user.id).execute()
            current_balance = float(user_data.data[0]['balance']) if user_data.data else 0
            # Update balance
            new_balance = current_balance + amount
            supabase.table('users').update({'balance': new_balance}).eq('id', request.user.id).execute()

            return JsonResponse({'success': True, 'new_balance': new_balance})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
@login_required
def withdraw_money(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = float(data.get('amount', 0))

            if amount <= 0:
                return JsonResponse({'error': 'Invalid amount'}, status=400)
            # Get current user's balance
            user_data = supabase.table('users').select('balance').eq('id', request.user.id).execute()
            current_balance = float(user_data.data[0]['balance']) if user_data.data else 0
            if amount > current_balance:
                return JsonResponse({'error': 'Insufficient funds'}, status=400)
            # Update balance
            new_balance = current_balance - amount
            supabase.table('users').update({'balance': new_balance}).eq('id', request.user.id).execute()

            return JsonResponse({'success': True, 'new_balance': new_balance})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
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

#place bid
# def place_bid(request, listing_id):
#     if request.method == 'POST':
#         listing = get_object_or_404(Listing, id=listing_id)
#         current_highest_bid = listing.highest_bid

#         bid_amount = float(request.POST.get('bid_amount'))

#         if bid_amount > current_highest_bid:
#             Bid.objects.create(listing=listing, user=request.user, amount=bid_amount)
#             listing.highest_bid = bid_amount
#             listing.save()

#             return JsonResponse({'status': 'success', 'new_highest_bid': bid_amount})
#         else:
#             return JsonResponse({'status': 'error', 'message': 'Bid must be higher than the current highest bid.'})

#     return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
@csrf_exempt
@login_required
def place_bid(request, listing_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bid_amount = Decimal(data.get('bid_amount'))

            # Get the listing
            listing_response = supabase.table('listings').select('*').eq('id', listing_id).execute()
            if not listing_response.data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Listing not found'
                }, status=404)
                
            listing = listing_response.data[0]
            
            # Check if user is the seller
            if request.user.email == listing.get('user_email'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'You cannot bid on your own listing'
                }, status=403)
            
            # Get user's current balance from Supabase
            user_response = supabase.table('users').select('balance').eq('email', request.user.email).execute()
            if not user_response.data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'User not found'
                }, status=404)
                
            current_balance = Decimal(user_response.data[0].get('balance', 0))
            
            # Check if user has sufficient funds
            if current_balance < bid_amount:
                print(f"Insufficient funds: balance={current_balance}, bid={bid_amount}")  # Debug print
                return JsonResponse({
                    'status': 'error',
                    'message': 'Insufficient funds in your account.'
                })
            
            # Create new bid in Supabase
            bid_data = {
                'user_id': request.user.id,
                'listing_id': listing_id,
                'amount': float(bid_amount),
                'status': 'pending'
            }
            
            supabase.table('bids').insert(bid_data).execute()
            
            return JsonResponse({'status': 'success'})

        except Exception as e:
            print(f"Error in place_bid: {str(e)}")  # Debug print
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

def fetch_comments(request, listing_id):
    try:
        comments = supabase.table('comments')\
            .select(
                'comment',
                'created_at',
                'commenter:users(first_name,last_name)'
            )\
            .eq('listing_id', listing_id)\
            .order('created_at', desc=True)\
            .execute()

        comments_data = []
        for comment in comments.data:
            # Handle case where commenter might be null (visitor)
            if comment.get('commenter') is None:
                user_info = {
                    'first_name': 'Visitor',
                    'last_name': ''
                }
            else:
                user_info = {
                    'first_name': comment['commenter'].get('first_name', 'Anonymous'),
                    'last_name': comment['commenter'].get('last_name', '')
                }

            comments_data.append({
                'user': user_info,
                'comment': comment.get('comment', ''),
                'created_at': comment.get('created_at', '')
            })

        return JsonResponse({'comments': comments_data})
    except Exception as e:
        print(f"Error in fetch_comments: {str(e)}")
        return JsonResponse({'comments': []})


def create_comment(request, listing_id):
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        if comment_text:
            try:
                commenter_id = request.user.id if request.user.is_authenticated else None

                comment_data = {
                    'listing_id': listing_id,
                    'comment': comment_text
                }

                if commenter_id is not None:
                    comment_data['commenter_id'] = commenter_id

                supabase.table('comments').insert(comment_data).execute()
            except Exception as e:
                print(f"Error creating comment: {str(e)}")

    return redirect('listing', id=listing_id)


@superuser_access
def update_application_status(request):
    if request.method == "POST":
        try:
            # Parse JSON request body
            data = json.loads(request.body)
            username = data.get('username')
            action = data.get('action')

            if not username or not action:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            print("Updating role for username:", username)  # Debugging output

            # Determine the new status based on the action
            new_status = 'approved' if action == 'approve' else 'rejected'

            # Update the application status in Supabase
            response = supabase.table('user_applications').update({'status': new_status}).eq('username', username).execute()

            print("Application update response:", response)  # Debugging output

            # Check for errors in the response
            if hasattr(response, 'error') and response.error:
                return JsonResponse({"error": response.error.message}, status=500)

            # If the action is approve, update the user's role
            if action == 'approve':
                # Update the user's role in the users table
                user_response = supabase.table('users').update({'role': 'user'}).eq('username', username).execute()

                print("User role update response:", user_response)  # Debugging output
                print("User role update data:", user_response.data)  # Debugging output

                # Check for errors in the user role update response
                if hasattr(user_response, 'error') and user_response.error:
                    return JsonResponse({"error": user_response.error.message}, status=500)

            return JsonResponse({"message": f"Application {new_status} successfully."}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)

def visitor_message(request):
    return render(request, 'visitor_message.html')

def get_user_rating_info(user_id):
    try:
        response = supabase.table('ratings')\
            .select('rating')\
            .eq('rated_user_id', user_id)\
            .execute()
        ratings = [r['rating'] for r in response.data]
        if ratings:
            average_rating = sum(ratings) / len(ratings)
            rating_count = len(ratings)
            return {
                'average': round(average_rating, 1),
                'count': rating_count
            }
        return {
            'average': 0.0,
            'count': 0
        }
    except Exception as e:
        print(f"Error calculating rating: {str(e)}")
        return {
            'average': 0.0,
            'count': 0
        }

@login_required
def accept_bid(request, bid_id):
    if request.method == 'POST':
        try:
            # Get the bid and related information
            bid_response = supabase.table('bids')\
                .select('*, listing:listings(*), user:users(*)')\
                .eq('id', bid_id)\
                .single()\
                .execute()

            if not bid_response.data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Bid not found'
                }, status=404)

            bid = bid_response.data
            listing_id = bid['listing_id']
            buyer_id = bid['user_id']
            seller_id = bid['listing']['user_id']
            amount = Decimal(bid['amount'])

            if request.user.id != seller_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Unauthorized'
                }, status=403)

            try:
                supabase.table('bids')\
                    .update({'status': 'accepted'})\
                    .eq('id', bid_id)\
                    .execute()


                supabase.table('bids')\
                    .update({'status': 'rejected'})\
                    .neq('id', bid_id)\
                    .eq('listing_id', listing_id)\
                    .execute()


                buyer_response = supabase.table('users')\
                    .select('balance')\
                    .eq('id', buyer_id)\
                    .single()\
                    .execute()

                buyer_balance = Decimal(buyer_response.data['balance'])

                seller_response = supabase.table('users')\
                    .select('balance')\
                    .eq('id', seller_id)\
                    .single()\
                    .execute()

                seller_balance = Decimal(seller_response.data['balance'])

                supabase.table('users')\
                    .update({'balance': float(buyer_balance - amount)})\
                    .eq('id', buyer_id)\
                    .execute()

                supabase.table('users')\
                    .update({'balance': float(seller_balance + amount)})\
                    .eq('id', seller_id)\
                    .execute()

                transaction_data = {
                    'buyer_id': buyer_id,
                    'seller_id': seller_id,
                    'listing_id': listing_id,
                    'amount': float(amount),
                    'status': 'completed',
                    'created_at': 'now()',
                    'updated_at': 'now()'
                }

                transaction_response = supabase.table('transactions')\
                    .insert(transaction_data)\
                    .execute()

                supabase.table('listings')\
                    .update({'availability': 'sold'})\
                    .eq('id', listing_id)\
                    .execute()
                return JsonResponse({
                    'status': 'success',
                    'transaction_id': transaction_response.data[0]['id'],
                    'buyer_name': f"{bid['user']['first_name']} {bid['user']['last_name']}",
                    'listing_title': bid['listing']['title']
                })
            except Exception as e:
                print(f"Transaction error: {str(e)}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Transaction failed'
                }, status=500)
        except Exception as e:
            print(f"Error in accept_bid: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

@login_required
def decline_bid(request, bid_id):
    if request.method == 'POST':
        try:
            print(f"Attempting to decline bid {bid_id}")  # Debug log
            # Update the bid status in Supabase
            response = supabase.table('bids')\
                .update({'status': 'rejected'})\
                .eq('id', bid_id)\
                .execute()

            # Check if the update was successful by checking if data was returned
            if response.data:
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to update bid status'
                }, status=500)
        except Exception as e:
            print(f"Exception in decline_bid: {str(e)}")  # Debug log
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

@login_required
def submit_rating(request, transaction_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rating_value = data.get('rating')
            comment = data.get('comment')

            transaction = Transaction.objects.get(id=transaction_id)

            if request.user == transaction.buyer:
                rated_user = transaction.seller
            else:
                rated_user = transaction.buyer

            # Create the rating
            Rating.objects.create(
                rater_user=request.user,
                rated_user=rated_user,
                transaction=transaction,
                rating=rating_value,
                comment=comment
            )

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

#suspension fee
@login_required
def suspension_fee(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        balance_response = supabase.table('users')\
            .select('balance')\
            .eq('email', request.user.email)\
            .single()\
            .execute()
        current_balance = float(balance_response.data['balance']) if balance_response.data else 0
        fee_amount = 50.00

        if current_balance < fee_amount:
            return JsonResponse({
                'error': 'Insufficient funds. Please deposit money to activate your account again.'
            }, status=400)

        new_balance = current_balance - fee_amount
        supabase.table('users')\
            .update({
                'balance': new_balance,
                'status': 'active'
            })\
            .eq('email', request.user.email)\
            .execute()

        return JsonResponse({'success': True, 'new_balance': new_balance})

    except Exception as e:
        print(f"Error processing reactivation fee: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# @login_required
# def check_account_status(request):
#     try:
#         response = supabase.table('users')\
#             .select('status')\
#             .eq('email', request.user.email)\
#             .single()\
#             .execute()
#         return JsonResponse({
#             'status': response.data.get('status', 'inactive')
#         })
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)