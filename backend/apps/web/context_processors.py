from django.utils import timezone

def global_web_context(request):
    """
    Context processor global injectant l'état d'abonnement et la configuration du thème
    dans tous les templates de l'application web.
    """
    is_premium = False
    profile = None
    
    if request.user.is_authenticated:
        try:
            profile = getattr(request.user, 'profile', None)
            if profile and profile.is_premium:
                is_premium = True
        except Exception:
            is_premium = False

    return {
        'is_premium': is_premium,
        'user_profile': profile,
        'now_year': timezone.now().year,
        'THEME_ACCENT_HEX': '47C26B',
    }
