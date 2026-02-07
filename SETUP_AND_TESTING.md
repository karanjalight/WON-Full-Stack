# Quick Setup & Testing Guide

## Prerequisites
- Django 5.0.6+ installed
- Database configured (SQLite works for testing)
- All migrations applied

## Step 1: Apply Migrations
```bash
cd won-fullstack
python3 manage.py makemigrations
python3 manage.py migrate
```

## Step 2: Create Superuser (if not already created)
```bash
python3 manage.py createsuperuser
```

## Step 3: Create Subscription Plans

1. Start the development server:
```bash
python3 manage.py runserver
```

2. Access Django Admin at `http://localhost:8000/admin/`

3. Create subscription plans for each user type:

### Parent Plan Example:
- **Name:** Parent Basic
- **Plan Type:** parent
- **Duration:** monthly
- **Price:** 29.99
- **Currency:** USD
- **Description:** Perfect for parents managing 1-3 children
- **Features:** (as JSON)
  ```json
  ["Up to 3 children", "Unlimited applications", "Email support", "Application tracking"]
  ```
- **Max Students:** 3
- **Is Active:** ✓

### Student Plan Example:
- **Name:** Student Explorer
- **Plan Type:** student
- **Duration:** monthly
- **Price:** 19.99
- **Currency:** USD
- **Description:** For independent students pursuing olympiad dreams
- **Features:**
  ```json
  ["Unlimited applications", "Tutor access", "Travel assistance", "Resource library"]
  ```
- **Is Active:** ✓
- **Is Featured:** ✓

### School Plan Example:
- **Name:** School Standard
- **Plan Type:** school
- **Duration:** annually
- **Price:** 499.99
- **Currency:** USD
- **Description:** Comprehensive solution for schools
- **Features:**
  ```json
  ["Up to 50 students", "Bulk applications", "Dedicated support", "Analytics dashboard", "Custom branding"]
  ```
- **Max Students:** 50
- **Is Active:** ✓

## Step 4: Test the Complete Flow

### 4.1 Test Signup & Onboarding

1. **Navigate to signup page:**
   `http://localhost:8000/signup/`

2. **Create a new user:**
   - Username: testparent
   - Email: parent@test.com
   - First Name: Test
   - Last Name: Parent
   - Phone: +1234567890
   - User Type: Parent
   - Password: testpass123

3. **After signup, you should be redirected to:**
   `http://localhost:8000/onboarding/subscription/`

4. **You should see:**
   - Parent subscription plans
   - Monthly/Quarterly/Annually tabs
   - "Subscribe Now" buttons

### 4.2 Test Subscription Checkout

1. **Click "Subscribe Now" on any plan**

2. **You should be redirected to:**
   `http://localhost:8000/subscriptions/<plan-id>/checkout/`

3. **Review the checkout page:**
   - Plan details in sidebar
   - Payment method selection
   - Terms and conditions checkbox

4. **Select payment method and submit:**
   - Choose "Pay with Card (Paystack)"
   - Check "I agree to the Terms and Conditions"
   - Click "Proceed to Payment"

### 4.3 Test Payment Flow (Mock)

1. **You'll be redirected to:**
   `http://localhost:8000/subscriptions/payment/initiate/<transaction-id>/`

2. **For testing without actual Paystack:**
   - The Paystack button will appear
   - To simulate successful payment, manually update the database:

```bash
python3 manage.py shell
```

```python
from backend.models import PaymentTransaction, UserSubscription
from django.utils import timezone

# Get the latest transaction
transaction = PaymentTransaction.objects.latest('created_at')

# Mark as completed
transaction.status = 'completed'
transaction.paid_at = timezone.now()
transaction.save()

# Activate subscription
subscription = transaction.subscription
subscription.status = 'active'
subscription.save()

# Update user onboarding
user = transaction.user
user.has_completed_onboarding = True
user.onboarding_step = 'completed'
user.onboarded_at = timezone.now()
user.save()

print(f"✅ Subscription activated for {user.username}")
exit()
```

### 4.4 Test Dashboard Access

1. **Navigate to dashboard:**
   `http://localhost:8000/dashboard/`

2. **You should see:**
   - Parent-specific dashboard
   - Stats cards (children, applications, etc.)
   - Subscription status card
   - Sidebar navigation

3. **Test navigation items:**
   - Dashboard → Main dashboard
   - My Subscription → Subscription management
   - Profile → Profile settings
   - My Children → Children management (parent only)
   - Notifications → Notifications center
   - Settings → Account settings

## Step 5: Test Different User Roles

### Create a Student User:
1. Logout and create new account with user_type='student'
2. Complete onboarding with student plan
3. Access student dashboard
4. Verify student-specific features

### Create a School User:
1. Logout and create new account with user_type='school'
2. Complete onboarding with school plan
3. Access school dashboard
4. Verify school-specific features

## Step 6: Configure Paystack (Production)

### For Real Payments:

1. **Sign up for Paystack:**
   - Visit https://paystack.com
   - Create an account
   - Get API keys from dashboard

2. **Add keys to settings.py:**
```python
# At the bottom of won/settings.py
PAYSTACK_PUBLIC_KEY = 'pk_test_xxxxxxxxxxxxx'  # Test key
PAYSTACK_SECRET_KEY = 'sk_test_xxxxxxxxxxxxx'  # Test secret key

# For production:
# PAYSTACK_PUBLIC_KEY = 'pk_live_xxxxxxxxxxxxx'
# PAYSTACK_SECRET_KEY = 'sk_live_xxxxxxxxxxxxx'
```

3. **Update Paystack payment template:**
   - Edit `templates/dashboard/paystack_payment.html`
   - Replace the placeholder key with `{{ paystack_public_key }}`
   - Ensure it loads from settings

4. **Set up webhook:**
   - In Paystack dashboard, go to Settings → Webhooks
   - Add webhook URL: `https://yourdomain.com/subscriptions/payment/webhook/`
   - Paystack will send payment notifications here

5. **Test with Paystack test cards:**
   - Card: 4084 0840 8408 4081
   - CVV: 408
   - Expiry: Any future date
   - OTP: 123456

## Troubleshooting

### Issue: URL not found
**Solution:** Make sure all URL patterns are added to `won/urls.py`

### Issue: Template does not exist
**Solution:** Check template path in `templates/dashboard/` folder

### Issue: Dashboard shows "No active subscription"
**Solution:** Manually activate subscription via Django shell (see Step 4.3)

### Issue: Paystack payment doesn't work
**Solution:** 
- Check if Paystack keys are configured
- Use test mode first before production
- Check browser console for JavaScript errors

### Issue: Permission denied on dashboard
**Solution:** Make sure user is logged in and has correct user_type

## Testing Checklist

- [ ] Can create new user account
- [ ] Redirected to onboarding after signup
- [ ] Can view subscription plans
- [ ] Can access checkout page
- [ ] Can see payment initiation page
- [ ] Subscription activates after payment
- [ ] Dashboard shows correct role-specific content
- [ ] Can navigate between dashboard pages
- [ ] Subscription management page works
- [ ] Mobile responsive design works
- [ ] Can logout and login again

## Next Steps

1. **Customize Plans:** Adjust subscription plans in admin
2. **Design Tweaks:** Modify Tailwind classes in templates
3. **Add Features:** Implement children/student management
4. **Production Setup:** Configure Paystack live keys
5. **Deploy:** Set up production server and database

## Support

For issues, check:
- Django error logs
- Browser console (F12)
- Database migrations status
- Template paths
- URL patterns

---

**Happy Testing! 🚀**
