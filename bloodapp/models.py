from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()

class BloodDonation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    donation_date = models.DateTimeField()
    blood_group = models.CharField(max_length=5)
    quantity_ml = models.IntegerField()
    hemoglobin_level = models.FloatField()
    blood_pressure = models.CharField(max_length=20)
    is_processed = models.BooleanField(default=False)
    processed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.donor.username} - {self.donation_date}"

class BloodRequest(models.Model):
    URGENCY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    blood_group = models.CharField(max_length=5)
    units_required = models.IntegerField()
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES)
    hospital_name = models.CharField(max_length=200)
    hospital_address = models.TextField()
    required_date = models.DateField()
    is_fulfilled = models.BooleanField(default=False)
    fulfilled_date = models.DateTimeField(null=True, blank=True)
    patient_name = models.CharField(max_length=200)
    patient_age = models.IntegerField()
    medical_condition = models.TextField()
    
    def __str__(self):
        return f"{self.patient_name} - {self.blood_group}"

class InformationPost(models.Model):
    CATEGORY_CHOICES = (
        ('general', 'General Information'),
        ('donation', 'Blood Donation'),
        ('health', 'Health Tips'),
        ('event', 'Events & Campaigns'),
        ('research', 'Medical Research'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    image = models.ImageField(upload_to='info_posts/', blank=True)

    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('information_detail', args=[self.pk])

    @property
    def excerpt(self):
        return (self.content or '')[:180]



class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    appointment_type = models.CharField(max_length=50)
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.user.username} - {self.appointment_type}"

class BloodInventory(models.Model):
    blood_group = models.CharField(max_length=5, unique=True)
    available_units = models.IntegerField(default=0)
    critical_level = models.IntegerField(default=10)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.blood_group}: {self.available_units} units"
    
    def is_critical(self):
        return self.available_units <= self.critical_level