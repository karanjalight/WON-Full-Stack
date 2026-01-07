"""
WON - World Olympiad Network
Django Database Models
Complete Schema with ERD

Author: Professional Database Design
Date: January 2026
Framework: Django
Database: PostgreSQL (recommended)

Core Modules:
1. Users & Authentication
2. Subscriptions & Payments
3. Olympiads & Competitions
4. Applications & Documents
5. Travel & Quotes
6. Tutoring & Sessions
7. Content & Resources
8. Notifications
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.utils import timezone
import uuid


# ============================================================================
# 1. USERS & AUTHENTICATION MODULE
# ============================================================================

class User(AbstractUser):
    """
    Custom User Model - Polymorphic base for all user types
    Extends Django's AbstractUser
    """
    USER_TYPES = (
        ('parent', 'Parent'),
        ('student', 'Student'),
        ('school', 'School'),
        ('tutor', 'Tutor'),
        ('admin', 'Admin'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    # Profile Information
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Verification (for independent students)
    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to='verifications/', blank=True, null=True)
    school_email = models.EmailField(blank=True, null=True, validators=[EmailValidator()])
    verified_at = models.DateTimeField(blank=True, null=True)
    
    # Relationships
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='created_users', help_text="School/Parent who created this user")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='children', limit_choices_to={'user_type': 'parent'})
    school = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='students', limit_choices_to={'user_type': 'school'})
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_type', 'is_verified']),
            models.Index(fields=['email']),
            models.Index(fields=['slug']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.username}-{self.user_type}")
            self.slug = f"{base_slug}-{str(self.id)[:8]}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_user_type_display()})"


class ParentProfile(models.Model):
    """Extended profile for Parents"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    occupation = models.CharField(max_length=200, blank=True, null=True)
    number_of_children = models.PositiveIntegerField(default=0)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    preferred_contact_method = models.CharField(max_length=20, 
                                               choices=[('email', 'Email'), ('phone', 'Phone'), ('both', 'Both')],
                                               default='email')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'parent_profiles'
        verbose_name = 'Parent Profile'
        verbose_name_plural = 'Parent Profiles'
    
    def __str__(self):
        return f"Parent: {self.user.get_full_name()}"


class StudentProfile(models.Model):
    """Extended profile for Students"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    date_of_birth = models.DateField(blank=True, null=True)
    grade_level = models.CharField(max_length=50, blank=True, null=True)
    current_school = models.CharField(max_length=255, blank=True, null=True)
    
    # Guardian Information (if independent student)
    guardian_name = models.CharField(max_length=255, blank=True, null=True)
    guardian_email = models.EmailField(blank=True, null=True)
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Academic Information
    interests = models.JSONField(default=list, blank=True, 
                                help_text="List of academic interests/subjects")
    achievements = models.TextField(blank=True, null=True)
    
    # Documents
    passport_number = models.CharField(max_length=50, blank=True, null=True)
    passport_expiry = models.DateField(blank=True, null=True)
    passport_document = models.FileField(upload_to='student_docs/passports/', blank=True, null=True)
    national_id = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_profiles'
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        indexes = [
            models.Index(fields=['date_of_birth']),
            models.Index(fields=['grade_level']),
        ]
    
    def __str__(self):
        return f"Student: {self.user.get_full_name()}"
    
    def get_age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class SchoolProfile(models.Model):
    """Extended profile for Schools"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='school_profile')
    school_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    school_type = models.CharField(max_length=50, 
                                  choices=[('public', 'Public'), ('private', 'Private'), 
                                          ('international', 'International')],
                                  blank=True, null=True)
    
    # Contact Information
    principal_name = models.CharField(max_length=255, blank=True, null=True)
    principal_email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Capacity
    total_students = models.PositiveIntegerField(default=0)
    active_olympiad_students = models.PositiveIntegerField(default=0)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to='school_verifications/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'school_profiles'
        verbose_name = 'School Profile'
        verbose_name_plural = 'School Profiles'
    
    def __str__(self):
        return self.school_name


class TutorProfile(models.Model):
    """Extended profile for Tutors"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutor_profile')
    
    # Professional Information
    title = models.CharField(max_length=100, blank=True, null=True, 
                           help_text="e.g., Dr., Prof., Mr.")
    qualifications = models.TextField(help_text="Education and certifications")
    experience_years = models.PositiveIntegerField(default=0)
    specializations = models.TextField(blank=True, null=True)
    
    # Rates and Availability
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, 
                                     validators=[MinValueValidator(0)],
                                     help_text="Rate in USD")
    currency = models.CharField(max_length=3, default='USD')
    calendly_link = models.URLField(blank=True, null=True, 
                                   help_text="Calendly scheduling link")
    
    # Statistics
    total_sessions = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0,
                                        validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_accepting_students = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tutor_profiles'
        verbose_name = 'Tutor Profile'
        verbose_name_plural = 'Tutor Profiles'
        ordering = ['-is_featured', '-average_rating']
    
    def __str__(self):
        return f"Tutor: {self.title} {self.user.get_full_name()}"


# ============================================================================
# 2. SUBSCRIPTIONS & PAYMENTS MODULE
# ============================================================================

class SubscriptionPlan(models.Model):
    """Subscription plans for different user types"""
    PLAN_TYPES = (
        ('parent', 'Parent Plan'),
        ('student', 'Student Plan'),
        ('school', 'School Plan'),
        ('tutor', 'Tutor Plan'),
    )
    
    DURATION_CHOICES = (
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, 
                               validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='USD')
    
    # Features (stored as JSON for flexibility)
    features = models.JSONField(default=dict, help_text="Plan features and limits")
    description = models.TextField(blank=True, null=True)
    
    # Limits
    max_students = models.PositiveIntegerField(null=True, blank=True, 
                                              help_text="For parent/school plans")
    max_applications = models.PositiveIntegerField(null=True, blank=True,
                                                   help_text="Application limit per period")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_plans'
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['plan_type', 'price']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.plan_type}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.get_plan_type_display()} (${self.price}/{self.duration})"


class UserSubscription(models.Model):
    """Active/Historic subscriptions for users"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending Payment'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions')
    
    # Subscription Period
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment
    auto_renew = models.BooleanField(default=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True, 
                                     help_text="e.g., Paystack, Card, M-Pesa")
    
    # Metadata
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_subscriptions'
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"
    
    def is_valid(self):
        return self.status == 'active' and self.end_date > timezone.now()


class PaymentTransaction(models.Model):
    """All payment transactions"""
    TRANSACTION_TYPES = (
        ('subscription', 'Subscription Payment'),
        ('application', 'Olympiad Application'),
        ('tutor_session', 'Tutor Session'),
        ('travel_booking', 'Travel Booking'),
        ('refund', 'Refund'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2, 
                                validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='USD')
    
    # Payment Gateway
    payment_gateway = models.CharField(max_length=50, default='paystack')
    gateway_reference = models.CharField(max_length=255, unique=True, blank=True, null=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Related Objects (nullable for flexibility)
    subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, 
                                    null=True, blank=True, related_name='transactions')
    application = models.ForeignKey('OlympiadApplication', on_delete=models.SET_NULL, 
                                   null=True, blank=True, related_name='transactions')
    tutor_session = models.ForeignKey('TutorSession', on_delete=models.SET_NULL, 
                                     null=True, blank=True, related_name='transactions')
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_transactions'
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['gateway_reference']),
            models.Index(fields=['transaction_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} - ${self.amount}"


# ============================================================================
# 3. OLYMPIADS & COMPETITIONS MODULE
# ============================================================================

class Subject(models.Model):
    """Academic subjects for Olympiads"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    icon = models.ImageField(upload_to='subjects/icons/', blank=True, null=True)
    
    # Statistics
    total_olympiads = models.PositiveIntegerField(default=0)
    total_tutors = models.PositiveIntegerField(default=0)
    
    # Display
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subjects'
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        ordering = ['display_order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class TutorSubject(models.Model):
    """Many-to-many relationship between Tutors and Subjects"""
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='tutors')
    experience_years = models.PositiveIntegerField(default=0)
    specialization_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tutor_subjects'
        verbose_name = 'Tutor Subject'
        verbose_name_plural = 'Tutor Subjects'
        unique_together = ['tutor', 'subject']
    
    def __str__(self):
        return f"{self.tutor.user.get_full_name()} - {self.subject.name}"


class Destination(models.Model):
    """Geographic destinations for Olympiads"""
    REGION_CHOICES = (
        ('africa', 'Africa'),
        ('europe', 'Europe'),
        ('asia', 'Asia'),
        ('north_america', 'North America'),
        ('south_america', 'South America'),
        ('middle_east', 'Middle East'),
        ('oceania', 'Oceania'),
        ('caribbean', 'Caribbean & Central America'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    region = models.CharField(max_length=50, choices=REGION_CHOICES)
    
    # Location Details
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    continent = models.CharField(max_length=50, blank=True, null=True)
    iframe_url = models.CharField(max_length=800, blank=True, null=True)
    
    # Travel Information
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='destinations/', blank=True, null=True)
    package_price_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    package_price_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Metadata
    timezone = models.CharField(max_length=50, blank=True, null=True)
    climate_info = models.TextField(blank=True, null=True)
    visa_requirements = models.TextField(blank=True, null=True)
    
    # Statistics
    total_olympiads = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'destinations'
        verbose_name = 'Destination'
        verbose_name_plural = 'Destinations'
        ordering = ['region', 'country', 'city']
        indexes = [
            models.Index(fields=['region', 'country']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.city}-{self.country}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.city}, {self.country} ({self.get_region_display()})"


class Competition(models.Model):
    """Main Olympiad competitions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    short_name = models.CharField(max_length=50, blank=True, null=True, 
                                  help_text="e.g., IMO, IPhO")
    
    # Relationships
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='competitions')
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT, 
                                   related_name='competitions')
    
    # Description
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='competitions/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='competitions/banners/', blank=True, null=True)
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    application_start_date = models.DateField(null=True, blank=True)
    application_deadline = models.DateField()
    
    # Age Requirements
    age_group_min = models.PositiveIntegerField(validators=[MinValueValidator(5)])
    age_group_max = models.PositiveIntegerField(validators=[MinValueValidator(5)])
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2, 
                                    validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='USD')
    
    # Additional Info
    website = models.URLField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    organizer = models.CharField(max_length=255, blank=True, null=True)
    
    # Status & Features
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, 
                            choices=[('upcoming', 'Upcoming'), ('ongoing', 'Ongoing'), 
                                   ('completed', 'Completed'), ('cancelled', 'Cancelled')],
                            default='upcoming')
    
    # Statistics
    total_applications = models.PositiveIntegerField(default=0)
    total_participants = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'competitions'
        verbose_name = 'Competition'
        verbose_name_plural = 'Competitions'
        ordering = ['-is_featured', 'application_deadline', 'start_date']
        indexes = [
            models.Index(fields=['subject', 'status']),
            models.Index(fields=['application_deadline']),
            models.Index(fields=['start_date']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.start_date.year}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.destination.city}, {self.start_date.year}"
    
    def is_application_open(self):
        today = timezone.now().date()
        return today <= self.application_deadline and self.is_active


class CompetitionRound(models.Model):
    """Rounds/Stages of competitions (qualifying, regional, international)"""
    ROUND_TYPES = (
        ('qualifying', 'Qualifying Round'),
        ('regional', 'Regional Round'),
        ('national', 'National Round'),
        ('international', 'International Round'),
        ('final', 'Final Round'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='rounds')
    round_type = models.CharField(max_length=20, choices=ROUND_TYPES)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, blank=True)
    
    # Details
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    
    # Dates
    date = models.DateField()
    registration_deadline = models.DateField()
    
    # Requirements
    requirements = models.TextField(blank=True, null=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    
    # Pricing
    additional_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                        validators=[MinValueValidator(0)])
    
    round_order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'competition_rounds'
        verbose_name = 'Competition Round'
        verbose_name_plural = 'Competition Rounds'
        ordering = ['competition', 'round_order', 'date']
        unique_together = ['competition', 'round_type']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.competition.slug}-{self.get_round_type_display()}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.competition.name} - {self.get_round_type_display()}"


# ============================================================================
# 4. APPLICATIONS & DOCUMENTS MODULE
# ============================================================================

class OlympiadApplication(models.Model):
    """Student applications to competitions"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('documents_pending', 'Documents Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted'),
        ('withdrawn', 'Withdrawn'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_number = models.CharField(max_length=50, unique=True, blank=True)
    
    # Relationships
    student = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='applications',
                               limit_choices_to={'user_type': 'student'})
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, 
                                   related_name='applications')
    round = models.ForeignKey(CompetitionRound, on_delete=models.SET_NULL, 
                             null=True, blank=True, related_name='applications')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    # Financial
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20,
                                     choices=[('pending', 'Pending'), ('partial', 'Partial'),
                                            ('paid', 'Paid'), ('refunded', 'Refunded')],
                                     default='pending')
    
    # Additional Information
    motivation_letter = models.TextField(blank=True, null=True)
    special_requirements = models.TextField(blank=True, null=True,
                                          help_text="Dietary, accessibility, etc.")
    emergency_contact_name = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Admin Notes
    reviewer_notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'olympiad_applications'
        verbose_name = 'Olympiad Application'
        verbose_name_plural = 'Olympiad Applications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['competition', 'status']),
            models.Index(fields=['application_number']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.application_number:
            # Generate unique application number
            year = timezone.now().year
            count = OlympiadApplication.objects.filter(
                created_at__year=year
            ).count() + 1
            self.application_number = f"WON-{year}-{count:05d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.application_number} - {self.student.get_full_name()} - {self.competition.short_name or self.competition.name}"


class ApplicationDocument(models.Model):
    """Documents attached to applications"""
    DOCUMENT_TYPES = (
        ('passport', 'Passport'),
        ('national_id', 'National ID'),
        ('birth_certificate', 'Birth Certificate'),
        ('recommendation_letter', 'Recommendation Letter'),
        ('transcript', 'Academic Transcript'),
        ('photo', 'Passport Photo'),
        ('medical_form', 'Medical Form'),
        ('consent_form', 'Parental Consent'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Upload'),
        ('uploaded', 'Uploaded'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(OlympiadApplication, on_delete=models.CASCADE, 
                                   related_name='documents')
    
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='application_documents/', null=True, blank=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text="Size in bytes")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Verification
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='verified_documents')
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True, null=True)
    
    # Expiry (for documents like passports)
    expiry_date = models.DateField(null=True, blank=True)
    
    uploaded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'application_documents'
        verbose_name = 'Application Document'
        verbose_name_plural = 'Application Documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.application.application_number} - {self.get_document_type_display()}"


# ============================================================================
# 5. TRAVEL & QUOTES MODULE
# ============================================================================

class TravelQuote(models.Model):
    """Travel quotes for competitions (generated for users)"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('sent', 'Sent to User'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quote_number = models.CharField(max_length=50, unique=True, blank=True)
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='travel_quotes')
    application = models.ForeignKey(OlympiadApplication, on_delete=models.CASCADE, 
                                   null=True, blank=True, related_name='travel_quotes')
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT, 
                                   related_name='travel_quotes')
    
    # Travel Details
    departure_city = models.CharField(max_length=100)
    departure_country = models.CharField(max_length=100)
    departure_date = models.DateField()
    return_date = models.DateField()
    
    number_of_passengers = models.PositiveIntegerField(default=1, 
                                                       validators=[MinValueValidator(1)])
    passenger_details = models.JSONField(default=list, blank=True,
                                        help_text="List of passenger information")
    
    # Pricing
    total_estimate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    
    # Validity
    quote_valid_until = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Additional Details
    special_requests = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Read Trips Integration
    readtrips_quote_id = models.CharField(max_length=100, blank=True, null=True)
    readtrips_response = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'travel_quotes'
        verbose_name = 'Travel Quote'
        verbose_name_plural = 'Travel Quotes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['quote_number']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.quote_number:
            year = timezone.now().year
            count = TravelQuote.objects.filter(created_at__year=year).count() + 1
            self.quote_number = f"TRV-{year}-{count:05d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quote_number} - {self.user.username} - {self.destination}"


class TravelQuoteItem(models.Model):
    """Individual items in a travel quote (flights, hotels, etc.)"""
    ITEM_TYPES = (
        ('flight', 'Flight'),
        ('hotel', 'Hotel Accommodation'),
        ('airport_transfer', 'Airport Transfer'),
        ('visa_assistance', 'Visa Assistance'),
        ('insurance', 'Travel Insurance'),
        ('meals', 'Meals'),
        ('local_transport', 'Local Transportation'),
        ('other', 'Other'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quote = models.ForeignKey(TravelQuote, on_delete=models.CASCADE, related_name='items')
    
    item_type = models.CharField(max_length=30, choices=ITEM_TYPES)
    description = models.TextField()
    
    # Pricing
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, 
                                   validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField(default=1)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Optional Details
    provider = models.CharField(max_length=255, blank=True, null=True)
    booking_reference = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'travel_quote_items'
        verbose_name = 'Travel Quote Item'
        verbose_name_plural = 'Travel Quote Items'
        ordering = ['quote', 'item_type']
    
    def save(self, *args, **kwargs):
        self.total_cost = self.unit_cost * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quote.quote_number} - {self.get_item_type_display()}"


class TravelBookingRequest(models.Model):
    """User requests to book travel (forwarded to Read Trips)"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent_to_readtrips', 'Sent to Read Trips'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quote = models.OneToOneField(TravelQuote, on_delete=models.CASCADE, 
                                 related_name='booking_request')
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    
    # Contact Information
    contact_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    
    # Additional Requests
    message = models.TextField(blank=True, null=True)
    
    # Read Trips Integration
    readtrips_booking_id = models.CharField(max_length=100, blank=True, null=True)
    readtrips_response = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'travel_booking_requests'
        verbose_name = 'Travel Booking Request'
        verbose_name_plural = 'Travel Booking Requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking Request - {self.quote.quote_number}"


# ============================================================================
# 6. TUTORING & SESSIONS MODULE
# ============================================================================

class TutorSession(models.Model):
    """Tutor sessions booked by students"""
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled_by_student', 'Cancelled by Student'),
        ('cancelled_by_tutor', 'Cancelled by Tutor'),
        ('no_show', 'No Show'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_number = models.CharField(max_length=50, unique=True, blank=True)
    
    # Relationships
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, 
                             related_name='sessions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='tutor_sessions',
                               limit_choices_to={'user_type': 'student'})
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, 
                               related_name='tutor_sessions')
    
    # Session Details
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    topic = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Calendly Integration
    calendly_event_id = models.CharField(max_length=255, blank=True, null=True)
    calendly_event_url = models.URLField(blank=True, null=True)
    meeting_link = models.URLField(blank=True, null=True, help_text="Zoom, Google Meet, etc.")
    
    # Status
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='scheduled')
    
    # Payment
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_status = models.CharField(max_length=20,
                                     choices=[('pending', 'Pending'), ('paid', 'Paid'), 
                                            ('refunded', 'Refunded')],
                                     default='pending')
    
    # Completion
    completed_at = models.DateTimeField(null=True, blank=True)
    session_notes = models.TextField(blank=True, null=True)
    
    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tutor_sessions'
        verbose_name = 'Tutor Session'
        verbose_name_plural = 'Tutor Sessions'
        ordering = ['-scheduled_at']
        indexes = [
            models.Index(fields=['tutor', 'status']),
            models.Index(fields=['student', 'scheduled_at']),
            models.Index(fields=['scheduled_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.session_number:
            year = timezone.now().year
            count = TutorSession.objects.filter(created_at__year=year).count() + 1
            self.session_number = f"SES-{year}-{count:05d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.session_number} - {self.tutor.user.get_full_name()} & {self.student.get_full_name()}"


class SessionReview(models.Model):
    """Student reviews for tutor sessions"""
    session = models.OneToOneField(TutorSession, on_delete=models.CASCADE, 
                                   related_name='review')
    
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(blank=True, null=True)
    
    # Specific Ratings
    expertise_rating = models.PositiveIntegerField(null=True, blank=True,
                                                   validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication_rating = models.PositiveIntegerField(null=True, blank=True,
                                                       validators=[MinValueValidator(1), MaxValueValidator(5)])
    helpfulness_rating = models.PositiveIntegerField(null=True, blank=True,
                                                     validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Visibility
    is_public = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'session_reviews'
        verbose_name = 'Session Review'
        verbose_name_plural = 'Session Reviews'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.session.session_number} - {self.rating}⭐"


# ============================================================================
# 7. CONTENT & RESOURCES MODULE
# ============================================================================

class Resource(models.Model):
    """Preparation resources and study materials"""
    RESOURCE_TYPES = (
        ('pdf', 'PDF Document'),
        ('video', 'Video'),
        ('article', 'Article'),
        ('practice_test', 'Practice Test'),
        ('guide', 'Study Guide'),
        ('link', 'External Link'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    description = models.TextField(blank=True, null=True)
    
    # Relationships
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, 
                               related_name='resources')
    competitions = models.ManyToManyField(Competition, blank=True, 
                                         related_name='resources')
    
    # Content
    file = models.FileField(upload_to='resources/', null=True, blank=True)
    external_url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='resources/thumbnails/', blank=True, null=True)
    
    # Access Control
    is_free = models.BooleanField(default=True)
    required_subscription_level = models.CharField(max_length=20, 
                                                   choices=[('free', 'Free'), 
                                                          ('basic', 'Basic'), 
                                                          ('premium', 'Premium')],
                                                   default='free')
    
    # Metadata
    author = models.CharField(max_length=255, blank=True, null=True)
    published_date = models.DateField(null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    downloads_count = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resources'
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['subject', 'resource_type']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"


class BlogPost(models.Model):
    """Blog posts and news articles"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    
    # Content
    excerpt = models.TextField(blank=True, null=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    
    # Author
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                              related_name='blog_posts',
                              limit_choices_to={'user_type': 'admin'})
    
    # Categorization
    category = models.CharField(max_length=100, blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement
    views_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blog_posts'
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ['-published_at', '-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title


class FAQ(models.Model):
    """Frequently Asked Questions"""
    CATEGORIES = (
        ('general', 'General'),
        ('subscriptions', 'Subscriptions'),
        ('applications', 'Applications'),
        ('travel', 'Travel'),
        ('tutoring', 'Tutoring'),
        ('payments', 'Payments'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    question = models.TextField()
    answer = models.TextField()
    
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    views_count = models.PositiveIntegerField(default=0)
    helpful_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'faqs'
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['category', 'display_order']
    
    def __str__(self):
        return f"{self.get_category_display()}: {self.question[:50]}"


# ============================================================================
# 8. NOTIFICATIONS MODULE
# ============================================================================

class EmailTemplate(models.Model):
    """Email templates for automated notifications"""
    TEMPLATE_TYPES = (
        ('welcome', 'Welcome Email'),
        ('application_submitted', 'Application Submitted'),
        ('application_accepted', 'Application Accepted'),
        ('application_rejected', 'Application Rejected'),
        ('deadline_reminder', 'Deadline Reminder'),
        ('payment_confirmation', 'Payment Confirmation'),
        ('session_reminder', 'Session Reminder'),
        ('subscription_expiring', 'Subscription Expiring'),
        ('quote_ready', 'Travel Quote Ready'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES, unique=True)
    
    subject = models.CharField(max_length=255)
    body_html = models.TextField(help_text="HTML email body with placeholders")
    body_text = models.TextField(help_text="Plain text version")
    
    # Variables available in template (stored as JSON for documentation)
    available_variables = models.JSONField(default=dict, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'email_templates'
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class Notification(models.Model):
    """User notifications (in-app and email)"""
    NOTIFICATION_TYPES = (
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('reminder', 'Reminder'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Links
    action_url = models.URLField(blank=True, null=True)
    action_text = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Email
    send_email = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ScheduledNotification(models.Model):
    """Scheduled notifications (e.g., deadline reminders)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Recipient
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                            related_name='scheduled_notifications')
    
    # Template
    email_template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE,
                                      related_name='scheduled_notifications')
    
    # Scheduling
    scheduled_for = models.DateTimeField()
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Context (data to populate template)
    context_data = models.JSONField(default=dict, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduled_notifications'
        verbose_name = 'Scheduled Notification'
        verbose_name_plural = 'Scheduled Notifications'
        ordering = ['scheduled_for']
        indexes = [
            models.Index(fields=['scheduled_for', 'sent']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.email_template.name} - {self.scheduled_for}"


# ============================================================================
# 9. ADDITIONAL MODELS
# ============================================================================

class ContactMessage(models.Model):
    """Contact form submissions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    
    # Optional: if user is logged in
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                            related_name='contact_messages')
    
    # Status
    is_read = models.BooleanField(default=False)
    is_responded = models.BooleanField(default=False)
    response = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='responded_messages')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'contact_messages'
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.email} - {self.created_at.date()}"


class ActivityLog(models.Model):
    """Audit log for important user actions"""
    ACTION_TYPES = (
        ('user_registered', 'User Registered'),
        ('user_login', 'User Login'),
        ('subscription_created', 'Subscription Created'),
        ('application_submitted', 'Application Submitted'),
        ('application_status_changed', 'Application Status Changed'),
        ('payment_made', 'Payment Made'),
        ('document_uploaded', 'Document Uploaded'),
        ('session_booked', 'Session Booked'),
        ('quote_generated', 'Quote Generated'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    
    # Additional context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activity_logs'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} - {self.created_at}"


"""
END OF MODELS

Additional Recommendations:
1. Use PostgreSQL for better JSON field support
2. Implement Django Signals for:
   - Auto-updating statistics (total_applications, total_sessions, etc.)
   - Sending notifications on status changes
   - Creating activity logs
3. Use Django REST Framework for API
4. Implement Celery for:
   - Scheduled notifications
   - Quote generation
   - Email sending
5. Use django-storages for S3 file uploads
6. Implement proper indexes in production
7. Add database-level constraints where appropriate
8. Use select_related() and prefetch_related() for query optimization
"""