"""
Custom Admin Views for WON
User Growth Analytics and Dashboard
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from datetime import timedelta
from .models import User, OlympiadApplication, UserSubscription, PaymentTransaction


@staff_member_required
def user_growth_view(request):
    """Custom admin view for user growth analytics with graph"""
    
    # Get period from request (default 30 days)
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get daily user counts
    daily_counts = User.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Get cumulative counts
    cumulative = []
    total_before = User.objects.filter(created_at__date__lt=start_date).count()
    total = total_before
    dates = []
    counts = []
    
    # Fill in all dates in range
    current_date = start_date
    daily_dict = {item['date']: item['count'] for item in daily_counts}
    
    while current_date <= end_date:
        count = daily_dict.get(current_date, 0)
        total += count
        dates.append(current_date.strftime('%Y-%m-%d'))
        counts.append(count)
        cumulative.append(total)
        current_date += timedelta(days=1)
    
    # Get user type breakdown
    breakdown = User.objects.values('user_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    user_types_dict = dict(User.USER_TYPES)
    
    # Get recent activity stats
    recent_applications = OlympiadApplication.objects.filter(
        created_at__date__gte=start_date
    ).count()
    
    recent_subscriptions = UserSubscription.objects.filter(
        created_at__date__gte=start_date
    ).count()
    
    recent_payments = PaymentTransaction.objects.filter(
        created_at__date__gte=start_date,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get user type distribution for pie chart
    import json
    user_type_labels = [user_types_dict.get(item['user_type'], item['user_type']) for item in breakdown]
    user_type_values = [item['count'] for item in breakdown]
    
    from django.contrib import admin
    
    context = {
        **admin.site.each_context(request),
        'dates': json.dumps(dates),
        'daily_counts': json.dumps(counts),
        'cumulative_counts': json.dumps(cumulative),
        'total_users': User.objects.count(),
        'period_total': sum(counts),
        'period_start': start_date.strftime('%Y-%m-%d'),
        'period_end': end_date.strftime('%Y-%m-%d'),
        'days': days,
        'user_type_breakdown': breakdown,
        'user_type_labels': json.dumps(user_type_labels),
        'user_type_values': json.dumps(user_type_values),
        'user_types_dict': user_types_dict,
        'recent_applications': recent_applications,
        'recent_subscriptions': recent_subscriptions,
        'recent_payments': recent_payments,
        'opts': User._meta,
        'has_view_permission': True,
        'title': 'User Growth Analytics',
    }
    
    request.current_app = admin.site.name
    
    return TemplateResponse(request, 'admin/user_growth.html', context)

