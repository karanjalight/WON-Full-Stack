from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction, models
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from backend.models import (
    Competition, Subject, Destination, TutorProfile, User, 
    StudentProfile, OlympiadApplication, TravelQuote, ApplicationDocument,
    TravelQuoteItem, SubscriptionPlan, TutorSession, ParentProfile, SchoolProfile
)
from core.forms import (
    ApplicationStep1Form, TravelQuoteForm, StudentRegistrationForm,
    StudentProfileForm, DocumentUploadForm, ApplicationReviewForm,
    TravelQuoteRequestForm, TutorSessionBookingForm, LoginForm, SignupForm
)

# Create your views here.

# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('account')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                next_url = request.GET.get('next', 'account')
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LoginForm()
    
    return render(request, 'frontend/auth/login.html', {'form': form})


def signup_view(request):
    """User signup view with user type selection"""
    if request.user.is_authenticated:
        return redirect('account')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {user.get_full_name() or user.username}!")
            return redirect('account')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignupForm()
    
    return render(request, 'frontend/auth/signup.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')


@login_required
def account_view(request):
    """User account page showing profile details"""
    user = request.user
    
    # Get user-specific profile data
    profile_data = {}
    
    if user.user_type == 'student':
        try:
            profile = user.student_profile
            profile_data = {
                'date_of_birth': profile.date_of_birth,
                'grade_level': profile.grade_level,
                'current_school': profile.current_school,
                'interests': profile.interests,
                'achievements': profile.achievements,
                'guardian_name': profile.guardian_name,
                'guardian_email': profile.guardian_email,
                'guardian_phone': profile.guardian_phone,
                'passport_number': profile.passport_number,
                'passport_expiry': profile.passport_expiry,
            }
        except StudentProfile.DoesNotExist:
            pass
    elif user.user_type == 'parent':
        try:
            profile = user.parent_profile
            profile_data = {
                'occupation': profile.occupation,
                'number_of_children': profile.number_of_children,
                'emergency_contact': profile.emergency_contact,
                'preferred_contact_method': profile.preferred_contact_method,
            }
        except ParentProfile.DoesNotExist:
            pass
    elif user.user_type == 'school':
        try:
            profile = user.school_profile
            profile_data = {
                'school_name': profile.school_name,
                'registration_number': profile.registration_number,
                'school_type': profile.school_type,
                'principal_name': profile.principal_name,
                'principal_email': profile.principal_email,
                'website': profile.website,
                'total_students': profile.total_students,
                'active_olympiad_students': profile.active_olympiad_students,
                'is_verified': profile.is_verified,
            }
        except SchoolProfile.DoesNotExist:
            pass
    elif user.user_type == 'tutor':
        try:
            profile = user.tutor_profile
            profile_data = {
                'title': profile.title,
                'specializations': profile.specializations,
                'qualifications': profile.qualifications,
                'hourly_rate': profile.hourly_rate,
                'currency': profile.currency,
                'average_rating': profile.average_rating,
                'total_reviews': profile.total_reviews,
                'is_accepting_students': profile.is_accepting_students,
            }
        except:
            pass
    
    # Get user's applications
    applications = OlympiadApplication.objects.filter(student=user).order_by('-created_at')[:5] if user.user_type == 'student' else []
    
    # Get user's travel quotes
    travel_quotes = TravelQuote.objects.filter(user=user).order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'profile_data': profile_data,
        'applications': applications,
        'travel_quotes': travel_quotes,
    }
    
    return render(request, 'frontend/auth/account.html', context)


def index(request):
    """Landing page view"""
    return render(request, 'frontend/index.html')

def about(request):
    """About page view"""
    return render(request, 'frontend/about.html')

def contact(request):
    """Contact page view"""
    return render(request, 'frontend/contact.html')

def destination(request):
    """Destinations listing page view with filtering and pagination"""
    # Get filter parameters from request
    region = request.GET.get('region', '')
    search_query = request.GET.get('search', '')
    
    # Start with active destinations
    destinations_list = Destination.objects.filter(is_active=True).prefetch_related('competitions')
    
    # Apply filters
    if region:
        destinations_list = destinations_list.filter(region=region)
    
    if search_query:
        destinations_list = destinations_list.filter(
            name__icontains=search_query
        ) | destinations_list.filter(
            city__icontains=search_query
        ) | destinations_list.filter(
            country__icontains=search_query
        ) | destinations_list.filter(
            description__icontains=search_query
        )
    
    # Order by region, then country, then city
    destinations_list = destinations_list.order_by('region', 'country', 'city')
    
    # Pagination
    paginator = Paginator(destinations_list, 12)  # Show 12 destinations per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Enrich destinations with additional data for cards (after pagination)
    enriched_destinations = []
    for dest in page_obj:
        # Get competitions for this destination
        competitions = dest.competitions.filter(is_active=True)
        
        # Calculate date range from competitions
        date_range = None
        if competitions.exists():
            start_dates = [c.start_date for c in competitions if c.start_date]
            if start_dates:
                min_date = min(start_dates)
                end_dates = [c.end_date for c in competitions if c.end_date]
                max_date = max(end_dates) if end_dates else min_date
                if min_date and max_date:
                    if min_date.year == max_date.year:
                        if min_date.month == max_date.month:
                            date_range = min_date.strftime('%B %Y')
                        else:
                            date_range = f"{min_date.strftime('%B')} - {max_date.strftime('%B %Y')}"
                    else:
                        date_range = f"{min_date.strftime('%B %Y')} - {max_date.strftime('%B %Y')}"
        
        # Get cities in the same region (for region-based display)
        region_cities = Destination.objects.filter(
            region=dest.region,
            is_active=True
        ).exclude(id=dest.id).values_list('city', flat=True)[:2]
        cities_list = [dest.city] + list(region_cities)
        cities_display = ", ".join(cities_list[:3])  # Show up to 3 cities
        
        enriched_destinations.append({
            'destination': dest,
            'date_range': date_range,
            'cities_display': cities_display,
            'competitions_count': competitions.count(),
        })
    
    # Create a custom page object-like structure
    class EnrichedPage:
        def __init__(self, items, original_page):
            self.items = items
            self.number = original_page.number
            self.paginator = original_page.paginator
            self.has_previous = original_page.has_previous()
            self.has_next = original_page.has_next()
            self.previous_page_number = original_page.previous_page_number() if self.has_previous else None
            self.next_page_number = original_page.next_page_number() if self.has_next else None
        
        def __iter__(self):
            return iter(self.items)
        
        def __len__(self):
            return len(self.items)
    
    enriched_page = EnrichedPage(enriched_destinations, page_obj)
    
    # Get all regions for filter dropdown
    regions = Destination.objects.filter(is_active=True).values_list('region', flat=True).distinct()
    region_choices = Destination.REGION_CHOICES
    
    context = {
        'destinations': enriched_page,
        'search_query': search_query,
        'current_region': region,
        'regions': regions,
        'region_choices': region_choices,
    }
    
    return render(request, 'frontend/destination.html', context)

def subjects(request):
    """Subjects listing page view with filtering"""
    # Get filter parameters from request
    search_query = request.GET.get('search', '')
    
    # Start with active subjects
    subjects_list = Subject.objects.filter(is_active=True)
    
    # Apply search filter
    if search_query:
        subjects_list = subjects_list.filter(
            name__icontains=search_query
        ) | subjects_list.filter(
            description__icontains=search_query
        )
    
    # Order by display_order, then by name
    subjects_list = subjects_list.order_by('display_order', 'name')
    
    # Pagination
    paginator = Paginator(subjects_list, 12)  # Show 12 subjects per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'subjects': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'frontend/subjects.html', context)

def subject_details(request, slug):
    """Subject details page view with comprehensive information"""
    subject = get_object_or_404(
        Subject.objects.prefetch_related('competitions', 'tutors__tutor__user'),
        slug=slug,
        is_active=True
    )
    
    # Get related competitions (active, ordered by date)
    competitions = Competition.objects.filter(
        subject=subject,
        is_active=True
    ).select_related('subject', 'destination').order_by('-is_featured', 'start_date', 'application_deadline')[:12]
    
    # Get tutors for this subject
    tutors = TutorProfile.objects.filter(
        subjects__subject=subject,
        is_accepting_students=True,
        user__is_active=True
    ).select_related('user').prefetch_related('subjects').distinct().order_by('-is_featured', '-average_rating')[:12]
    
    # Get unique destinations through competitions
    destinations = Destination.objects.filter(
        competitions__subject=subject,
        competitions__is_active=True
    ).distinct().order_by('country', 'city')[:12]
    
    # Get related subjects (other active subjects)
    related_subjects = Subject.objects.filter(
        is_active=True
    ).exclude(id=subject.id).order_by('display_order', 'name')[:6]
    
    context = {
        'subject': subject,
        'competitions': competitions,
        'tutors': tutors,
        'destinations': destinations,
        'related_subjects': related_subjects,
    }
    
    return render(request, 'frontend/subject-details.html', context)

def destination_details(request, slug):
    """Destination details page view"""
    destination = get_object_or_404(
        Destination.objects.prefetch_related('competitions__subject'),
        slug=slug,
        is_active=True
    )
    
    # Get related competitions for this destination
    competitions = Competition.objects.filter(
        destination=destination,
        is_active=True
    ).select_related('subject', 'destination').order_by('-is_featured', 'start_date')[:6]
    
    # Get related destinations (same region, excluding current)
    related_destinations = Destination.objects.filter(
        region=destination.region,
        is_active=True
    ).exclude(id=destination.id).order_by('country', 'city')[:6]
    
    # Generate Google Maps embed URL if iframe_url is not provided
    map_url = destination.iframe_url
    if not map_url:
        # Generate Google Maps embed URL from city and country
        # Using standard Google Maps embed format (works without API key)
        from urllib.parse import quote
        location_query = f"{destination.city}, {destination.country}"
        map_url = f"https://maps.google.com/maps?q={quote(location_query)}&t=&z=13&ie=UTF8&iwloc=&output=embed"
    
    context = {
        'destination': destination,
        'competitions': competitions,
        'related_destinations': related_destinations,
        'map_url': map_url,
    }
    
    return render(request, 'frontend/destination-details.html', context)

def faq(request):
    """FAQ page view"""
    return render(request, 'frontend/faq.html')

def news(request):
    """News listing page view"""
    return render(request, 'frontend/news.html')

def news_details(request):
    """News details page view"""
    return render(request, 'frontend/news-details.html')

def team(request):
    """Tutors listing page view with filtering and pagination"""
    # Get filter parameters from request
    subject_slug = request.GET.get('subject', '')
    search_query = request.GET.get('search', '')
    min_rate = request.GET.get('min_rate', '')
    max_rate = request.GET.get('max_rate', '')
    sort_by = request.GET.get('sort', 'featured')  # featured, rating, rate_low, rate_high
    
    # Start with active tutors who are accepting students
    tutors_list = TutorProfile.objects.filter(
        is_accepting_students=True,
        user__is_active=True
    ).select_related('user').prefetch_related('subjects__subject')
    
    # Apply filters
    if subject_slug:
        tutors_list = tutors_list.filter(subjects__subject__slug=subject_slug)
    
    if search_query:
        tutors_list = tutors_list.filter(
            user__first_name__icontains=search_query
        ) | tutors_list.filter(
            user__last_name__icontains=search_query
        ) | tutors_list.filter(
            user__username__icontains=search_query
        ) | tutors_list.filter(
            title__icontains=search_query
        ) | tutors_list.filter(
            specializations__icontains=search_query
        ) | tutors_list.filter(
            qualifications__icontains=search_query
        )
    
    if min_rate:
        try:
            tutors_list = tutors_list.filter(hourly_rate__gte=float(min_rate))
        except ValueError:
            pass
    
    if max_rate:
        try:
            tutors_list = tutors_list.filter(hourly_rate__lte=float(max_rate))
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'rating':
        tutors_list = tutors_list.order_by('-average_rating', '-total_reviews')
    elif sort_by == 'rate_low':
        tutors_list = tutors_list.order_by('hourly_rate')
    elif sort_by == 'rate_high':
        tutors_list = tutors_list.order_by('-hourly_rate')
    else:  # featured (default)
        tutors_list = tutors_list.order_by('-is_featured', '-average_rating', '-total_reviews')
    
    # Remove duplicates
    tutors_list = tutors_list.distinct()
    
    # Pagination
    paginator = Paginator(tutors_list, 12)  # Show 12 tutors per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all subjects for filter
    subjects = Subject.objects.filter(is_active=True).order_by('name')
    
    # Get rate range for filter
    from django.db.models import Min, Max
    rate_range = tutors_list.aggregate(
        min_rate=Min('hourly_rate'),
        max_rate=Max('hourly_rate')
    )
    
    context = {
        'tutors': page_obj,
        'subjects': subjects,
        'current_subject': subject_slug,
        'search_query': search_query,
        'min_rate': min_rate,
        'max_rate': max_rate,
        'sort_by': sort_by,
        'rate_range': rate_range,
    }
    
    return render(request, 'frontend/team.html', context)

def team_details(request, pk):
    """Tutor details page view"""
    tutor = get_object_or_404(
        TutorProfile.objects.select_related('user').prefetch_related('subjects__subject'),
        user__id=pk,
        user__is_active=True
    )
    
    # Get tutor's subjects
    tutor_subjects = tutor.subjects.all().select_related('subject')
    
    # Get related tutors (same subjects, excluding current)
    related_tutors = TutorProfile.objects.filter(
        subjects__subject__in=[ts.subject for ts in tutor_subjects],
        is_accepting_students=True,
        user__is_active=True
    ).exclude(user__id=pk).select_related('user').distinct().order_by('-is_featured', '-average_rating')[:6]
    
    context = {
        'tutor': tutor,
        'tutor_subjects': tutor_subjects,
        'related_tutors': related_tutors,
    }
    
    return render(request, 'frontend/team-details.html', context)

def book_tutor_session(request, pk):
    """Book a tutor session"""
    tutor = get_object_or_404(
        TutorProfile.objects.select_related('user'),
        user__id=pk,
        is_accepting_students=True,
        user__is_active=True
    )
    
    # Get tutor's subjects for the form
    tutor_subjects = tutor.subjects.all().select_related('subject')
    subject_ids = [ts.subject.id for ts in tutor_subjects]
    
    if request.method == 'POST':
        form = TutorSessionBookingForm(request.POST)
        # Limit subject choices to tutor's subjects
        form.fields['subject'].queryset = Subject.objects.filter(id__in=subject_ids, is_active=True)
        form.fields['tutor'].initial = tutor
        
        if form.is_valid():
            # Get or create student user
            student = None
            if request.user.is_authenticated and request.user.user_type == 'student':
                student = request.user
            else:
                # For non-authenticated users, we'll need to create a guest booking
                # or prompt them to register. For now, we'll use a placeholder
                # In production, you might want to create a guest user or require registration
                messages.warning(request, "Please log in as a student to book a session.")
                return redirect('book-tutor-session', pk=pk)
            
            # Calculate amount
            duration_minutes = int(form.cleaned_data['duration_minutes'])
            hourly_rate = tutor.hourly_rate
            amount = (hourly_rate * duration_minutes) / 60
            
            # Create session
            session = TutorSession.objects.create(
                tutor=tutor,
                student=student,
                subject=form.cleaned_data['subject'],
                scheduled_at=form.cleaned_data['scheduled_at'],
                duration_minutes=duration_minutes,
                topic=form.cleaned_data.get('topic', ''),
                description=form.cleaned_data.get('description', ''),
                amount=amount,
                currency=tutor.currency,
                status='scheduled',
                payment_status='pending'
            )
            
            # Update tutor's total sessions count
            tutor.total_sessions += 1
            tutor.save(update_fields=['total_sessions'])
            
            messages.success(request, f"Session booked successfully! Session number: {session.session_number}")
            return redirect('tutor-session-confirmation', session_id=session.id)
    else:
        form = TutorSessionBookingForm(initial={'tutor': tutor})
        # Limit subject choices to tutor's subjects
        form.fields['subject'].queryset = Subject.objects.filter(id__in=subject_ids, is_active=True)
    
    context = {
        'tutor': tutor,
        'form': form,
        'tutor_subjects': tutor_subjects,
    }
    
    return render(request, 'frontend/book-tutor-session.html', context)

def tutor_session_confirmation(request, session_id):
    """Tutor session booking confirmation page"""
    session = get_object_or_404(
        TutorSession.objects.select_related('tutor__user', 'student', 'subject'),
        id=session_id
    )
    
    # Verify user has access to this session
    if request.user.is_authenticated:
        if request.user != session.student and not request.user.is_staff:
            messages.error(request, "You don't have permission to view this session.")
            return redirect('index')
    else:
        # For guest bookings, you might want to store session_id in session
        # For now, we'll allow viewing if they have the link
        pass
    
    context = {
        'session': session,
    }
    
    return render(request, 'frontend/tutor-session-confirmation.html', context)

def tour(request):
    """Tours listing page view (Competitions)"""
    return render(request, 'frontend/tour.html')

def tour_2(request):
    """Tours alternative listing page view"""
    return render(request, 'frontend/tour-2.html')

def tour_details(request, slug):
    """Tour details page view (Competition details) - DEPRECATED, use olympiad_details"""
    return olympiad_details(request, slug)

def olympiad_details(request, slug):
    """Olympiad details page view"""
    competition = get_object_or_404(
        Competition.objects.select_related('subject', 'destination'),
        slug=slug,
        is_active=True
    )
    
    # Get related competitions (same subject, excluding current)
    related_competitions = Competition.objects.filter(
        subject=competition.subject,
        is_active=True
    ).exclude(id=competition.id).order_by('-is_featured', 'start_date')[:6]
    
    # Get tutors for this subject
    tutors = TutorProfile.objects.filter(
        subjects__subject=competition.subject,
        is_accepting_students=True,
        user__is_active=True
    ).select_related('user').distinct().order_by('-is_featured', '-average_rating')[:6]
    
    context = {
        'competition': competition,
        'related_competitions': related_competitions,
        'tutors': tutors,
    }
    
    return render(request, 'frontend/olympiad-details.html', context)

def tour_list(request):
    """Tours list page view"""
    return render(request, 'frontend/tour-list.html')

def olympiads(request):
    """Olympiads listing page view"""
    # Get filter parameters from request
    subject_slug = request.GET.get('subject')
    location = request.GET.get('location')
    search_query = request.GET.get('search')
    
    # Start with active competitions
    competitions = Competition.objects.filter(is_active=True).select_related('subject', 'destination')
    
    # Apply filters
    if subject_slug:
        competitions = competitions.filter(subject__slug=subject_slug)
    
    if location:
        competitions = competitions.filter(destination__city__icontains=location) | \
                      competitions.filter(destination__country__icontains=location)
    
    if search_query:
        competitions = competitions.filter(
            name__icontains=search_query
        ) | competitions.filter(
            description__icontains=search_query
        )
    
    # Order by featured first, then by application deadline
    competitions = competitions.order_by('-is_featured', 'application_deadline', 'start_date')
    
    # Pagination
    paginator = Paginator(competitions, 12)  # Show 12 competitions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all subjects and destinations for filters
    subjects = Subject.objects.filter(is_active=True).order_by('name')
    destinations = Destination.objects.filter(is_active=True).order_by('country', 'city')
    
    context = {
        'competitions': page_obj,
        'subjects': subjects,
        'destinations': destinations,
        'current_subject': subject_slug,
        'current_location': location,
        'search_query': search_query,
    }
    
    return render(request, 'frontend/olympiads.html', context)

def error_404(request, exception=None):
    """Custom 404 error page view"""
    return render(request, 'frontend/404.html', status=404)


# ============================================================================
# OLYMPIAD APPLICATION FLOW
# ============================================================================

def start_application(request, slug):
    """Start application process - redirects to step 1"""
    competition = get_object_or_404(Competition, slug=slug, is_active=True)
    
    # Check if application is open
    if not competition.is_application_open():
        messages.error(request, "Applications for this competition are currently closed.")
        return redirect('olympiad-details', slug=slug)
    
    # Initialize session data
    request.session['application_data'] = {
        'competition_id': str(competition.id),
        'step': 1,
    }
    
    return redirect('application-step', step=1)


def application_step(request, step):
    """Handle multi-step application process"""
    # Get application data from session
    app_data = request.session.get('application_data', {})
    
    if not app_data or 'competition_id' not in app_data:
        messages.error(request, "Please start a new application.")
        return redirect('olympiads')
    
    competition = get_object_or_404(Competition, id=app_data['competition_id'], is_active=True)
    
    # Check if application is still open
    if not competition.is_application_open():
        messages.error(request, "Applications for this competition are currently closed.")
        return redirect('olympiad-details', slug=competition.slug)
    
    step = int(step)
    total_steps = 7
    
    # Handle form submissions
    if request.method == 'POST':
        if step == 1:
            form = ApplicationStep1Form(request.POST)
            if form.is_valid():
                app_data.update({
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name'],
                    'email': form.cleaned_data['email'],
                    'phone': form.cleaned_data['phone'],
                    'date_of_birth': form.cleaned_data['date_of_birth'].isoformat(),
                    'emergency_contact_name': form.cleaned_data['emergency_contact_name'],
                    'emergency_contact_phone': form.cleaned_data['emergency_contact_phone'],
                    'motivation_letter': form.cleaned_data.get('motivation_letter', ''),
                    'special_requirements': form.cleaned_data.get('special_requirements', ''),
                    'step': 2,
                })
                request.session['application_data'] = app_data
                return redirect('application-step', step=2)
        
        elif step == 2:
            form = TravelQuoteForm(request.POST)
            if form.is_valid():
                # Generate travel quote
                quote_data = {
                    'departure_city': form.cleaned_data['departure_city'],
                    'departure_country': form.cleaned_data['departure_country'],
                    'departure_date': form.cleaned_data['departure_date'].isoformat(),
                    'return_date': form.cleaned_data['return_date'].isoformat(),
                    'number_of_passengers': form.cleaned_data['number_of_passengers'],
                    'special_requests': form.cleaned_data.get('special_requests', ''),
                }
                app_data['travel_quote'] = quote_data
                app_data['step'] = 3
                request.session['application_data'] = app_data
                return redirect('application-step', step=3)
        
        elif step == 3:
            # Check if user is logged in
            if request.user.is_authenticated:
                app_data['user_id'] = str(request.user.id)
                app_data['step'] = 4
                request.session['application_data'] = app_data
                return redirect('application-step', step=4)
            else:
                # Handle registration
                reg_form = StudentRegistrationForm(request.POST)
                if reg_form.is_valid():
                    user = reg_form.save()
                    # Update user with data from step 1
                    user.first_name = app_data.get('first_name', '')
                    user.last_name = app_data.get('last_name', '')
                    user.email = app_data.get('email', '')
                    user.phone = app_data.get('phone', '')
                    user.save()
                    
                    # Create or update student profile
                    student_profile, created = StudentProfile.objects.get_or_create(user=user)
                    if app_data.get('date_of_birth'):
                        student_profile.date_of_birth = datetime.fromisoformat(app_data['date_of_birth']).date()
                        student_profile.save()
                    
                    # Auto login
                    login(request, user)
                    app_data['user_id'] = str(user.id)
                    app_data['step'] = 4
                    request.session['application_data'] = app_data
                    messages.success(request, "Account created successfully!")
                    return redirect('application-step', step=4)
                else:
                    form = reg_form
                    return render(request, 'frontend/application/step3.html', {
                        'form': form,
                        'competition': competition,
                        'step': step,
                        'total_steps': total_steps,
                        'app_data': app_data,
                    })
        
        elif step == 4:
            if not request.user.is_authenticated:
                messages.error(request, "Please log in to continue.")
                return redirect('application-step', step=3)
            
            # Create student profile if it doesn't exist
            student_profile, created = StudentProfile.objects.get_or_create(user=request.user)
            profile_form = StudentProfileForm(request.POST, instance=student_profile)
            if profile_form.is_valid():
                profile_form.save()
                app_data['step'] = 5
                request.session['application_data'] = app_data
                return redirect('application-step', step=5)
            else:
                form = profile_form
                return render(request, 'frontend/application/step4.html', {
                    'form': form,
                    'competition': competition,
                    'step': step,
                    'total_steps': total_steps,
                    'app_data': app_data,
                })
        
        elif step == 5:
            # Document upload - handled via AJAX or separate view
            app_data['step'] = 6
            request.session['application_data'] = app_data
            return redirect('application-step', step=6)
        
        elif step == 6:
            review_form = ApplicationReviewForm(request.POST)
            if review_form.is_valid():
                app_data['step'] = 7
                request.session['application_data'] = app_data
                return redirect('application-step', step=7)
            else:
                form = review_form
                return render(request, 'frontend/application/step6.html', {
                    'form': form,
                    'competition': competition,
                    'step': step,
                    'total_steps': total_steps,
                    'app_data': app_data,
                })
        
        elif step == 7:
            # Final submission
            return submit_application(request)
    
    # Render appropriate step form
    if step == 1:
        # Pre-fill form if data exists
        initial = {}
        if app_data.get('first_name'):
            initial = {
                'first_name': app_data.get('first_name'),
                'last_name': app_data.get('last_name'),
                'email': app_data.get('email'),
                'phone': app_data.get('phone'),
                'emergency_contact_name': app_data.get('emergency_contact_name'),
                'emergency_contact_phone': app_data.get('emergency_contact_phone'),
                'motivation_letter': app_data.get('motivation_letter'),
                'special_requirements': app_data.get('special_requirements'),
            }
        form = ApplicationStep1Form(initial=initial)
        form.fields['competition'].initial = competition
    
    elif step == 2:
        initial = {}
        if app_data.get('travel_quote'):
            quote = app_data['travel_quote']
            initial = {
                'departure_city': quote.get('departure_city'),
                'departure_country': quote.get('departure_country'),
                'number_of_passengers': quote.get('number_of_passengers', 1),
                'special_requests': quote.get('special_requests'),
            }
        form = TravelQuoteForm(initial=initial)
    
    elif step == 3:
        if request.user.is_authenticated:
            app_data['user_id'] = str(request.user.id)
            app_data['step'] = 4
            request.session['application_data'] = app_data
            return redirect('application-step', step=4)
        form = StudentRegistrationForm()
    
    elif step == 4:
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to continue.")
            return redirect('application-step', step=3)
        # Create student profile if it doesn't exist
        student_profile, created = StudentProfile.objects.get_or_create(user=request.user)
        form = StudentProfileForm(instance=student_profile)
    
    elif step == 5:
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to continue.")
            return redirect('application-step', step=3)
        form = None  # Documents handled separately
    
    elif step == 6:
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to continue.")
            return redirect('application-step', step=3)
        form = ApplicationReviewForm()
    
    elif step == 7:
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to continue.")
            return redirect('application-step', step=3)
        # Step 7 shows processing and auto-submits
        # The actual submission happens via POST to submit_application
        if request.method == 'POST':
            return submit_application(request)
        form = None  # Payment/submission
    
    else:
        messages.error(request, "Invalid step.")
        return redirect('olympiads')
    
    template = f'frontend/application/step{step}.html'
    return render(request, template, {
        'form': form,
        'competition': competition,
        'step': step,
        'total_steps': total_steps,
        'app_data': app_data,
    })


@transaction.atomic
def submit_application(request):
    """Final step: Submit the application"""
    app_data = request.session.get('application_data', {})
    
    if not app_data or not request.user.is_authenticated:
        messages.error(request, "Please complete all steps.")
        return redirect('olympiads')
    
    competition = get_object_or_404(Competition, id=app_data['competition_id'])
    
    try:
        # Create or update application
        application, created = OlympiadApplication.objects.get_or_create(
            student=request.user,
            competition=competition,
            defaults={
                'status': 'draft',
                'motivation_letter': app_data.get('motivation_letter', ''),
                'special_requirements': app_data.get('special_requirements', ''),
                'emergency_contact_name': app_data.get('emergency_contact_name', ''),
                'emergency_contact_phone': app_data.get('emergency_contact_phone', ''),
                'total_cost': competition.base_price,
            }
        )
        
        if not created:
            # Update existing application
            application.motivation_letter = app_data.get('motivation_letter', '')
            application.special_requirements = app_data.get('special_requirements', '')
            application.emergency_contact_name = app_data.get('emergency_contact_name', '')
            application.emergency_contact_phone = app_data.get('emergency_contact_phone', '')
            application.save()
        
        # Create travel quote if provided
        if app_data.get('travel_quote'):
            quote_data = app_data['travel_quote']
            TravelQuote.objects.create(
                user=request.user,
                application=application,
                destination=competition.destination,
                departure_city=quote_data['departure_city'],
                departure_country=quote_data['departure_country'],
                departure_date=datetime.fromisoformat(quote_data['departure_date']).date(),
                return_date=datetime.fromisoformat(quote_data['return_date']).date(),
                number_of_passengers=quote_data['number_of_passengers'],
                special_requests=quote_data.get('special_requests', ''),
                status='generated',
                quote_valid_until=competition.start_date,
            )
        
        # Mark as submitted
        application.status = 'submitted'
        application.submitted_at = timezone.now()
        application.save()
        
        # Clear session data
        del request.session['application_data']
        
        messages.success(request, f"Application submitted successfully! Your application number is {application.application_number}.")
        return redirect('application-success', application_id=str(application.id))
    
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('application-step', step=6)


def application_success(request, application_id):
    """Application submission success page"""
    application = get_object_or_404(OlympiadApplication, id=application_id, student=request.user)
    return render(request, 'frontend/application/success.html', {
        'application': application,
    })


def upload_document(request):
    """Handle document upload via AJAX"""
    if request.method == 'POST' and request.user.is_authenticated:
        app_data = request.session.get('application_data', {})
        if not app_data:
            return JsonResponse({'error': 'No active application'}, status=400)
        
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Get or create application
            competition = get_object_or_404(Competition, id=app_data['competition_id'])
            application, _ = OlympiadApplication.objects.get_or_create(
                student=request.user,
                competition=competition,
                defaults={'status': 'draft'}
            )
            
            document = form.save(commit=False)
            document.application = application
            document.status = 'uploaded'
            document.uploaded_at = timezone.now()
            if request.FILES.get('file'):
                document.file_size = request.FILES['file'].size
            document.save()
            
            return JsonResponse({
                'success': True,
                'document_id': str(document.id),
                'message': 'Document uploaded successfully'
            })
        else:
            return JsonResponse({'error': 'Invalid form data'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def download_quotation_pdf(request, application_id):
    """Generate and download quotation PDF for application"""
    application = get_object_or_404(OlympiadApplication, id=application_id, student=request.user)
    
    # Create a BytesIO buffer for the PDF
    buffer = BytesIO()
    
    # Create the PDF object
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        leading=14
    )
    
    # Title
    title = Paragraph("TRAVEL QUOTATION", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Company info header
    company_info = [
        ['<b>readtrips</b>', ''],
        ['Travel & Tour Services', ''],
        ['Nairobi, Kenya', ''],
        ['Email: info@readtrips.com', ''],
        ['Phone: +254 700 000 000', ''],
    ]
    
    company_table = Table(company_info, colWidths=[4*inch, 2*inch])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 16),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Quotation details
    quotation_date = application.submitted_at.strftime('%B %d, %Y') if application.submitted_at else timezone.now().strftime('%B %d, %Y')
    
    quotation_info = [
        ['<b>Quotation Number:</b>', application.application_number or 'N/A'],
        ['<b>Date:</b>', quotation_date],
        ['<b>Valid Until:</b>', (timezone.now() + timezone.timedelta(days=30)).strftime('%B %d, %Y')],
    ]
    
    quotation_table = Table(quotation_info, colWidths=[2.5*inch, 3.5*inch])
    quotation_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(quotation_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Customer Information
    customer_heading = Paragraph("Customer Information", heading_style)
    elements.append(customer_heading)
    
    student = application.student
    customer_info = [
        ['<b>Name:</b>', student.get_full_name() or student.username],
        ['<b>Email:</b>', student.email],
        ['<b>Application Number:</b>', application.application_number or 'N/A'],
    ]
    
    customer_table = Table(customer_info, colWidths=[2.5*inch, 3.5*inch])
    customer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Competition/Tour Details
    competition_heading = Paragraph("Competition/Tour Details", heading_style)
    elements.append(competition_heading)
    
    competition = application.competition
    competition_info = [
        ['<b>Competition:</b>', competition.name],
        ['<b>Subject:</b>', competition.subject.name if competition.subject else 'N/A'],
        ['<b>Destination:</b>', f"{competition.destination.city}, {competition.destination.country}" if competition.destination else 'N/A'],
        ['<b>Round:</b>', application.round.name if application.round else 'N/A'],
        ['<b>Status:</b>', application.get_status_display()],
    ]
    
    competition_table = Table(competition_info, colWidths=[2.5*inch, 3.5*inch])
    competition_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(competition_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Pricing Information
    pricing_heading = Paragraph("Pricing Information", heading_style)
    elements.append(pricing_heading)
    
    pricing_data = [
        ['<b>Description</b>', '<b>Amount</b>'],
        ['Total Cost', f"KES {application.total_cost:,.2f}"],
    ]
    
    pricing_table = Table(pricing_data, colWidths=[4*inch, 2*inch])
    pricing_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]))
    elements.append(pricing_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Additional Notes
    if application.special_requirements:
        notes_heading = Paragraph("Special Requirements", heading_style)
        elements.append(notes_heading)
        notes_para = Paragraph(application.special_requirements, normal_style)
        elements.append(notes_para)
        elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_text = Paragraph(
        "<i>This quotation is valid for 30 days from the date of issue. "
        "For any inquiries, please contact us at info@readtrips.com or +254 700 000 000.</i>",
        ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceBefore=20
        )
    )
    elements.append(footer_text)
    
    # Build PDF with watermark
    class WatermarkedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            self.pages = []
        
        def showPage(self):
            self.pages.append(dict(self.__dict__))
            self._startPage()
        
        def save(self):
            page_count = len(self.pages)
            for page in self.pages:
                self.__dict__.update(page)
                self.draw_watermark()
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)
        
        def draw_watermark(self):
            self.saveState()
            # Set watermark properties
            self.setFont('Helvetica-Bold', 60)
            # Use gray color with transparency effect (light gray)
            self.setFillColorRGB(0.88, 0.88, 0.88)  # #e0e0e0 equivalent
            
            # Rotate and position watermark
            self.translate(A4[0]/2, A4[1]/2)
            self.rotate(45)
            self.drawCentredString(0, 0, 'readtrips')
            self.restoreState()
            
            # Add footer with contact info
            self.saveState()
            self.setFont('Helvetica', 8)
            self.setFillColor(colors.HexColor('#666666'))
            
            footer_text = "readtrips | Nairobi, Kenya | Email: info@readtrips.com | Phone: +254 700 000 000"
            text_width = self.stringWidth(footer_text, 'Helvetica', 8)
            self.drawString((A4[0] - text_width) / 2, 30, footer_text)
            self.restoreState()
    
    # Build PDF
    doc.build(elements, canvasmaker=WatermarkedCanvas)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quotation_{application.application_number}.pdf"'
    response.write(pdf)
    
    return response


# ============================================================================
# TRAVEL QUOTE GENERATION
# ============================================================================

def generate_travel_quote(request, slug=None):
    """Generate travel quote for a destination"""
    destination = None
    if slug:
        destination = get_object_or_404(Destination, slug=slug, is_active=True)
    
    quote = None
    form = TravelQuoteRequestForm()
    
    if request.method == 'POST':
        form = TravelQuoteRequestForm(request.POST)
        if form.is_valid():
            # Get or create user (if not authenticated, create a guest user or use email)
            user = None
            if request.user.is_authenticated:
                user = request.user
            else:
                # Try to find user by email, or create a guest record
                email = form.cleaned_data['email']
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    # Create a temporary user for the quote
                    # In production, you might want to handle this differently
                    user = User.objects.create_user(
                        username=f"guest_{email.split('@')[0]}_{timezone.now().timestamp()}",
                        email=email,
                        first_name=form.cleaned_data['full_name'].split()[0] if form.cleaned_data['full_name'] else '',
                        last_name=' '.join(form.cleaned_data['full_name'].split()[1:]) if len(form.cleaned_data['full_name'].split()) > 1 else '',
                        phone=form.cleaned_data['phone'],
                        user_type='parent',  # Default to parent for quote requests
                        is_active=False  # Mark as inactive until they register
                    )
            
            # Get destination from form or URL
            if not destination:
                # You might want to add a destination field to the form
                # For now, we'll use the one from URL
                messages.error(request, "Please select a destination.")
                return redirect('destination')
            
            # Calculate quote validity (30 days from now)
            quote_valid_until = timezone.now().date() + timedelta(days=30)
            
            # Create travel quote
            quote = TravelQuote.objects.create(
                user=user,
                destination=destination,
                departure_city=form.cleaned_data['departure_city'],
                departure_country=form.cleaned_data['departure_country'],
                departure_date=form.cleaned_data['departure_date'],
                return_date=form.cleaned_data['return_date'],
                number_of_passengers=form.cleaned_data['number_of_passengers'],
                special_requests=form.cleaned_data.get('special_requests', ''),
                quote_valid_until=quote_valid_until,
                status='generated',
                currency=destination.currency or 'USD',
            )
            
            # Calculate base costs (simplified pricing logic)
            # In production, you'd integrate with actual pricing APIs
            days = (quote.return_date - quote.departure_date).days
            base_flight_cost = 500 * quote.number_of_passengers  # Example: $500 per passenger
            base_hotel_cost = 0
            
            # Hotel cost based on accommodation preference
            accommodation = form.cleaned_data.get('accommodation_preference', 'standard')
            hotel_rates = {
                'economy': 50,
                'standard': 100,
                'luxury': 200,
                'premium': 350,
            }
            base_hotel_cost = hotel_rates.get(accommodation, 100) * days * quote.number_of_passengers
            
            # Create quote items
            # Flight
            TravelQuoteItem.objects.create(
                quote=quote,
                item_type='flight',
                description=f"Round-trip flight ({form.cleaned_data.get('flight_class', 'economy')} class) from {quote.departure_city} to {destination.city}",
                unit_cost=base_flight_cost / quote.number_of_passengers,
                quantity=quote.number_of_passengers,
                provider="Partner Airlines"
            )
            
            # Hotel
            TravelQuoteItem.objects.create(
                quote=quote,
                item_type='hotel',
                description=f"Hotel accommodation ({accommodation}) for {days} nights",
                unit_cost=base_hotel_cost / quote.number_of_passengers / days if days > 0 else 0,
                quantity=quote.number_of_passengers * days,
                provider="Partner Hotels"
            )
            
            # Add-on features
            addon_features = form.cleaned_data.get('addon_features', [])
            addon_pricing = {
                'visa_assistance': 150,
                'travel_insurance': 50,
                'airport_transfer': 75,
                'local_transport': 100,
                'guided_tours': 200,
                'meals': 300,
                'sim_card': 25,
                'travel_kit': 50,
                'currency_exchange': 20,
                '24_7_support': 100,
            }
            
            addon_descriptions = {
                'visa_assistance': 'Visa Processing Assistance',
                'travel_insurance': 'Travel Insurance Coverage',
                'airport_transfer': 'Airport Transfer Service (Round-trip)',
                'local_transport': 'Local Transportation Pass',
                'guided_tours': 'Guided City Tours',
                'meals': 'Meal Plans (Breakfast, Lunch, Dinner)',
                'sim_card': 'Local SIM Card & Data Package',
                'travel_kit': 'Travel Essentials Kit',
                'currency_exchange': 'Currency Exchange Service',
                '24_7_support': '24/7 Travel Support Hotline',
            }
            
            for addon in addon_features:
                if addon in addon_pricing:
                    TravelQuoteItem.objects.create(
                        quote=quote,
                        item_type='other',
                        description=addon_descriptions.get(addon, addon.replace('_', ' ').title()),
                        unit_cost=addon_pricing[addon],
                        quantity=quote.number_of_passengers,
                        provider="WON Travel Services"
                    )
            
            # Calculate total
            total = sum(item.total_cost for item in quote.items.all())
            quote.total_estimate = total
            quote.save()
            
            messages.success(request, f"Travel quote generated successfully! Quote Number: {quote.quote_number}")
            # Redirect to quote display page or show success
            return redirect('travel-quote-detail', quote_id=str(quote.id))
    
    # Pre-fill destination if provided
    if destination:
        initial = {}
        form = TravelQuoteRequestForm(initial=initial)
    
    context = {
        'form': form,
        'destination': destination,
        'quote': quote,
    }
    
    return render(request, 'frontend/travel-quote.html', context)


def travel_quote_detail(request, quote_id):
    """Display travel quote details and allow PDF download"""
    quote = get_object_or_404(TravelQuote, id=quote_id)
    
    # Check if user has access (either the quote owner or admin)
    if not request.user.is_authenticated or (quote.user != request.user and not request.user.is_staff):
        # Allow access if they have the quote number (for email links)
        quote_number = request.GET.get('quote_number')
        if quote_number != quote.quote_number:
            messages.error(request, "You don't have permission to view this quote.")
            return redirect('destination')
    
    # Get all quote items
    quote_items = quote.items.all()
    
    context = {
        'quote': quote,
        'quote_items': quote_items,
    }
    
    return render(request, 'frontend/travel-quote-detail.html', context)


def download_travel_quote_pdf(request, quote_id):
    """Generate and download travel quote PDF"""
    quote = get_object_or_404(TravelQuote, id=quote_id)
    
    # Check access
    if not request.user.is_authenticated or (quote.user != request.user and not request.user.is_staff):
        quote_number = request.GET.get('quote_number')
        if quote_number != quote.quote_number:
            messages.error(request, "You don't have permission to download this quote.")
            return redirect('destination')
    
    # Create a BytesIO buffer for the PDF
    buffer = BytesIO()
    
    # Create the PDF object
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        leading=14
    )
    
    # Title
    title = Paragraph("TRAVEL QUOTE", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Company info header
    company_info = [
        ['<b>WON Travel Services</b>', ''],
        ['Travel & Tour Services', ''],
        ['Email: info@won.com', ''],
        ['Phone: +254 700 000 000', ''],
    ]
    
    company_table = Table(company_info, colWidths=[4*inch, 2*inch])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 16),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Quotation details
    quotation_date = quote.created_at.strftime('%B %d, %Y')
    
    quotation_info = [
        ['<b>Quote Number:</b>', quote.quote_number or 'N/A'],
        ['<b>Date:</b>', quotation_date],
        ['<b>Valid Until:</b>', quote.quote_valid_until.strftime('%B %d, %Y')],
    ]
    
    quotation_table = Table(quotation_info, colWidths=[2.5*inch, 3.5*inch])
    quotation_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(quotation_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Customer Information
    customer_heading = Paragraph("Customer Information", heading_style)
    elements.append(customer_heading)
    
    customer_info = [
        ['<b>Name:</b>', quote.user.get_full_name() or quote.user.username],
        ['<b>Email:</b>', quote.user.email],
        ['<b>Phone:</b>', quote.user.phone or 'N/A'],
    ]
    
    customer_table = Table(customer_info, colWidths=[2.5*inch, 3.5*inch])
    customer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Travel Details
    travel_heading = Paragraph("Travel Details", heading_style)
    elements.append(travel_heading)
    
    destination = quote.destination
    travel_info = [
        ['<b>Destination:</b>', f"{destination.city}, {destination.country}"],
        ['<b>Departure From:</b>', f"{quote.departure_city}, {quote.departure_country}"],
        ['<b>Departure Date:</b>', quote.departure_date.strftime('%B %d, %Y')],
        ['<b>Return Date:</b>', quote.return_date.strftime('%B %d, %Y')],
        ['<b>Number of Passengers:</b>', str(quote.number_of_passengers)],
    ]
    
    travel_table = Table(travel_info, colWidths=[2.5*inch, 3.5*inch])
    travel_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(travel_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Quote Items
    items_heading = Paragraph("Quote Breakdown", heading_style)
    elements.append(items_heading)
    
    quote_items = quote.items.all()
    items_data = [['<b>Description</b>', '<b>Quantity</b>', '<b>Unit Price</b>', '<b>Total</b>']]
    
    for item in quote_items:
        items_data.append([
            item.description,
            str(item.quantity),
            f"{quote.currency} {item.unit_cost:,.2f}",
            f"{quote.currency} {item.total_cost:,.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
    items_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Total
    total_data = [
        ['<b>TOTAL ESTIMATE:</b>', f"<b>{quote.currency} {quote.total_estimate:,.2f}</b>"]
    ]
    total_table = Table(total_data, colWidths=[4*inch, 2*inch])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Special Requests
    if quote.special_requests:
        notes_heading = Paragraph("Special Requests", heading_style)
        elements.append(notes_heading)
        notes_para = Paragraph(quote.special_requests, normal_style)
        elements.append(notes_para)
        elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_text = Paragraph(
        "<i>This quote is valid until {}. "
        "Prices are estimates and may vary based on availability and booking date. "
        "For any inquiries, please contact us at info@won.com or +254 700 000 000.</i>".format(
            quote.quote_valid_until.strftime('%B %d, %Y')
        ),
        ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceBefore=20
        )
    )
    elements.append(footer_text)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="travel_quote_{quote.quote_number}.pdf"'
    response.write(pdf)
    
    return response


def subscription_parents(request):
    """Parents subscription packages page"""
    plans = SubscriptionPlan.objects.filter(
        plan_type='parent',
        is_active=True
    ).order_by('price')
    
    # Group plans by duration
    monthly_plans = plans.filter(duration='monthly')
    quarterly_plans = plans.filter(duration='quarterly')
    annually_plans = plans.filter(duration='annually')
    
    context = {
        'category': 'Parents',
        'category_description': 'Empower your child to become a global champion with our comprehensive parent subscription packages. Access Olympiad competitions, track applications, and get expert guidance.',
        'monthly_plans': monthly_plans,
        'quarterly_plans': quarterly_plans,
        'annually_plans': annually_plans,
        'all_plans': plans,
    }
    
    return render(request, 'frontend/subscription-details.html', context)


def subscription_schools(request):
    """Schools subscription packages page"""
    plans = SubscriptionPlan.objects.filter(
        plan_type='school',
        is_active=True
    ).order_by('price')
    
    # Group plans by duration
    monthly_plans = plans.filter(duration='monthly')
    quarterly_plans = plans.filter(duration='quarterly')
    annually_plans = plans.filter(duration='annually')
    
    context = {
        'category': 'Schools',
        'category_description': 'Showcase your school as a global leader. Our school subscription packages help you manage multiple students, track their Olympiad progress, and access premium resources.',
        'monthly_plans': monthly_plans,
        'quarterly_plans': quarterly_plans,
        'annually_plans': annually_plans,
        'all_plans': plans,
    }
    
    return render(request, 'frontend/subscription-details.html', context)


def subscription_students(request):
    """Students subscription packages page"""
    plans = SubscriptionPlan.objects.filter(
        plan_type='student',
        is_active=True
    ).order_by('price')
    
    # Group plans by duration
    monthly_plans = plans.filter(duration='monthly')
    quarterly_plans = plans.filter(duration='quarterly')
    annually_plans = plans.filter(duration='annually')
    
    context = {
        'category': 'Students',
        'category_description': 'Access resources and excel abroad. Our student subscription packages provide you with study materials, competition access, and preparation support to achieve academic excellence.',
        'monthly_plans': monthly_plans,
        'quarterly_plans': quarterly_plans,
        'annually_plans': annually_plans,
        'all_plans': plans,
    }
    
    return render(request, 'frontend/subscription-details.html', context)

