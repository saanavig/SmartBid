from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User 
from django.conf import settings
#from supabaseClient import create_client 

def create_client():
    SUPABASE_URL = settings.SUPABASE_URL
    SUPABASE_KEY = settings.SUPABASE_KEY
    return create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        if not email or not password:
            return None
        supabase = create_client()

        try:
            # Update to match Supabase's response structure
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if not response.user:
                return None

            # Get or create user with email as username
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=email.split('@')[0],
                    email=email
                )
            return user

        except Exception as e:
            print(f"Supabase authentication failed: {e}")
            return None