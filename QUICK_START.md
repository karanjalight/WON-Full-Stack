# Quick Start Guide: SaaS Features

## What's New

Your World Olympiad Network platform now has full end-to-end SaaS features:

✅ **Login redirects to dashboard** - No more generic account page
✅ **Subscription inheritance** - Students automatically inherit parent/school subscriptions
✅ **Application visibility** - Parents and schools see all their students' applications
✅ **Subscription enforcement** - Applications require active subscriptions
✅ **Admin access** - Students created by subscribed accounts get full access
✅ **Complete permissions** - All views properly check subscription and ownership

## How to Test

### 1. Test Parent Flow
```bash
# Start the server
python manage.py runserver

# In browser:
1. Sign up as Parent
2. Subscribe to a parent plan
3. Add a child account (Dashboard → Children → Add Child)
4. Logout and login as the child
5. Notice: Child can access dashboard without subscribing
6. Notice: Child can apply for competitions (using parent's subscription)
7. Logout and login as parent again
8. Notice: Parent sees child's applications in dashboard
```

### 2. Test School Flow
```bash
# In browser:
1. Sign up as School
2. Subscribe to a school plan
3. Add student accounts (Dashboard → Students → Add Student)
4. Logout and login as student
5. Notice: Student can access dashboard and apply
6. Submit an application
7. Logout and login as school
8. Notice: School sees student's application
```

### 3. Test Subscription Enforcement
```bash
# In browser:
1. Sign up as Student (don't subscribe)
2. Try to apply for competition
3. Notice: Redirected to subscription page
4. Subscribe to student plan
5. Now can apply for competitions
```

## Database Setup

If you have existing data, run this migration script:

```bash
python manage.py shell
```

Then paste this:

```python
from backend.models import User

# Update students to set created_by field
print("Updating student accounts...")

# For students with parent
students_with_parent = User.objects.filter(
    user_type='student', 
    parent__isnull=False, 
    created_by__isnull=True
)
for student in students_with_parent:
    student.created_by = student.parent
    student.save()
print(f"Updated {students_with_parent.count()} students with parent relationship")

# For students with school
students_with_school = User.objects.filter(
    user_type='student', 
    school__isnull=False, 
    created_by__isnull=True
)
for student in students_with_school:
    student.created_by = student.school
    student.save()
print(f"Updated {students_with_school.count()} students with school relationship")

print("Migration complete!")
```

## Key URLs

- **Login**: `/login/` → Redirects to `/dashboard/`
- **Parent Dashboard**: `/dashboard/` (auto-routes based on user type)
- **School Dashboard**: `/dashboard/` (auto-routes based on user type)
- **Student Dashboard**: `/dashboard/` (auto-routes based on user type)
- **Children Management**: `/dashboard/children/`
- **Students Management**: `/dashboard/students/`
- **Add Child**: `/dashboard/children/add/`
- **Add Student**: `/dashboard/students/add/`
- **Applications**: `/dashboard/applications/`
- **Subscription**: `/dashboard/subscription/`

## Helper Methods Available

```python
from backend.models import User

# Get any user
user = User.objects.get(username='student1')

# Check subscription status
has_sub = user.has_active_subscription()
print(f"Has subscription: {has_sub}")

# Get subscription details with source
subscription, source_type, source_user = user.get_subscription_source()
print(f"Subscription from: {source_type}")  # 'own', 'parent', or 'school'

# Check if can submit applications
can_apply = user.can_submit_application()
print(f"Can apply: {can_apply}")

# Check dashboard access
has_access = user.has_dashboard_access()
print(f"Has dashboard access: {has_access}")

# Check admin access (for students)
has_admin = user.has_inherited_admin_access
print(f"Has inherited admin: {has_admin}")
```

## Template Context

All dashboard templates now have these variables:

```django
{{ active_subscription }}      {# Subscription object #}
{{ subscription_source }}       {# 'own', 'parent', or 'school' #}
{{ subscription_owner }}        {# User who owns the subscription #}
{{ can_apply }}                {# Boolean - can submit applications #}
{{ recent_applications }}       {# QuerySet of applications #}
{{ children }}                 {# Parent's children (QuerySet) #}
{{ students }}                 {# School's students (QuerySet) #}
```

## Troubleshooting

### Login doesn't redirect to dashboard
- Check `core/views.py` line 42 and 54
- Should say `redirect('dashboard')` not `redirect('account')`

### Student can't access dashboard
- Check if parent/school has active subscription
- Verify `created_by` field is set on student
- Check using: `student.has_dashboard_access()`

### Applications not showing in parent/school dashboard
- Check if applications exist: `OlympiadApplication.objects.filter(student__created_by=parent_user)`
- Verify parent/school dashboard queries include `created_by` in filter

### Can't submit applications
- Check subscription: `user.get_subscription_source()`
- Check limits: `user.can_submit_application()`
- Verify plan has `max_applications` set (or None for unlimited)

## Next Steps

1. **Test all flows** (parent, school, student)
2. **Verify subscriptions work** (create test plans in admin)
3. **Check application limits** (ensure max_applications is respected)
4. **Test notifications** (parents/schools get notified on student applications)
5. **Review templates** (add subscription info display if needed)

## File Changes Summary

### Modified Files
- `core/views.py` - Login, dashboard, and child management views
- `backend/models.py` - User model helper methods
- `core/forms.py` - No changes (already had created_by logic)

### New Files
- `SAAS_FEATURES_IMPLEMENTATION.md` - Complete documentation
- `QUICK_START.md` - This file

### No Changes Needed
- Templates (backward compatible)
- URLs (no changes)
- Settings (no changes)
- Migrations (auto-generated if needed)

## Support

For detailed documentation, see:
- `SAAS_FEATURES_IMPLEMENTATION.md` - Full feature documentation
- `SUBSCRIPTION_FEATURE_README.md` - Subscription system details
- `CHILD_ACCOUNT_IMPLEMENTATION.md` - Child account management

Happy testing! 🚀
