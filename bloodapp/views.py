from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import *
from accounts.models import CustomUser
from django.core.paginator import Paginator
from datetime import timedelta
from .models import BloodRequest
from django.utils.dateparse import parse_date



def home(request):
    context = {
        'blood_inventory': BloodInventory.objects.all(),
        'recent_posts': InformationPost.objects.filter(is_published=True)[:3],
    }
    
    if request.user.is_authenticated:
        user = request.user
        
        if user.user_type == 'donor':
            context['donation_count'] = BloodDonation.objects.filter(donor=user).count()
            last_donation = BloodDonation.objects.filter(donor=user).order_by('-donation_date').first()
            context['last_donation'] = last_donation.donation_date if last_donation else None
            
        elif user.user_type == 'recipient':
            context['request_count'] = BloodRequest.objects.filter(recipient=user).count()
            context['fulfilled_requests'] = BloodRequest.objects.filter(recipient=user, is_fulfilled=True).count()
    
    return render(request, 'home.html', context)

@login_required
def donation_history(request):
    donations = BloodDonation.objects.filter(donor=request.user).order_by('-donation_date')
    total_ml = sum(d.quantity_ml for d in donations)
    last_donation = donations.first()
    next_eligible = last_donation.donation_date + timedelta(days=56) if last_donation else None

    return render(request, 'bloodapp/donation_history.html', {
        'donations': donations,
        'total_ml': total_ml,
        'next_eligible': next_eligible,
    })



@login_required
def request_blood(request):
    if request.user.user_type != 'recipient':
        messages.error(request, 'Only recipients can request blood.')
        return redirect('home')
    
    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        units_required = request.POST.get('units_required')
        urgency = request.POST.get('urgency')
        hospital_name = request.POST.get('hospital_name')
        hospital_address = request.POST.get('hospital_address')
        required_date = request.POST.get('required_date')
        patient_name = request.POST.get('patient_name')
        patient_age = request.POST.get('patient_age')
        medical_condition = request.POST.get('medical_condition')

        # Validate required fields
        if not all([blood_group, units_required, urgency, hospital_name, hospital_address, required_date, patient_name, patient_age]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('request_blood')

        try:
            # Convert date string into proper date object
            req_date = parse_date(required_date)
            if req_date is None:
                messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
                return redirect('request_blood')

            # Create blood request
            BloodRequest.objects.create(
                recipient=request.user,
                blood_group=blood_group,
                units_required=units_required,
                urgency=urgency,
                hospital_name=hospital_name,
                hospital_address=hospital_address,
                required_date=req_date,
                patient_name=patient_name,
                patient_age=patient_age,
                medical_condition=medical_condition
            )

            messages.success(request, 'Your blood request has been submitted!')
            return redirect('home')

        except Exception as e:
            messages.error(request, f'Error creating blood request: {e}')
            return redirect('request_blood')

    return render(request, 'bloodapp/request_blood.html')


@login_required
def request_appointment(request):
    if request.user.user_type != 'donor':
        messages.error(request, 'Only donors can schedule appointments.')
        return redirect('home')
    
    if request.method == 'POST':
        appointment_type = request.POST.get('appointment_type')
        scheduled_date = request.POST.get('scheduled_date')  
        notes = request.POST.get('notes')

        if not appointment_type or not scheduled_date:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('request_appointment')

        try:
          
            from django.utils.dateparse import parse_datetime
            scheduled_dt = parse_datetime(scheduled_date)
            if scheduled_dt is None:
                messages.error(request, 'Invalid date format. Please use YYYY-MM-DD HH:MM.')
                return redirect('request_appointment')

        
            Appointment.objects.create(
                user=request.user,
                appointment_type=appointment_type,
                scheduled_date=scheduled_dt,
                notes=notes
            )

            messages.success(request, 'Your appointment request has been submitted!')
            return redirect('home')

        except Exception as e:
            messages.error(request, f'Error creating appointment: {e}')
            return redirect('request_appointment')

    return render(request, 'bloodapp/request_appointment.html')



@login_required
def profile(request):
    if request.method == 'POST':
        # Update profile logic
        pass
    
    return render(request, 'accounts/profile.html')



def information_center(request):
    posts = InformationPost.objects.filter(is_published=True).order_by('-created_at')
    
    # Get search query
    search_query = request.GET.get('q', '')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        posts = posts.filter(category=category)
    
    # Get unique categories with counts
    categories = InformationPost.objects.filter(is_published=True).values(
        'category'
    ).annotate(
        count=Count('category')
    ).order_by('category')
    
    # Pagination
    paginator = Paginator(posts, 6)  # Show 6 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'bloodapp/information_centre.html', {
        'posts': page_obj,
        'categories': categories,
        'active_category': category,
        'search_query': search_query,
    })