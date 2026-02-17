"""
URL configuration for won project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from core import views
from backend.admin_views import user_growth_view

urlpatterns = [
    # Admin - Custom analytics route must come before admin.site.urls
    path('admin/analytics/user-growth/', user_growth_view, name='admin_user_growth'),
    path('admin/', admin.site.urls),
    
    # Main pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    
    # Destinations (Trips)
    path('destination/', views.destination, name='destination'),
    path('destination/<slug:slug>/', views.destination_details, name='destination-details'),
    
    # Subjects
    path('subjects/', views.subjects, name='subjects'),
    path('subjects/<slug:slug>/', views.subject_details, name='subject-details'),
    
    # Past Papers
    path('past-papers/', views.past_papers, name='past_papers'),
    path('past-papers/cart/', views.past_papers_cart, name='past_papers_cart'),
    path('past-papers/checkout/', views.past_papers_checkout, name='past_papers_checkout'),
    path('past-papers/<slug:slug>/', views.past_paper_detail, name='past_paper_detail'),
    
    # News/Resources
    path('news/', views.news, name='news'),
    path('news/<int:pk>/', views.news_details, name='news-details'),
    
    # Events
    path('events/', views.events_list, name='events'),
    path('events/<slug:slug>/', views.event_detail, name='event-detail'),
    
    # Tutors
    path('tutors/', views.team, name='team'),
    path('tutors/<uuid:pk>/', views.team_details, name='team-details'),
    path('tutors/<uuid:pk>/book/', views.book_tutor_session, name='book-tutor-session'),
    path('tutor-session/<uuid:session_id>/confirmation/', views.tutor_session_confirmation, name='tutor-session-confirmation'),
    # Redirect old team URLs to tutors for backward compatibility
    path('team/', RedirectView.as_view(url='/tutors/', permanent=True), name='team-old'),
    path('team/<uuid:pk>/', RedirectView.as_view(pattern_name='team-details', permanent=True), name='team-details-old'),
    
    # Tours (Competitions/Olympiads)
    path('tour/', views.tour, name='tour'),
    path('tour-2/', views.tour_2, name='tour-2'),
    path('olympiads/', views.olympiads, name='olympiads'),
    # Redirect tour-list to olympiads
    path('tour-list/', RedirectView.as_view(url='/olympiads/', permanent=True), name='tour-list'),
    # Olympiad detail page
    path('olympiad/<slug:slug>/', views.olympiad_details, name='olympiad-details'),
    # Redirect old tour-details to olympiad-details
    path('tour/<slug:slug>/', RedirectView.as_view(pattern_name='olympiad-details', permanent=True), name='tour-details'),
    
    # Application Flow
    path('apply/<slug:slug>/', views.start_application, name='start-application'),
    path('application/step/<int:step>/', views.application_step, name='application-step'),
    path('application/success/<uuid:application_id>/', views.application_success, name='application-success'),
    path('application/<uuid:application_id>/quotation/pdf/', views.download_quotation_pdf, name='download-quotation-pdf'),
    path('application/upload-document/', views.upload_document, name='upload-document'),
    
    # Travel Quote Generation
    path('travel-quote/', views.generate_travel_quote, name='generate-travel-quote'),
    path('travel-quote/<slug:slug>/', views.generate_travel_quote, name='generate-travel-quote-destination'),
    path('travel-quote/detail/<uuid:quote_id>/', views.travel_quote_detail, name='travel-quote-detail'),
    path('travel-quote/<uuid:quote_id>/download/', views.download_travel_quote_pdf, name='download-travel-quote-pdf'),
    path('api/travel/departure-countries/', views.departure_countries_api, name='departure-countries-api'),
    path('api/travel/departure-cities/', views.departure_cities_api, name='departure-cities-api'),
    
    # Subscriptions
    path('subscriptions/parents/', views.subscription_parents, name='subscription-parents'),
    path('subscriptions/schools/', views.subscription_schools, name='subscription-schools'),
    path('subscriptions/students/', views.subscription_students, name='subscription-students'),
    
    # Subscription Checkout & Payment
    path('subscriptions/<uuid:plan_id>/checkout/', views.subscription_checkout, name='subscription-checkout'),
    path('subscriptions/payment/initiate/<uuid:transaction_id>/', views.initiate_paystack_payment, name='initiate-paystack-payment'),
    path('subscriptions/payment/verify/<uuid:transaction_id>/', views.verify_paystack_payment, name='verify-paystack-payment'),
    path('subscriptions/payment/webhook/', views.paystack_webhook, name='paystack-webhook'),
    
    # Onboarding
    path('onboarding/subscription/', views.onboarding_subscription, name='onboarding-subscription'),
    
    # Dashboard Routes
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/subscription/', views.dashboard_subscription, name='dashboard_subscription'),
    path('dashboard/subscription/<uuid:subscription_id>/cancel/', views.cancel_pending_subscription, name='cancel_pending_subscription'),
    path('dashboard/profile/', views.dashboard_profile, name='dashboard_profile'),
    path('dashboard/children/', views.dashboard_children, name='dashboard_children'),
    path('dashboard/children/add/', views.add_child, name='add_child'),
    path('dashboard/children/<uuid:child_id>/edit/', views.edit_child, name='edit_child'),
    path('dashboard/children/<uuid:child_id>/delete/', views.delete_child, name='delete_child'),
    path('dashboard/children/<uuid:child_id>/view/', views.child_dashboard_view, name='child_dashboard_view'),
    path('dashboard/students/', views.dashboard_students, name='dashboard_students'),
    path('dashboard/students/add/', views.add_school_student, name='add_school_student'),
    path('dashboard/students/<uuid:child_id>/edit/', views.edit_child, name='edit_student'),
    path('dashboard/students/<uuid:child_id>/delete/', views.delete_child, name='delete_student'),
    path('dashboard/students/<uuid:child_id>/view/', views.child_dashboard_view, name='student_dashboard_view'),
    path('dashboard/applications/', views.dashboard_applications, name='dashboard_applications'),
    path('dashboard/applications/<uuid:application_id>/', views.application_detail, name='application_detail'),
    path('dashboard/tutor-sessions/', views.dashboard_tutor_sessions, name='dashboard_tutor_sessions'),
    path('dashboard/tutor-sessions/<uuid:session_id>/', views.dashboard_tutor_session_detail, name='dashboard_tutor_session_detail'),
    path('dashboard/tutor-calendar/', views.tutor_calendar, name='tutor_calendar'),
    path('dashboard/notifications/', views.dashboard_notifications, name='dashboard_notifications'),
    path('dashboard/settings/', views.dashboard_settings, name='dashboard_settings'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('account/', views.account_view, name='account'),
]

# Custom 404 handler
handler404 = 'core.views.error_404'

# Serve static files in development
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
