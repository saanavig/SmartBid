from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from .forms import CustomSignupForm
from django.contrib.auth import login

# Custom Signup View
class CustomSignupView(View):
    def get(self, request):
        form = CustomSignupForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        print(request.POST)  # Log the form data
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save(request)  # Pass request to save method
            login(request, user)
            return redirect('profile')
        else:
            print(form.errors)  # Log form errors
        return render(request, 'signup.html', {'form': form, 'errors': form.errors})

# Homepage View
def homepage(request):
    return render(request, 'homepage.html')

# Profile View (Login Required)
#@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})


#Dashboard View
def dashboard(request):
    return render(request, 'dashboard.html')

#Dashboard's My Account View
def account(request):
    return render(request, 'account.html')

#Dashboard's View Bids
def viewbids(request):
    return render(request, 'viewbids.html')

#Dashboard's Requests
def requests(request):
    return render(request, 'requests.html')
