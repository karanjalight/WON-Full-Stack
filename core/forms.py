"""
Forms for Olympiad Application Process
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from backend.models import (
    User, StudentProfile, Competition, OlympiadApplication, 
    TravelQuote, ApplicationDocument
)
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

