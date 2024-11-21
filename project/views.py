# views.py
from django.shortcuts import render, redirect
from django.views import View
from .forms import CustomSignupForm

class CustomSignupView(View):
    def get(self, request):
        form = CustomSignupForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('profile')
        return render(request, 'signup.html', {'form': form})
