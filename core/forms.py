"""
Forms for Olympiad Application Process
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from backend.models import (
    User, StudentProfile, Competition, OlympiadApplication, 
    TravelQuote, ApplicationDocument, TutorProfile, TutorSession, Subject,
    ParentProfile, SchoolProfile
)
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils import timezone


class ApplicationStep1Form(forms.Form):
    """Step 1: Basic Application Information"""
    competition = forms.ModelChoiceField(
        queryset=Competition.objects.filter(is_active=True),
        widget=forms.HiddenInput()
    )
    
    # Basic applicant info (can be filled without account)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    # Emergency contact
    emergency_contact_name = forms.CharField(max_length=255, required=True)
    emergency_contact_phone = forms.CharField(max_length=20, required=True)
    
    # Motivation
    motivation_letter = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
        help_text="Why do you want to participate in this competition?"
    )
    
    # Special requirements
    special_requirements = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Dietary restrictions, accessibility needs, etc."
    )


class TravelQuoteForm(forms.Form):
    """Step 2: Travel Quote Information"""
    departure_city = forms.CharField(max_length=100, required=True)
    departure_country = forms.CharField(max_length=100, required=True)
    departure_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    return_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    number_of_passengers = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        required=True
    )
    special_requests = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )


class TravelQuoteRequestForm(forms.Form):
    """Comprehensive Travel Quote Request Form"""
    # Contact Information
    full_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'})
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'})
    )
    
    # Travel Details
    departure_city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City of departure'})
    )
    departure_country = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country of departure'})
    )
    departure_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    return_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    # Passenger Information
    number_of_passengers = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=1,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '20'})
    )
    
    ACCOMMODATION_CHOICES = [
        ('economy', 'Economy (Budget-friendly)'),
        ('standard', 'Standard (3-star)'),
        ('luxury', 'Luxury (4-5 star)'),
        ('premium', 'Premium (5-star+)'),
    ]
    accommodation_preference = forms.ChoiceField(
        choices=ACCOMMODATION_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Travel Preferences
    flight_class = forms.ChoiceField(
        choices=[
            ('economy', 'Economy Class'),
            ('business', 'Business Class'),
            ('first', 'First Class'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Add-on Features (Multiple Choice)
    ADDON_CHOICES = [
        ('visa_assistance', 'Visa Processing Assistance'),
        ('travel_insurance', 'Travel Insurance'),
        ('airport_transfer', 'Airport Transfer Service'),
        ('local_transport', 'Local Transportation Pass'),
        ('guided_tours', 'Guided City Tours'),
        ('meals', 'Meal Plans (Breakfast/Lunch/Dinner)'),
        ('sim_card', 'Local SIM Card & Data'),
        ('travel_kit', 'Travel Essentials Kit'),
        ('currency_exchange', 'Currency Exchange Service'),
        ('24_7_support', '24/7 Travel Support'),
    ]
    addon_features = forms.MultipleChoiceField(
        choices=ADDON_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    # Special Requests
    special_requests = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Any special requirements, dietary restrictions, accessibility needs, etc.'
        }),
        required=False
    )
    
    # Budget Range (Optional)
    budget_range = forms.ChoiceField(
        choices=[
            ('', 'Select budget range (optional)'),
            ('under_1000', 'Under $1,000'),
            ('1000_2500', '$1,000 - $2,500'),
            ('2500_5000', '$2,500 - $5,000'),
            ('5000_10000', '$5,000 - $10,000'),
            ('over_10000', 'Over $10,000'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        departure_date = cleaned_data.get('departure_date')
        return_date = cleaned_data.get('return_date')
        
        if departure_date and return_date:
            if return_date <= departure_date:
                raise ValidationError("Return date must be after departure date.")
            
            # Check if trip is too far in the future (optional validation)
            from django.utils import timezone
            if departure_date < timezone.now().date():
                raise ValidationError("Departure date cannot be in the past.")
        
        return cleaned_data


class StudentRegistrationForm(UserCreationForm):
    """Step 3: User Registration Form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    phone = forms.CharField(max_length=20, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'] = forms.CharField(
            widget=forms.HiddenInput(),
            initial='student'
        )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.user_type = 'student'
        if commit:
            user.save()
            # Create student profile
            StudentProfile.objects.create(
                user=user,
                date_of_birth=timezone.now().date()  # Will be updated from session
            )
        return user


class StudentProfileForm(forms.ModelForm):
    """Step 4: Complete Student Profile"""
    interests = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Enter your interests separated by commas (e.g., Mathematics, Physics, Programming)"
    )
    
    class Meta:
        model = StudentProfile
        fields = [
            'date_of_birth', 'grade_level', 'current_school',
            'guardian_name', 'guardian_email', 'guardian_phone',
            'achievements', 'passport_number',
            'passport_expiry', 'national_id'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'passport_expiry': forms.DateInput(attrs={'type': 'date'}),
            'achievements': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.interests:
            # Convert list to comma-separated string
            self.fields['interests'].initial = ', '.join(self.instance.interests) if isinstance(self.instance.interests, list) else ''
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Convert comma-separated string to list
        interests_str = self.cleaned_data.get('interests', '')
        if interests_str:
            instance.interests = [i.strip() for i in interests_str.split(',') if i.strip()]
        if commit:
            instance.save()
        return instance


class DocumentUploadForm(forms.ModelForm):
    """Step 5: Document Upload Form"""
    class Meta:
        model = ApplicationDocument
        fields = ['document_type', 'file', 'expiry_date']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make expiry_date optional for non-expiring documents
        self.fields['expiry_date'].required = False


class ApplicationReviewForm(forms.Form):
    """Step 6: Review and Confirm Application"""
    terms_accepted = forms.BooleanField(
        required=True,
        label="I accept the terms and conditions"
    )
    privacy_accepted = forms.BooleanField(
        required=True,
        label="I accept the privacy policy"
    )


class TutorSessionBookingForm(forms.Form):
    """Form for booking a tutor session"""
    tutor = forms.ModelChoiceField(
        queryset=TutorProfile.objects.filter(is_accepting_students=True, user__is_active=True),
        widget=forms.HiddenInput()
    )
    
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'required': True}),
        help_text="Select the subject you want help with"
    )
    
    scheduled_at = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'required': True
        }),
        help_text="Select date and time for your session"
    )
    
    duration_minutes = forms.ChoiceField(
        choices=[
            (30, '30 minutes'),
            (60, '1 hour'),
            (90, '1.5 hours'),
            (120, '2 hours'),
        ],
        initial=60,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Session duration"
    )
    
    topic = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Algebra, Calculus, Problem Solving'
        }),
        help_text="Specific topic or area you want to focus on (optional)"
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe what you\'d like to cover in this session...'
        }),
        required=False,
        help_text="Additional details about what you want to learn or practice"
    )
    
    # Contact information (for non-authenticated users)
    student_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Your full name (if not logged in)"
    )
    
    student_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text="Your email (if not logged in)"
    )
    
    student_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Your phone number (if not logged in)"
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I accept the terms and conditions for booking a session"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        scheduled_at = cleaned_data.get('scheduled_at')
        duration_minutes = cleaned_data.get('duration_minutes')
        tutor = cleaned_data.get('tutor')
        
        if scheduled_at:
            from django.utils import timezone
            from datetime import timedelta
            
            if scheduled_at < timezone.now():
                raise ValidationError("Scheduled time cannot be in the past.")
            
            # Check if tutor is available (basic check - can be enhanced)
            if tutor:
                duration = int(duration_minutes or 60)
                session_end = scheduled_at + timedelta(minutes=duration)
                
                # Check for overlapping sessions
                overlapping = TutorSession.objects.filter(
                    tutor=tutor,
                    scheduled_at__lt=session_end,
                    status__in=['scheduled', 'confirmed']
                ).exclude(
                    scheduled_at__gte=session_end
                ).filter(
                    scheduled_at__gte=scheduled_at - timedelta(minutes=duration)
                ).exists()
                
                if overlapping:
                    raise ValidationError("This time slot appears to be already booked. Please select another time.")
        
        return cleaned_data


# ============================================================================
# AUTHENTICATION FORMS
# ============================================================================

class LoginForm(AuthenticationForm):
    """Login form with custom styling"""
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username or Email'
        self.fields['password'].label = 'Password'


class SignupForm(UserCreationForm):
    """Signup form with user type selection"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890'
        })
    )
    user_type = forms.ChoiceField(
        choices=[
            ('student', 'Student'),
            ('parent', 'Parent'),
            ('school', 'School'),
            ('tutor', 'Tutor'),
        ],
        required=True,
        widget=forms.RadioSelect(attrs={
            'class': 'user-type-radio'
        }),
        help_text="Select your account type"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'user_type', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirm Password'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'
        self.fields['email'].label = 'Email Address'
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['phone'].label = 'Phone Number'
        self.fields['user_type'].label = 'I am a'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.user_type = self.cleaned_data['user_type']
        
        if commit:
            user.save()
            
            # Create appropriate profile based on user type
            if user.user_type == 'student':
                StudentProfile.objects.create(user=user)
            elif user.user_type == 'parent':
                ParentProfile.objects.create(user=user)
            elif user.user_type == 'school':
                SchoolProfile.objects.create(
                    user=user,
                    school_name=user.get_full_name() or user.username
                )
            # Tutor profile would be created separately through admin or a separate form
        
        return user

