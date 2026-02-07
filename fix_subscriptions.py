"""
Quick fix script to activate subscriptions that were created during testing
Run this with: python3 manage.py shell < fix_subscriptions.py
"""

from backend.models import UserSubscription, PaymentTransaction
from django.utils import timezone

print("\n=== Fixing Subscriptions ===\n")

# Get all pending or expired subscriptions with completed payments
subscriptions = UserSubscription.objects.filter(status__in=['pending', 'expired'])

for subscription in subscriptions:
    # Check if there's a completed payment for this subscription
    completed_payment = PaymentTransaction.objects.filter(
        subscription=subscription,
        status='completed'
    ).first()
    
    if completed_payment:
        # Activate the subscription
        subscription.status = 'active'
        subscription.save()
        
        # Update user onboarding
        user = subscription.user
        user.has_completed_onboarding = True
        user.onboarding_step = 'completed'
        user.onboarded_at = timezone.now()
        user.save()
        
        print(f"✅ Activated subscription for {user.username} - {subscription.plan.name}")
    else:
        print(f"⚠️  No completed payment found for {subscription.user.username}'s subscription")

print("\n=== Done! ===\n")
