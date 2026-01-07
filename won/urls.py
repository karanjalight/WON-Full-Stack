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
    
    # News/Resources
    path('news/', views.news, name='news'),
    path('news/<int:pk>/', views.news_details, name='news-details'),
    
    # Team (Tutors)
    path('team/', views.team, name='team'),
    path('team/<int:pk>/', views.team_details, name='team-details'),
    
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
]

# Custom 404 handler
handler404 = 'core.views.error_404'

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
