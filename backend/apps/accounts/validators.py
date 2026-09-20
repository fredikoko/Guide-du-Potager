import re
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

DISPOSABLE_EMAIL_DOMAINS = {
    'yopmail.com', 'yopmail.fr', 'yopmail.net',
    'mailinator.com', 'tempmail.com', 'temp-mail.org',
    '10minutemail.com', 'guerrillamail.com', 'trashmail.com',
    'sharklasers.com', 'getairmail.com', 'dispostable.com',
    'fakeinbox.com', 'throwawaymail.com', 'burnermail.io'
}

def validate_server_email(email_str, user=None):
    """
    Méthode de validation serveur stricte pour les adresses email (inscription et modification).
    - Vérification de la présence et du type.
    - Nettoyage et normalisation (minuscules, sans espaces superflus).
    - Validation du format et de la syntaxe (RFC / Django validator).
    - Contrôle de la structure du domaine et de l'extension (TLD valide).
    - Rejet des domaines d'adresses email temporaires / jetables.
    - Vérification de l'unicité dans la base de données (insensible à la casse).
    """
    if not email_str or not isinstance(email_str, str):
        raise ValidationError("L'adresse email est obligatoire.")

    email_clean = email_str.strip().lower()

    if len(email_clean) > 254:
        raise ValidationError("L'adresse email ne doit pas dépasser 254 caractères.")

    # 1. Validation syntaxique standard Django
    try:
        django_validate_email(email_clean)
    except ValidationError:
        raise ValidationError("Le format de l'adresse email est invalide.")

    # 2. Validation de structure détaillée (domaine et TLD de 2 lettres minimum)
    email_regex = r'^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$'
    if not re.match(email_regex, email_clean):
        raise ValidationError("L'adresse email comporte un nom de domaine ou une extension invalide.")

    # 3. Vérification des domaines d'emails jetables / temporaires
    domain = email_clean.split('@')[-1]
    if domain in DISPOSABLE_EMAIL_DOMAINS:
        raise ValidationError("Les adresses email temporaires ou jetables ne sont pas autorisées.")

    # 4. Vérification de l'unicité en base de données
    User = get_user_model()
    qs = User.objects.filter(email__iexact=email_clean)
    if user and getattr(user, 'pk', None):
        qs = qs.exclude(pk=user.pk)

    if qs.exists():
        raise ValidationError("Cette adresse email est déjà associée à un compte.")

    return email_clean
