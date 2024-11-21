from django import forms
from allauth.account.forms import SignupForm

class CustomSignupForm(SignupForm):
        first_name = forms.CharField(max_length=30, label='First Name')
        last_name = forms.CharField(max_length=30, label='Last Name')

        # Override the init method to change the default order of the fields
        def __init__(self, *args, **kwargs):
                super(CustomSignupForm, self).__init__(*args, **kwargs)
                # Reorder the fields
                self.fields['first_name'] = self.fields.pop('first_name')
                self.fields['last_name'] = self.fields.pop('last_name')
                self.fields['email'] = self.fields.pop('email')
                self.fields['username'] = self.fields.pop('username')
                self.fields['password1'] = self.fields.pop('password1')
                self.fields['password2'] = self.fields.pop('password2')
                #self.fields['security'] = self.fields.pop('security')

        def save(self, request):
                user = super(CustomSignupForm, self).save(request)
                user.first_name = self.cleaned_data['first_name']
                user.last_name = self.cleaned_data['last_name']
                user.save()
                return user
