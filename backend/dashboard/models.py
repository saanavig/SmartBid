from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password_hash = models.TextField()
    username = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(
        max_length=20,
        default='visitor',
        choices=[('visitor', 'Visitor'), ('user', 'User'), ('super-user', 'Super User')]
    )
    status = models.CharField(max_length=20, default='active')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'users'


class Listing(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.CharField(
        max_length=20,
        choices=[('for-sale', 'For Sale'), ('for-rent', 'For Rent'), ('sold', 'Sold'), ('rented', 'Rented')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'listings'


class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'bids'


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions_as_buyer')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions_as_seller')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[('completed', 'Completed'), ('pending', 'Pending'), ('failed', 'Failed')]
    )
    transaction_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'transactions'


class Rating(models.Model):
    id = models.AutoField(primary_key=True)
    rater_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_received')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'ratings'


class Complaint(models.Model):
    id = models.AutoField(primary_key=True)
    complainant_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints_filed')
    defendant_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints_against')
    complaint_text = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('resolved', 'Resolved')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'complaints'


class UserApplication(models.Model):
    id = models.AutoField(primary_key=True)
    visitor = models.ForeignKey(User, on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)
    arithmetic_question = models.TextField()
    answer = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
    )
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='applications_approved')
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'user_applications'


class VIPStatus(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('expired', 'Expired'), ('pending', 'Pending')]
    )

    class Meta:
        managed = False
        db_table = 'vip_status'
