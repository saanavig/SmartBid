from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from supabase import create_client
from datetime import datetime
from dotenv import load_dotenv
import os
import supabase

load_dotenv()


SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@receiver(post_save, sender=User)
def sync_auth_user_to_supabase(sender, instance, created, **kwargs):
        if created:
            auth_user = supabase.table("auth_users").select("id").eq("email", instance.email).execute()
            user_id = auth_user.data[0]['id']

            supabase.table("users").insert({
                "id": user_id,
                "email": instance.email,
                "username": instance.username,
                "first_name": instance.first_name,
                "last_name": instance.last_name,
                "role": "user",
                "status": "active",
                "balance": "0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }).execute()
        else:
            try:
                # Update users record
                supabase.table("users").update({
                    "username": instance.username,
                    "first_name": instance.first_name,
                    "last_name": instance.last_name,
                    "updated_at": datetime.now().isoformat(),
                }).eq("email", instance.email).execute()
            except Exception as e:
                print(f"Error syncing user to Supabase: {str(e)}")
