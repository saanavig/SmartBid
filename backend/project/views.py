from django.shortcuts import render, redirect, get_object_or_404
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
import random
import datetime
from dashboard.models import Listing, Bid, User, Comment



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

        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operators = ["+", "-", "*"]
        operator = random.choice(operators)

        if operator == "+":
            correct_answer = num1 + num2
        elif operator == "-":
            correct_answer = num1 - num2
        else:
            correct_answer = num1 * num2

        # Check if the arithmetic answer is correct
        if int(arithmetic_answer) != correct_answer:
            return render(request, 'signup.html', {
                'form': form,
                'arithmetic_question': f"What is {num1} {operator} {num2}?",
                'error': "Incorrect answer to the arithmetic question. Please try again."
            })

        # If form is valid, save the user and their data to Supabase
        if form.is_valid():
            user = form.save()  # This calls the overridden save method in your CustomSignupForm
            print(f"New user created: {user.username} ({user.id})")

            # Save user data in Supabase
            create_client.table('Users').insert({
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'username': user.username,
                'password': user.password,  # It's better to store hashed passwords, not plaintext
                'arithmetic_question': f"What is {num1} {operator} {num2}?",
                'correct_answer': correct_answer
            }).execute()

            # Log the user in after successful signup
            login(request, user)

            # Add a success message for approval waiting
            messages.success(request, "Your application has been submitted. Please wait for the superuser to approve your application.")

            # Redirect to the profile or a success page
            return redirect('profile')  # Or any other success page URL
        else:
            # If the form is invalid, render the page with form errors
            return render(request, 'signup.html', {
                'form': form,
                'arithmetic_question': f"What is {num1} {operator} {num2}?",
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
@login_required
# def profile(request):
#     return render(request, 'profile.html', {'user': request.user})
@login_required
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
    # Fetch listing and images from Supabase
    listing = supabase.table('listings').select('*').eq('id', id).execute()
    images = supabase.table('listing_images').select('*').eq('listing_id', id).execute()

    # Fetch comments from Supabase
    comments = supabase.table('comments').select(
        'comment',
        'created_at',
        'commenter:users(first_name,last_name)'  # Join with users table
    ).eq('listing_id', id).order('created_at', desc=True).execute()

    # Debug prints
    print("Listing data:", listing.data)
    print("Images data:", images.data)
    print("Comments data:", comments.data)

    # Process comments data to match your template's expected format
    formatted_comments = []
    for comment in comments.data:
        formatted_comments.append({
            'user': {
                'first_name': comment['commenter']['first_name'] if comment['commenter'] else 'Visitor',
                'last_name': comment['commenter']['last_name'] if comment['commenter'] else ''
            },
            'comment': comment['comment']
        })

    bids = supabase.table('bids')\
    .select(
        'id',
        'amount',
        'status',
        'created_at',
        'bidder:users!user_id(first_name,last_name)'
    )\
    .eq('listing_id', id)\
    .order('amount', desc=True)\
    .execute()

    #Format bids for template
    formatted_bids = []
    for bid in bids.data:
        formatted_bids.append({
            'id': bid['id'],
            'user': {
                'first_name': bid['bidder']['first_name'],
                'last_name': bid['bidder']['last_name']
            },
            'amount': bid['amount'],
            'status': bid['status']
        })

    #debugging statements
    print("Listing data:", listing.data)
    print("Images data:", images.data)
    print("Comments data:", comments.data)

    context = {
        'listing': listing.data[0],
        'images': images.data,
        'comments': formatted_comments,
        'bids': formatted_bids,
        # Add user context conditionally
        'user': {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        } if request.user.is_authenticated else {
            'first_name': 'Visitor',
            'last_name': ''
        }
    }
    return render(request, 'listing.html', context)


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
            bid_amount = float(data.get('bid_amount', 0))

            # Validate bid amount
            if bid_amount <= 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid bid amount'
                }, status=400)

            # Get current listing
            listing = supabase.table('listings').select('*').eq('id', listing_id).execute()

            if not listing.data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Listing not found'
                }, status=404)

            current_highest_bid = float(listing.data[0].get('highest_bid', 0))

            # Check if bid is higher than current highest
            if bid_amount <= current_highest_bid:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Bid must be higher than current highest bid'
                }, status=400)

            # Record bid in bids table (creating a new bid record)
            supabase.table('bids').insert({
                'listing_id': listing_id,
                'user_email': request.user.email,
                'amount': bid_amount,
                'created_at': datetime.now().isoformat()
            }).execute()

            # Update listing with new highest bid and highest bidder
            supabase.table('listings').update({
                'highest_bid': bid_amount,
                'highest_bidder': request.user.email
            }).eq('id', listing_id).execute()

            return JsonResponse({
                'status': 'success',
                'new_highest_bid': bid_amount,
                'message': 'Bid placed successfully'
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)


def fetch_comments(request, listing_id):
    comments = Comment.objects.filter(listing_id=listing_id).order_by('-created_at')
    comments_data = [
        {
            'user': {
                'first_name': comment.user.first_name,
                'last_name': comment.user.last_name
            },
            'comment': comment.comment,  # Changed from content to comment to match your model
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for comment in comments
    ]
    return JsonResponse({'comments': comments_data})

def create_comment(request, listing_id):
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        if comment_text:
            # For visitors, we'll set commenter_id as NULL
            commenter_id = request.user.id if request.user.is_authenticated else None

            # Insert comment into Supabase
            supabase.table('comments').insert({
                'listing_id': listing_id,
                'commenter_id': commenter_id,
                'comment': comment_text
            }).execute()

            return redirect('listing', id=listing_id)

    return redirect('listing', id=listing_id)