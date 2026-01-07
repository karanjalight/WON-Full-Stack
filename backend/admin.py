"""
WON - World Olympiad Network
Comprehensive Django Admin Configuration
Professional Admin Interface with Analytics
"""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import Count, Sum, Q
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
import json
from ckeditor.widgets import CKEditorWidget

from .models import (
    # Users & Authentication
    User, ParentProfile, StudentProfile, SchoolProfile, TutorProfile,
    # Subscriptions & Payments
    SubscriptionPlan, UserSubscription, PaymentTransaction,
    # Olympiads & Competitions
    Subject, TutorSubject, Destination, Competition, CompetitionRound,
    # Applications & Documents
    OlympiadApplication, ApplicationDocument,
    # Travel & Quotes
    TravelQuote, TravelQuoteItem, TravelBookingRequest,
    # Tutoring & Sessions
    TutorSession, SessionReview,
    # Content & Resources
    Resource, BlogPost, FAQ,
    # Notifications
    EmailTemplate, Notification, ScheduledNotification,
    # Additional
    ContactMessage, ActivityLog,
)


# ============================================================================
# CUSTOM ADMIN SITE
# ============================================================================

class WONAdminSite(AdminSite):
    site_header = "WON - World Olympiad Network"
    site_title = "WON Admin"
    index_title = "Dashboard"


# ============================================================================
# INLINE ADMIN CLASSES
# ============================================================================

class ParentProfileInline(admin.StackedInline):
    model = ParentProfile
    can_delete = False
    verbose_name_plural = 'Parent Profile'
    fields = ('occupation', 'number_of_children', 'emergency_contact', 'preferred_contact_method')


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'
    fields = ('date_of_birth', 'grade_level', 'current_school', 'guardian_name', 
              'guardian_email', 'guardian_phone', 'interests', 'achievements',
              'passport_number', 'passport_expiry', 'national_id')


class SchoolProfileInline(admin.StackedInline):
    model = SchoolProfile
    can_delete = False
    verbose_name_plural = 'School Profile'
    fields = ('school_name', 'registration_number', 'school_type', 'principal_name',
              'principal_email', 'website', 'total_students', 'active_olympiad_students',
              'is_verified', 'verification_document')


class TutorProfileInline(admin.StackedInline):
    model = TutorProfile
    can_delete = False
    verbose_name_plural = 'Tutor Profile'
    fields = ('title', 'qualifications', 'experience_years', 'specializations',
              'hourly_rate', 'currency', 'calendly_link', 'is_featured', 'is_accepting_students')


class TravelQuoteItemInline(admin.TabularInline):
    model = TravelQuoteItem
    extra = 1
    fields = ('item_type', 'description', 'unit_cost', 'quantity', 'total_cost', 'provider')


class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 0
    fields = ('document_type', 'file', 'status', 'verified_by', 'verified_at', 'expiry_date')
    readonly_fields = ('verified_at',)


# ============================================================================
# USER ADMIN
# ============================================================================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'full_name', 'user_type', 'is_verified', 
                   'is_active', 'is_staff', 'created_at', 'user_stats')
    list_filter = ('user_type', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 
                  'created_at', 'country')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'country', 'city')
    readonly_fields = ('id', 'slug', 'created_at', 'updated_at', 'last_login_at', 'user_stats')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Authentication', {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'user_type', 'phone', 'profile_picture', 'bio')
        }),
        ('Location', {
            'fields': ('country', 'city', 'address')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_document', 'school_email', 'verified_at')
        }),
        ('Relationships', {
            'fields': ('created_by', 'parent', 'school')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Timestamps', {
            'fields': ('id', 'slug', 'created_at', 'updated_at', 'last_login_at')
        }),
        ('Statistics', {
            'fields': ('user_stats',)
        }),
    )
    
    inlines = [ParentProfileInline, StudentProfileInline, SchoolProfileInline, TutorProfileInline]
    
    def full_name(self, obj):
        return obj.get_full_name() or '-'
    full_name.short_description = 'Full Name'
    
    def user_stats(self, obj):
        stats = []
        if obj.user_type == 'student':
            apps = obj.applications.count()
            stats.append(f"Applications: {apps}")
        if obj.user_type == 'tutor':
            sessions = obj.tutor_profile.sessions.count() if hasattr(obj, 'tutor_profile') else 0
            stats.append(f"Sessions: {sessions}")
        subs = obj.subscriptions.filter(status='active').count()
        if subs > 0:
            stats.append(f"Active Subscriptions: {subs}")
        return format_html('<br>'.join(stats)) if stats else '-'
    user_stats.short_description = 'Statistics'


# ============================================================================
# PROFILE ADMINS
# ============================================================================

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'occupation', 'number_of_children', 'preferred_contact_method', 'created_at')
    list_filter = ('preferred_contact_method', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'occupation')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'grade_level', 'current_school', 'age_display', 'created_at')
    list_filter = ('grade_level', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 
                    'current_school', 'guardian_name', 'guardian_email')
    readonly_fields = ('created_at', 'updated_at', 'age_display')
    
    def age_display(self, obj):
        age = obj.get_age()
        return f"{age} years" if age else '-'
    age_display.short_description = 'Age'


@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'user', 'school_type', 'total_students', 
                   'active_olympiad_students', 'is_verified', 'created_at')
    list_filter = ('school_type', 'is_verified', 'created_at')
    search_fields = ('school_name', 'user__username', 'user__email', 'registration_number',
                    'principal_name', 'principal_email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'experience_years', 'hourly_rate', 'currency',
                   'average_rating', 'total_sessions', 'is_featured', 'is_accepting_students')
    list_filter = ('is_featured', 'is_accepting_students', 'currency', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name',
                    'title', 'qualifications', 'specializations')
    readonly_fields = ('created_at', 'updated_at')


# ============================================================================
# SUBSCRIPTIONS & PAYMENTS
# ============================================================================

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'duration', 'price', 'currency', 
                   'is_active', 'is_featured', 'subscriber_count', 'created_at')
    list_filter = ('plan_type', 'duration', 'is_active', 'is_featured', 'currency', 'created_at')
    search_fields = ('name', 'slug', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'subscriber_count')
    prepopulated_fields = {'slug': ('name', 'plan_type')}
    
    def subscriber_count(self, obj):
        return obj.subscriptions.filter(status='active').count()
    subscriber_count.short_description = 'Active Subscribers'


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date', 
                   'is_valid_display', 'auto_renew', 'payment_method', 'created_at')
    list_filter = ('status', 'auto_renew', 'payment_method', 'plan__plan_type', 
                  'start_date', 'end_date', 'created_at')
    search_fields = ('user__username', 'user__email', 'plan__name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'is_valid_display')
    date_hierarchy = 'created_at'
    
    def is_valid_display(self, obj):
        is_valid = obj.is_valid()
        color = 'green' if is_valid else 'red'
        text = 'Valid' if is_valid else 'Expired/Invalid'
        return format_html('<span style="color: {};">{}</span>', color, text)
    is_valid_display.short_description = 'Status'


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_number', 'user', 'transaction_type', 'amount', 'currency',
                   'status', 'payment_gateway', 'paid_at', 'created_at')
    list_filter = ('transaction_type', 'status', 'payment_gateway', 'currency', 
                  'created_at', 'paid_at')
    search_fields = ('user__username', 'user__email', 'gateway_reference', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'transaction_number')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('user', 'transaction_type', 'amount', 'currency', 'status', 'description')
        }),
        ('Payment Gateway', {
            'fields': ('payment_gateway', 'gateway_reference', 'gateway_response')
        }),
        ('Related Objects', {
            'fields': ('subscription', 'application', 'tutor_session')
        }),
        ('Timestamps', {
            'fields': ('id', 'paid_at', 'created_at', 'updated_at')
        }),
    )
    
    def transaction_number(self, obj):
        return str(obj.id)[:8].upper()
    transaction_number.short_description = 'Transaction #'


# ============================================================================
# OLYMPIADS & COMPETITIONS
# ============================================================================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_olympiads', 'total_tutors', 'is_active', 
                   'display_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'total_olympiads', 'total_tutors', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(TutorSubject)
class TutorSubjectAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'subject', 'experience_years', 'created_at')
    list_filter = ('subject', 'created_at')
    search_fields = ('tutor__user__username', 'tutor__user__email', 'subject__name')


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'region', 'total_olympiads', 
                   'is_active', 'created_at')
    list_filter = ('region', 'is_active', 'created_at')
    search_fields = ('name', 'city', 'country', 'continent')
    readonly_fields = ('id', 'total_olympiads', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('city', 'country')}
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'region', 'is_active')
        }),
        ('Location Details', {
            'fields': ('country', 'city', 'continent', 'iframe_url')
        }),
        ('Travel Information', {
            'fields': ('description', 'image', 'package_price_min', 'package_price_max', 'currency')
        }),
        ('Additional Information', {
            'fields': ('timezone', 'climate_info', 'visa_requirements'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_olympiads',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'subject', 'destination', 'start_date',
                   'application_deadline', 'status', 'total_applications', 
                   'is_featured', 'is_active')
    list_filter = ('subject', 'status', 'is_featured', 'is_active', 'start_date', 
                  'application_deadline', 'created_at')
    search_fields = ('name', 'short_name', 'description', 'organizer', 'contact_email')
    readonly_fields = ('id', 'total_applications', 'total_participants', 
                       'created_at', 'updated_at', 'application_status')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'start_date'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Ensure slug field is included in the form
        if 'slug' not in form.base_fields:
            from django import forms
            form.base_fields['slug'] = forms.SlugField(
                required=False,
                max_length=300,
                help_text="Auto-generated from name if left blank"
            )
        # Add CKEditor widgets for rich text fields
        form.base_fields['description'].widget = CKEditorWidget()
        form.base_fields['requirements'].widget = CKEditorWidget()
        return form
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'short_name', 'slug', 'subject', 'destination', 'description', 'requirements')
        }),
        ('Images', {
            'fields': ('image', 'banner_image')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'application_start_date', 'application_deadline')
        }),
        ('Requirements', {
            'fields': ('age_group_min', 'age_group_max')
        }),
        ('Pricing', {
            'fields': ('base_price', 'currency')
        }),
        ('Contact Information', {
            'fields': ('website', 'contact_email', 'organizer')
        }),
        ('Status & Features', {
            'fields': ('status', 'is_featured', 'is_active')
        }),
        ('Statistics', {
            'fields': ('total_applications', 'total_participants', 'application_status')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at')
        }),
    )
    
    def application_status(self, obj):
        if not obj or not obj.pk:
            return format_html('<span style="color: gray;">N/A</span>')
        today = timezone.now().date()
        if not obj.application_deadline:
            return format_html('<span style="color: gray;">Not Set</span>')
        if obj.application_deadline < today:
            return format_html('<span style="color: red;">Closed</span>')
        elif obj.application_start_date and obj.application_start_date > today:
            return format_html('<span style="color: orange;">Not Open Yet</span>')
        else:
            return format_html('<span style="color: green;">Open</span>')
    application_status.short_description = 'Application Status'


@admin.register(CompetitionRound)
class CompetitionRoundAdmin(admin.ModelAdmin):
    list_display = ('competition', 'round_type', 'name', 'date', 'registration_deadline',
                   'max_participants', 'is_active', 'created_at')
    list_filter = ('round_type', 'is_active', 'date', 'registration_deadline', 'created_at')
    search_fields = ('competition__name', 'name', 'location', 'description')
    readonly_fields = ('id', 'slug', 'created_at', 'updated_at')


# ============================================================================
# APPLICATIONS & DOCUMENTS
# ============================================================================

@admin.register(OlympiadApplication)
class OlympiadApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_number', 'student', 'competition', 'status',
                   'payment_status', 'total_cost', 'submitted_at', 'created_at')
    list_filter = ('status', 'payment_status', 'competition', 'submitted_at', 'created_at')
    search_fields = ('application_number', 'student__username', 'student__email',
                    'competition__name', 'emergency_contact_name', 'emergency_contact_phone')
    readonly_fields = ('id', 'application_number', 'created_at', 'updated_at', 
                      'submitted_at', 'reviewed_at', 'accepted_at')
    date_hierarchy = 'created_at'
    inlines = [ApplicationDocumentInline]
    
    fieldsets = (
        ('Application Details', {
            'fields': ('application_number', 'student', 'competition', 'round', 'status')
        }),
        ('Dates', {
            'fields': ('submitted_at', 'reviewed_at', 'accepted_at')
        }),
        ('Financial', {
            'fields': ('total_cost', 'payment_status')
        }),
        ('Application Content', {
            'fields': ('motivation_letter', 'special_requirements')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Admin Notes', {
            'fields': ('reviewer_notes', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at')
        }),
    )


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ('application', 'document_type', 'status', 'verified_by',
                   'verified_at', 'expiry_date', 'created_at')
    list_filter = ('document_type', 'status', 'verified_at', 'expiry_date', 'created_at')
    search_fields = ('application__application_number', 'file_name', 'verification_notes')
    readonly_fields = ('id', 'verified_at', 'uploaded_at', 'created_at', 'updated_at')


# ============================================================================
# TRAVEL & QUOTES
# ============================================================================

@admin.register(TravelQuote)
class TravelQuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_number', 'user', 'destination', 'departure_city',
                   'departure_date', 'return_date', 'total_estimate', 'currency',
                   'status', 'quote_valid_until', 'created_at')
    list_filter = ('status', 'currency', 'destination__region', 'departure_date',
                  'quote_valid_until', 'created_at')
    search_fields = ('quote_number', 'user__username', 'user__email', 
                    'destination__city', 'destination__country')
    readonly_fields = ('id', 'quote_number', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    inlines = [TravelQuoteItemInline]
    
    fieldsets = (
        ('Quote Details', {
            'fields': ('quote_number', 'user', 'application', 'destination', 'status')
        }),
        ('Travel Information', {
            'fields': ('departure_city', 'departure_country', 'departure_date', 'return_date',
                      'number_of_passengers', 'passenger_details')
        }),
        ('Pricing', {
            'fields': ('total_estimate', 'currency')
        }),
        ('Validity', {
            'fields': ('quote_valid_until',)
        }),
        ('Additional Information', {
            'fields': ('special_requests', 'notes')
        }),
        ('Read Trips Integration', {
            'fields': ('readtrips_quote_id', 'readtrips_response')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at')
        }),
    )


@admin.register(TravelQuoteItem)
class TravelQuoteItemAdmin(admin.ModelAdmin):
    list_display = ('quote', 'item_type', 'description', 'unit_cost', 'quantity',
                   'total_cost', 'provider', 'created_at')
    list_filter = ('item_type', 'created_at')
    search_fields = ('quote__quote_number', 'description', 'provider', 'booking_reference')
    readonly_fields = ('id', 'total_cost', 'created_at', 'updated_at')


@admin.register(TravelBookingRequest)
class TravelBookingRequestAdmin(admin.ModelAdmin):
    list_display = ('quote', 'status', 'contact_name', 'contact_email', 'contact_phone',
                   'readtrips_booking_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('quote__quote_number', 'contact_name', 'contact_email', 'contact_phone',
                    'readtrips_booking_id')
    readonly_fields = ('id', 'created_at', 'updated_at')


# ============================================================================
# TUTORING & SESSIONS
# ============================================================================

@admin.register(TutorSession)
class TutorSessionAdmin(admin.ModelAdmin):
    list_display = ('session_number', 'tutor', 'student', 'subject', 'scheduled_at',
                   'duration_minutes', 'status', 'amount', 'currency', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'currency', 'subject', 'scheduled_at', 'created_at')
    search_fields = ('session_number', 'tutor__user__username', 'student__username',
                    'topic', 'description')
    readonly_fields = ('id', 'session_number', 'created_at', 'updated_at')
    date_hierarchy = 'scheduled_at'
    
    fieldsets = (
        ('Session Details', {
            'fields': ('session_number', 'tutor', 'student', 'subject', 'status')
        }),
        ('Schedule', {
            'fields': ('scheduled_at', 'duration_minutes', 'topic', 'description')
        }),
        ('Calendly Integration', {
            'fields': ('calendly_event_id', 'calendly_event_url', 'meeting_link')
        }),
        ('Payment', {
            'fields': ('amount', 'currency', 'payment_status')
        }),
        ('Completion', {
            'fields': ('completed_at', 'session_notes')
        }),
        ('Cancellation', {
            'fields': ('cancelled_at', 'cancellation_reason')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at')
        }),
    )


@admin.register(SessionReview)
class SessionReviewAdmin(admin.ModelAdmin):
    list_display = ('session', 'rating', 'expertise_rating', 'communication_rating',
                   'helpfulness_rating', 'is_public', 'is_featured', 'created_at')
    list_filter = ('rating', 'is_public', 'is_featured', 'created_at')
    search_fields = ('session__session_number', 'review_text')
    readonly_fields = ('created_at', 'updated_at')


# ============================================================================
# CONTENT & RESOURCES
# ============================================================================

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'subject', 'is_free', 
                   'required_subscription_level', 'views_count', 'downloads_count',
                   'is_featured', 'is_active', 'created_at')
    list_filter = ('resource_type', 'is_free', 'required_subscription_level',
                  'is_featured', 'is_active', 'subject', 'created_at')
    search_fields = ('title', 'description', 'author')
    readonly_fields = ('id', 'views_count', 'downloads_count', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('competitions',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'published_at',
                   'views_count', 'comments_count', 'is_featured', 'created_at')
    list_filter = ('status', 'category', 'is_featured', 'published_at', 'created_at')
    search_fields = ('title', 'excerpt', 'content', 'author__username')
    readonly_fields = ('id', 'views_count', 'comments_count', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'featured_image')
        }),
        ('Author & Categorization', {
            'fields': ('author', 'category', 'tags')
        }),
        ('Status & Publishing', {
            'fields': ('status', 'published_at', 'is_featured')
        }),
        ('Engagement', {
            'fields': ('views_count', 'comments_count')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at')
        }),
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question_preview', 'category', 'display_order', 'is_active',
                   'views_count', 'helpful_count', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('question', 'answer')
    readonly_fields = ('id', 'views_count', 'helpful_count', 'created_at', 'updated_at')
    
    def question_preview(self, obj):
        return obj.question[:100] + '...' if len(obj.question) > 100 else obj.question
    question_preview.short_description = 'Question'


# ============================================================================
# NOTIFICATIONS
# ============================================================================

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'subject', 'is_active', 'created_at')
    list_filter = ('template_type', 'is_active', 'created_at')
    search_fields = ('name', 'subject', 'body_html', 'body_text')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'read_at',
                   'email_sent', 'created_at')
    list_filter = ('notification_type', 'is_read', 'email_sent', 'send_email', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'message')
    readonly_fields = ('id', 'read_at', 'email_sent_at', 'created_at')
    date_hierarchy = 'created_at'


@admin.register(ScheduledNotification)
class ScheduledNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_template', 'scheduled_for', 'sent', 'sent_at',
                   'retry_count', 'created_at')
    list_filter = ('sent', 'email_template', 'scheduled_for', 'created_at')
    search_fields = ('user__username', 'user__email', 'email_template__name', 'error_message')
    readonly_fields = ('id', 'sent_at', 'created_at', 'updated_at')
    date_hierarchy = 'scheduled_for'


# ============================================================================
# ADDITIONAL MODELS
# ============================================================================

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'is_responded',
                   'responded_by', 'created_at')
    list_filter = ('is_read', 'is_responded', 'created_at')
    search_fields = ('name', 'email', 'phone', 'subject', 'message')
    readonly_fields = ('id', 'responded_at', 'created_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'user')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Response', {
            'fields': ('is_read', 'is_responded', 'response', 'responded_by', 'responded_at')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at')
        }),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'description_preview', 'ip_address',
                   'created_at')
    list_filter = ('action_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'description', 'ip_address')
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'created_at'
    
    def description_preview(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_preview.short_description = 'Description'
    
    def has_add_permission(self, request):
        return False  # Activity logs are created automatically


# Add USER_TYPES_DICT to User model for easier access
User.USER_TYPES_DICT = dict(User.USER_TYPES)


# ============================================================================
# ADMIN SITE CUSTOMIZATION
# ============================================================================

# Customize admin site header
admin.site.site_header = "WON - World Olympiad Network"
admin.site.site_title = "WON Admin Portal"
admin.site.index_title = "Dashboard & Analytics"


# ============================================================================
# CUSTOM ADMIN INDEX VIEW
# ============================================================================

from django.template.response import TemplateResponse

def custom_admin_index(request, extra_context=None):
    """
    Custom admin index view with statistics
    """
    from .models import User, Competition, OlympiadApplication, PaymentTransaction
    
    # Calculate statistics
    total_users = User.objects.count()
    total_competitions = Competition.objects.count()
    total_applications = OlympiadApplication.objects.count()
    
    # Calculate total revenue from completed payments
    revenue_result = PaymentTransaction.objects.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))
    total_revenue = revenue_result['total'] or 0
    
    # Get app list from default admin index
    app_list = admin.site.get_app_list(request)
    
    # Organize models into logical groups
    organized_apps = []
    for app in app_list:
        if app['name'] == 'Backend' and app['models']:
            # Group backend models by category
            models = app['models']
            organized_models = sorted(models, key=lambda x: (
                # Users first
                0 if 'User' in x['name'] and 'Profile' not in x['name'] else
                1 if 'Parent' in x['name'] or 'Student' in x['name'] or 'School' in x['name'] or 'Tutor' in x['name'] else
                # Subscriptions & Payments
                2 if 'Subscription' in x['name'] or 'Payment' in x['name'] else
                # Competitions
                3 if 'Competition' in x['name'] or 'Subject' in x['name'] or 'Destination' in x['name'] else
                # Applications
                4 if 'Application' in x['name'] else
                # Travel
                5 if 'Travel' in x['name'] else
                # Tutoring
                6 if 'Tutor' in x['name'] or 'Session' in x['name'] else
                # Content
                7 if 'Resource' in x['name'] or 'Blog' in x['name'] or 'FAQ' in x['name'] else
                # Notifications
                8 if 'Notification' in x['name'] or 'Email' in x['name'] else
                # Other
                9
            ))
            app['models'] = organized_models
        organized_apps.append(app)
    
    context = {
        **admin.site.each_context(request),
        'title': admin.site.index_title or admin.site.site_title,
        'app_list': organized_apps,
        'total_users': total_users,
        'total_competitions': total_competitions,
        'total_applications': total_applications,
        'total_revenue': total_revenue,
        **(extra_context or {}),
    }
    
    request.current_app = admin.site.name
    
    return TemplateResponse(request, 'admin/index.html', context)

# Override the admin index view
admin.site.index = custom_admin_index
