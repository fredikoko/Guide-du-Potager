import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import EmailVerificationCode

def generate_numeric_code(length=6):
    """Génère un code numérique aléatoire à N chiffres (par défaut 6)."""
    return "".join(random.choices("0123456789", k=length))

def send_verification_email(email, purpose='registration', user=None):
    """
    Génère un code à 6 chiffres, l'enregistre en base et l'envoie par e-mail.
    Durée de validité : 15 minutes.
    """
    email_clean = email.strip().lower()
    code = generate_numeric_code(6)
    expires_at = timezone.now() + timedelta(minutes=15)

    # Invalider les anciens codes non utilisés pour cet email et cet objectif
    EmailVerificationCode.objects.filter(
        email__iexact=email_clean,
        purpose=purpose,
        is_used=False
    ).update(is_used=True)

    # Créer le nouvel enregistrement de code
    EmailVerificationCode.objects.create(
        user=user,
        email=email_clean,
        code=code,
        purpose=purpose,
        expires_at=expires_at,
        is_used=False
    )

    # Sujet et message personnalisés selon l'objectif
    if purpose == 'registration':
        subject = "Votre code de confirmation - Guide du Potager Tropical"
        message = (
            f"Bonjour,\n\n"
            f"Bienvenue sur le Guide du Potager Tropical !\n\n"
            f"Voici votre code de confirmation pour finaliser la création de votre compte :\n\n"
            f"    👉  {code}  👈\n\n"
            f"Ce code est valable pendant 15 minutes.\n"
            f"Si vous n'avez pas demandé la création de ce compte, vous pouvez ignorer cet e-mail.\n\n"
            f"À très bientôt pour cultiver avec succès !\n"
            f"L'équipe du Guide du Potager Tropical"
        )
    else:  # email_change
        subject = "Confirmation de votre nouvelle adresse e-mail - Guide du Potager Tropical"
        message = (
            f"Bonjour,\n\n"
            f"Une demande de changement d'adresse e-mail a été effectuée sur votre compte.\n\n"
            f"Voici votre code de confirmation à renseigner dans l'application pour valider cette adresse :\n\n"
            f"    👉  {code}  👈\n\n"
            f"Ce code est valable pendant 15 minutes.\n"
            f"Si vous n'êtes pas à l'origine de cette demande, veuillez sécuriser votre compte immédiatement.\n\n"
            f"L'équipe du Guide du Potager Tropical"
        )

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@guidedupotagertropical.com')

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[email_clean],
        fail_silently=False
    )

    return code

def verify_email_code(email, code, purpose='registration', user=None):
    """
    Vérifie la validité d'un code de confirmation.
    Lève une ValidationError si le code est incorrect, expiré ou déjà utilisé.
    """
    if not code or not isinstance(code, str):
        raise ValidationError("Le code de confirmation est obligatoire.")

    email_clean = email.strip().lower()
    code_clean = code.strip()

    qs = EmailVerificationCode.objects.filter(
        email__iexact=email_clean,
        code=code_clean,
        purpose=purpose,
        is_used=False
    ).order_by('-created_at')

    if user and getattr(user, 'pk', None):
        # Pour le changement d'email, on peut facultativement vérifier le user associé
        qs_user = qs.filter(user=user)
        if qs_user.exists():
            qs = qs_user

    record = qs.first()

    if not record:
        raise ValidationError("Code de confirmation invalide ou déjà utilisé.")

    if timezone.now() > record.expires_at:
        record.is_used = True
        record.save(update_fields=['is_used'])
        raise ValidationError("Ce code de confirmation a expiré. Veuillez en demander un nouveau.")

    # Consommer le code
    record.is_used = True
    record.save(update_fields=['is_used'])
    return True
