from django.http import HttpResponseForbidden
from django.shortcuts import render

def superuser_access(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("You are not authorized to view this page")
        return view_func(request, *args, **kwargs)
    return wrapper

def visitor_access(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return render(request, 'visitor_message.html', {
            'message': "Your user application has been submitted successfully. Please wait 24 hours for a Superuser to approve/deny your application. Try logging in after 24 hours to find updates. Click here to go to the <a href='{% url 'homepage' %}'>homepage</a>."
        })
    return wrapper