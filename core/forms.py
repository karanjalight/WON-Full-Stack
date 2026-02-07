"""
Forms for Olympiad Application Process
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from backend.models import (
    User, StudentProfile, Competition, OlympiadApplication, 
    TravelQuote, ApplicationDocument, TutorProfile, TutorSession, Subject,
    ParentProfile, SchoolProfile, SubscriptionPlan, UserSubscription, PaymentTransaction
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
            elif user.user_type == 'tutor':
                # Create a minimal tutor profile so the tutor can access dashboard
                TutorProfile.objects.create(
                    user=user,
                    qualifications="Pending verification",
                    hourly_rate=0,
                    specializations="",
                )
        
        return user


# ============================================================================
# SUBSCRIPTION FORMS
# ============================================================================

class SubscriptionCheckoutForm(forms.Form):
    """Subscription checkout form"""
    plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        widget=forms.HiddenInput()
    )
    
    payment_method = forms.ChoiceField(
        choices=[
            ('paystack', 'Pay with Card (Paystack)'),
            ('mpesa', 'M-Pesa (Coming Soon)'),
        ],
        initial='paystack',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        label='I agree to the Terms and Conditions',
        error_messages={'required': 'You must accept the terms and conditions to proceed.'}
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Filter plans by user type if user is provided
        if user and hasattr(user, 'user_type'):
            self.fields['plan'].queryset = SubscriptionPlan.objects.filter(
                is_active=True,
                plan_type=user.user_type
            )
    
    def clean(self):
        cleaned_data = super().clean()
        plan = cleaned_data.get('plan')
        
        # Validate user has the correct user type for the plan
        if self.user and plan:
            if plan.plan_type != self.user.user_type:
                raise ValidationError(
                    f"This plan is for {plan.get_plan_type_display()}s only. "
                    f"You are registered as a {self.user.get_user_type_display()}."
                )
        
        return cleaned_data


class PaymentConfirmationForm(forms.Form):
    """Payment confirmation form (for manual payment verification)"""
    payment_reference = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter payment reference number'
        })
    )
    
    payment_method = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Paystack, Bank Transfer'
        })
    )
    
    amount_paid = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        })
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional notes (optional)'
        }),
        required=False
    )


# ============================================================================
# CHILD/STUDENT ACCOUNT MANAGEMENT FORMS
# ============================================================================

class AddChildForm(forms.ModelForm):
    """Form for parents to add a child account"""
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password for this child'
        }),
        help_text="Password must be at least 8 characters"
    )
    
    confirm_password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text="Child's date of birth"
    )
    
    grade_level = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Grade 8, Form 3, Year 10'
        })
    )
    
    interests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Mathematics, Physics, Chemistry, Biology...'
        }),
        help_text="Enter subjects/interests separated by commas"
    )
    
    send_welcome_email = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Send welcome email with login credentials'
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name',
                'required': True
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username for login',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'child@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
        }
    
    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.fields['email'].required = False
        self.fields['phone'].required = False
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose another.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError("Passwords do not match.")
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'
        user.set_password(self.cleaned_data['password'])
        
        if self.parent:
            user.parent = self.parent
            user.created_by = self.parent
        
        if commit:
            user.save()
            
            # Create student profile
            interests_str = self.cleaned_data.get('interests', '')
            interests_list = [i.strip() for i in interests_str.split(',') if i.strip()] if interests_str else []
            
            StudentProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data['date_of_birth'],
                grade_level=self.cleaned_data.get('grade_level', ''),
                interests=interests_list
            )
        
        return user


class AddSchoolStudentForm(forms.ModelForm):
    """Form for schools to add a student account"""
    password = forms.CharField(
        max_length=128,
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password (optional - will auto-generate if empty)'
        }),
        help_text="Leave empty to auto-generate a secure password"
    )
    
    confirm_password = forms.CharField(
        max_length=128,
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    grade_level = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Grade 10, Form 4'
        })
    )
    
    student_id = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'School student ID number'
        }),
        help_text="Internal student ID in your school system"
    )
    
    send_credentials_email = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Send login credentials via email'
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name',
                'required': True
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username (will auto-generate if empty)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'student@school.edu',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
        }
    
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.school = school
        self.fields['username'].required = False
        self.fields['phone'].required = False
        self.generated_password = None
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            # Auto-generate username from first and last name
            first_name = self.data.get('first_name', '').lower()
            last_name = self.data.get('last_name', '').lower()
            if first_name and last_name:
                base_username = f"{first_name}.{last_name}"
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                return username
        elif User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password:
            if password != confirm_password:
                raise ValidationError("Passwords do not match.")
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
        else:
            # Generate secure password
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits + string.punctuation
            self.generated_password = ''.join(secrets.choice(alphabet) for i in range(12))
            cleaned_data['password'] = self.generated_password
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'
        user.set_password(self.cleaned_data['password'])
        
        if self.school:
            user.school = self.school
            user.created_by = self.school
        
        if commit:
            user.save()
            
            # Create student profile
            StudentProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                grade_level=self.cleaned_data.get('grade_level', ''),
                current_school=self.school.get_full_name() if self.school else ''
            )
        
        return user


class EditChildForm(forms.ModelForm):
    """Form for editing child/student information"""
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    grade_level = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Grade 8'
        })
    )
    
    interests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Mathematics, Physics, Chemistry...'
        }),
        help_text="Enter subjects/interests separated by commas"
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_picture', 'bio', 'country', 'city']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'student_profile'):
            profile = self.instance.student_profile
            self.fields['date_of_birth'].initial = profile.date_of_birth
            self.fields['grade_level'].initial = profile.grade_level
            if profile.interests:
                self.fields['interests'].initial = ', '.join(profile.interests) if isinstance(profile.interests, list) else ''
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        
        if hasattr(user, 'student_profile'):
            profile = user.student_profile
            profile.date_of_birth = self.cleaned_data.get('date_of_birth')
            profile.grade_level = self.cleaned_data.get('grade_level', '')
            
            # Handle interests
            interests_str = self.cleaned_data.get('interests', '')
            if interests_str:
                profile.interests = [i.strip() for i in interests_str.split(',') if i.strip()]
            
            if commit:
                profile.save()
        
        return user

