from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from datetime import datetime
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
    StudentProfile, OlympiadApplication, TravelQuote, ApplicationDocument
)
from core.forms import (
    ApplicationStep1Form, TravelQuoteForm, StudentRegistrationForm,
    StudentProfileForm, DocumentUploadForm, ApplicationReviewForm
)

# Create your views here.

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
    """Team listing page view"""
    return render(request, 'frontend/team.html')

def team_details(request):
    """Team member details page view"""
    return render(request, 'frontend/team-details.html')

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



