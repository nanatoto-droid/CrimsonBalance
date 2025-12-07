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
from .forms import InformationPostForm
from django.utils import timezone

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
def donor_appointments(request):
    if request.user.user_type != 'donor':
        messages.error(request, 'Only donors can view appointments.')
        return redirect('home')

    appointments = Appointment.objects.filter(user=request.user).order_by('-scheduled_date')

    total_count = appointments.count()
    confirmed_count = appointments.filter(status='confirmed').count()
    completed_count = appointments.filter(status='completed').count()
    pending_count = appointments.filter(status='pending').count()
    cancelled_count = appointments.filter(status='cancelled').count()

    return render(request, 'bloodapp/donor_appointments.html', {
        'appointments': appointments,
        'total_count': total_count,
        'confirmed_count': confirmed_count,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'cancelled_count': cancelled_count,
    })


@login_required
def recipient_history(request):
    if request.user.user_type != 'recipient':
        messages.error(request, 'Only recipients can view request history.')
        return redirect('home')

    requests = BloodRequest.objects.filter(recipient=request.user).order_by('-required_date')
    fulfilled_count = requests.filter(is_fulfilled=True).count()
    pending_count = requests.filter(is_fulfilled=False).count()

    return render(request, 'bloodapp/recipient_history.html', {
        'requests': requests,
        'fulfilled_count': fulfilled_count,
        'pending_count': pending_count,
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
    featured_posts = InformationPost.objects.filter(is_published=True, is_featured=True).order_by('-created_at')[:3]

    return render(request, 'bloodapp/information_centre.html', {
        'posts': page_obj,
        'categories': categories,
        'active_category': category,
        'search_query': search_query,
        'featured_posts': featured_posts,
    })
    
 
@login_required
def information_create(request):
    # Only doctors and admins can create posts
    if request.user.user_type not in ['doctor', 'admin']:
        messages.error(request, 'Only doctors or admins can create posts.')
        return redirect('information_center')

    if request.method == 'POST':
        form = InformationPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.created_at = timezone.now()
            post.save()
            messages.success(request, 'Information post created.')
            return redirect('information_detail', post.pk)
    else:
        form = InformationPostForm()

    return render(request, 'bloodapp/information_form.html', {'form': form, 'mode': 'create'})


@login_required
def information_edit(request, pk):
    # Only doctors and admins can edit posts
    if request.user.user_type not in ['doctor', 'admin']:
        messages.error(request, 'Only doctors or admins can edit posts.')
        return redirect('information_center')

    post = get_object_or_404(InformationPost, pk=pk)
    if request.method == 'POST':
        form = InformationPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Information post updated.')
            return redirect('information_detail', post.pk)
    else:
        form = InformationPostForm(instance=post)

    return render(request, 'bloodapp/information_form.html', {'form': form, 'mode': 'edit', 'post': post})


@login_required
def information_delete(request, pk):
    # Only doctors and admins can delete posts
    if request.user.user_type not in ['doctor', 'admin']:
        messages.error(request, 'Only doctors or admins can delete posts.')
        return redirect('information_center')

    post = get_object_or_404(InformationPost, pk=pk)
    post.delete()
    messages.success(request, 'Information post deleted.')
    return redirect('information_center')


def information_detail(request, pk):
    # Everyone can view published posts
    post = get_object_or_404(InformationPost, pk=pk)
    if not post.is_published and (not request.user.is_authenticated or request.user.user_type not in ['doctor', 'admin']):
        messages.error(request, 'This post is not published.')
        return redirect('information_center')

    return render(request, 'bloodapp/information_detail.html', {'post': post})



@login_required
def doctor_dashboard(request):
    if request.user.user_type != 'doctor':
        messages.error(request, 'Only doctors can access the doctor dashboard.')
        return redirect('home')

    donations = BloodDonation.objects.all().order_by('-donation_date')
    requests = BloodRequest.objects.all().order_by('-required_date')
    appointments = Appointment.objects.all().order_by('-scheduled_date')
    inventory = BloodInventory.objects.all()

    # Summary counts
    donation_count = donations.count()
    request_count = requests.count()
    appointment_count = appointments.count()
    critical_inventory = inventory.filter(available_units__lte=models.F('critical_level')).count()

    return render(request, 'bloodapp/doctor_dashboard.html', {
        'donations': donations,       
        'requests': requests,         
        'appointments': appointments, 
        'inventory': inventory,
        'donation_count': donation_count,
        'request_count': request_count,
        'appointment_count': appointment_count,
        'critical_inventory': critical_inventory,
    })

@login_required
def process_donation(request, donation_id):
    if request.user.user_type != 'doctor':
        messages.error(request, 'Only doctors can process donations.')
        return redirect('home')

    donation = get_object_or_404(BloodDonation, id=donation_id)
    donation.is_processed = True
    donation.processed_date = timezone.now()
    donation.save()
    messages.success(request, 'Donation marked as processed.')
    return redirect('doctor_dashboard')


@login_required
def fulfill_request(request, request_id):
    if request.user.user_type != 'doctor':
        messages.error(request, 'Only doctors can fulfill requests.')
        return redirect('home')

    req = get_object_or_404(BloodRequest, id=request_id)
    req.is_fulfilled = True
    req.fulfilled_date = timezone.now()
    req.save()
    messages.success(request, 'Request marked as fulfilled.')
    return redirect('doctor_dashboard')


@login_required
def update_appointment_status(request, appointment_id, status):
    if request.user.user_type != 'doctor':
        messages.error(request, 'Only doctors can update appointments.')
        return redirect('home')

    appt = get_object_or_404(Appointment, id=appointment_id)
    appt.status = status
    appt.save()
    messages.success(request, f'Appointment marked as {status}.')
    return redirect('doctor_dashboard')