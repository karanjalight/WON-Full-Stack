from django.conf import settings


def google_tag_manager(request):
    """Expose GTM container ID to templates when tracking is enabled."""
    gtm_id = (getattr(settings, 'GOOGLE_TAG_MANAGER_ID', '') or '').strip()
    disabled = getattr(settings, 'GOOGLE_TAG_MANAGER_DISABLED', False)
    enabled = bool(gtm_id) and not disabled
    return {
        'google_tag_manager_id': gtm_id if enabled else '',
        'google_tag_manager_enabled': enabled,
    }


def site_contact(request):
    """Public support email and phone for templates."""
    phone = getattr(settings, 'WON_SUPPORT_PHONE', '0738509200')
    # Display with spacing: 0738509200 -> 0738 509 200
    if len(phone) == 10 and phone.isdigit():
        phone_display = f'{phone[:4]} {phone[4:7]} {phone[7:]}'
    else:
        phone_display = phone
    return {
        'won_support_email': getattr(settings, 'WON_SUPPORT_EMAIL', 'support@worldolympiads.org'),
        'won_support_phone': phone_display,
        'won_support_phone_tel': getattr(settings, 'WON_SUPPORT_PHONE_TEL', '+254738509200'),
        'won_social_instagram': getattr(settings, 'WON_SOCIAL_INSTAGRAM', ''),
        'won_social_x': getattr(settings, 'WON_SOCIAL_X', ''),
        'won_social_linkedin': getattr(settings, 'WON_SOCIAL_LINKEDIN', ''),
        'won_social_facebook': getattr(settings, 'WON_SOCIAL_FACEBOOK', ''),
        'won_social_youtube': getattr(settings, 'WON_SOCIAL_YOUTUBE', ''),
    }
