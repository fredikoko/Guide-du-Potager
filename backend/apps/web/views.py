from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime

from apps.content.models import Part, Chapter, AboutPage
from apps.glossary.models import Vegetable, PlantFamily, Tool, CalendarEntry, TOOL_CATEGORIES, TROPICAL_SEASON_CHOICES
from apps.pests.models import Disease, Insect
from apps.blog.models import Post, Category, Comment
from apps.subscriptions.models import SubscriptionPlan, Subscription
from apps.subscriptions.chariow_service import ChariowService
from apps.accounts.models import UserProfile

from .forms import WebLoginForm, WebRegisterForm, UserProfileUpdateForm, BlogCommentForm

User = get_user_model()

def user_has_premium_access(request):
    """Vérifie si l'utilisateur courant possède un abonnement Premium actif."""
    if not request.user.is_authenticated:
        return False
    try:
        return bool(request.user.profile.is_premium)
    except Exception:
        return False

# ==============================================================================
# ACCUEIL & GUIDE EBOOK (CHAPITRES)
# ==============================================================================

def home_view(request):
    """Page d'accueil responsive & Sommaire interactif du Guide du Potager."""
    parts = Part.objects.prefetch_related('chapters').all()
    recent_posts = Post.objects.filter(is_published=True).select_related('category')[:3]
    featured_tools = Tool.objects.all()[:3]
    vegetables_count = Vegetable.objects.count()
    calendar_count = CalendarEntry.objects.count()
    
    context = {
        'parts': parts,
        'recent_posts': recent_posts,
        'featured_tools': featured_tools,
        'vegetables_count': vegetables_count,
        'calendar_count': calendar_count,
        'active_tab': 'home',
    }
    return render(request, 'web/home.html', context)

def chapter_detail_view(request, chapter_id):
    """Lecture d'un chapitre avec navigation précédente / suivante et paywall."""
    chapter = get_object_or_404(Chapter.objects.select_related('part'), id=chapter_id)
    is_premium_user = user_has_premium_access(request)
    
    # Navigation : Chapitre précédent et suivant
    prev_chapter = Chapter.objects.filter(
        Q(part=chapter.part, order__lt=chapter.order) | Q(part__order__lt=chapter.part.order)
    ).order_by('-part__order', '-order').first()

    next_chapter = Chapter.objects.filter(
        Q(part=chapter.part, order__gt=chapter.order) | Q(part__order__gt=chapter.part.order)
    ).order_by('part__order', 'order').first()

    is_locked = chapter.is_premium and not is_premium_user

    context = {
        'chapter': chapter,
        'is_locked': is_locked,
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter,
        'active_tab': 'guide',
    }
    return render(request, 'web/chapter_detail.html', context)

# ==============================================================================
# FICHES LÉGUMES & VARIÉTÉS TROPICALES
# ==============================================================================

def vegetables_list_view(request):
    """Catalogue des légumes tropicaux avec recherche et filtrage par saison ou famille."""
    query = request.GET.get('q', '').strip()
    season = request.GET.get('season', '').strip()
    family_id = request.GET.get('family', '').strip()

    vegetables = Vegetable.objects.select_related('family').all()

    if query:
        vegetables = vegetables.filter(
            Q(name__icontains=query) |
            Q(scientific_name__icontains=query) |
            Q(tropical_varieties__icontains=query)
        )
    if season:
        vegetables = vegetables.filter(tropical_season=season)
    if family_id:
        vegetables = vegetables.filter(family_id=family_id)

    families = PlantFamily.objects.all()

    context = {
        'vegetables': vegetables,
        'families': families,
        'query': query,
        'selected_season': season,
        'selected_family': family_id,
        'seasons': TROPICAL_SEASON_CHOICES,
        'active_tab': 'vegetables',
    }
    return render(request, 'web/vegetables_list.html', context)

def vegetable_detail_view(request, vegetable_id):
    """Fiche technique complète d'un légume (saisons, eau, chaleur, semis, récoltes)."""
    vegetable = get_object_or_404(Vegetable.objects.select_related('family'), id=vegetable_id)
    calendar_entries = vegetable.calendar_entries.filter(is_active=True).order_by('month')
    related_diseases = vegetable.diseases.all()
    related_insects = vegetable.insects.all()

    context = {
        'vegetable': vegetable,
        'calendar_entries': calendar_entries,
        'related_diseases': related_diseases,
        'related_insects': related_insects,
        'active_tab': 'vegetables',
    }
    return render(request, 'web/vegetable_detail.html', context)

# ==============================================================================
# SIMULATEUR CALENDRIER CULTURAL TROPICAL
# ==============================================================================

def calendar_view(request):
    """Simulateur mensuel interactif des semis et récoltes maraîchères."""
    current_month = timezone.now().month
    selected_month = int(request.GET.get('month', current_month))
    if not (1 <= selected_month <= 12):
        selected_month = current_month

    action_filter = request.GET.get('action', '').strip()  # 'semis', 'recolte' ou tous

    entries = CalendarEntry.objects.filter(month=selected_month, is_active=True).select_related('vegetable', 'vegetable__family')

    if action_filter in ['semis', 'recolte']:
        entries = entries.filter(action=action_filter)

    months_list = [
        (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
        (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
        (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre')
    ]

    context = {
        'months': months_list,
        'selected_month': selected_month,
        'selected_month_name': dict(months_list).get(selected_month, ''),
        'action_filter': action_filter,
        'entries': entries,
        'active_tab': 'calendar',
    }
    return render(request, 'web/calendar.html', context)

# ==============================================================================
# FAMILLES BOTANIQUES
# ==============================================================================

def families_list_view(request):
    """Liste des familles botaniques, caractéristiques et rotations des cultures."""
    families = PlantFamily.objects.prefetch_related('vegetables').all()
    context = {
        'families': families,
        'active_tab': 'families',
    }
    return render(request, 'web/families_list.html', context)

# ==============================================================================
# OUTILS MARAÎCHERS DE PRÉCISION
# ==============================================================================

def tools_list_view(request):
    """Catalogue des outils avec filtrage par catégorie et badges vert clair #47C26B."""
    category = request.GET.get('cat', '').strip()
    tools = Tool.objects.all()

    if category:
        tools = tools.filter(category=category)

    context = {
        'tools': tools,
        'categories': TOOL_CATEGORIES,
        'selected_category': category,
        'active_tab': 'tools',
    }
    return render(request, 'web/tools_list.html', context)

def tool_detail_view(request, tool_id):
    """Détail d'un outil maraîcher. Paywall si premium et utilisateur non-abonné."""
    tool = get_object_or_404(Tool, id=tool_id)
    is_premium_user = user_has_premium_access(request)
    is_locked = tool.is_premium and not is_premium_user

    context = {
        'tool': tool,
        'is_locked': is_locked,
        'active_tab': 'tools',
    }
    return render(request, 'web/tool_detail.html', context)

# ==============================================================================
# MALADIES DES PLANTES & SOINS BIO
# ==============================================================================

def diseases_list_view(request):
    """Maladies cryptogamiques & bactériennes avec badges vert clair #47C26B."""
    diseases = Disease.objects.prefetch_related('affected_vegetables').all()
    context = {
        'diseases': diseases,
        'active_tab': 'diseases',
    }
    return render(request, 'web/diseases_list.html', context)

def disease_detail_view(request, disease_id):
    """Détail des symptômes et recettes bio. Paywall si premium et non-abonné."""
    disease = get_object_or_404(Disease.objects.prefetch_related('affected_vegetables'), id=disease_id)
    is_premium_user = user_has_premium_access(request)
    is_locked = disease.is_premium and not is_premium_user

    context = {
        'disease': disease,
        'is_locked': is_locked,
        'active_tab': 'diseases',
    }
    return render(request, 'web/disease_detail.html', context)

# ==============================================================================
# INSECTES RAVAGEURS & BIOCONTRÔLE
# ==============================================================================

def insects_list_view(request):
    """Insectes ravageurs & auxiliaires avec badges vert clair #47C26B."""
    insects = Insect.objects.prefetch_related('affected_vegetables').all()
    context = {
        'insects': insects,
        'active_tab': 'insects',
    }
    return render(request, 'web/insects_list.html', context)

def insect_detail_view(request, insect_id):
    """Détail des dégâts et biocontrôle. Paywall si premium et non-abonné."""
    insect = get_object_or_404(Insect.objects.prefetch_related('affected_vegetables'), id=insect_id)
    is_premium_user = user_has_premium_access(request)
    is_locked = insect.is_premium and not is_premium_user

    context = {
        'insect': insect,
        'is_locked': is_locked,
        'active_tab': 'insects',
    }
    return render(request, 'web/insect_detail.html', context)

# ==============================================================================
# BLOG & ACTUALITÉS MARAÎCHÈRES
# ==============================================================================

def blog_list_view(request):
    """Articles, fiches pratiques et retours d'expérience avec filtres."""
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()

    posts = Post.objects.filter(is_published=True).select_related('category', 'author')

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query)
        )
    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    categories = Category.objects.all()

    context = {
        'posts': posts,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
        'active_tab': 'blog',
    }
    return render(request, 'web/blog_list.html', context)

def blog_detail_view(request, slug):
    """Article de blog avec commentaires et incrémentation des vues."""
    post = get_object_or_404(Post.objects.select_related('category', 'author'), slug=slug, is_published=True)
    
    # Incrémentation des vues
    Post.objects.filter(id=post.id).update(views_count=post.views_count + 1)
    post.views_count += 1

    is_premium_user = user_has_premium_access(request)
    is_locked = post.is_premium and not is_premium_user

    comments = post.comments.filter(is_approved=True).select_related('author').order_by('-created_at')
    comment_form = BlogCommentForm()

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = BlogCommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
            messages.success(request, "Votre commentaire a été publié avec succès !")
            return redirect('web:blog_detail', slug=slug)

    recent_posts = Post.objects.filter(is_published=True).exclude(id=post.id)[:3]

    context = {
        'post': post,
        'is_locked': is_locked,
        'comments': comments,
        'comment_form': comment_form,
        'recent_posts': recent_posts,
        'active_tab': 'blog',
    }
    return render(request, 'web/blog_detail.html', context)

# ==============================================================================
# FORMULES D'ABONNEMENT & PAIEMENT CHARIOW
# ==============================================================================

def subscription_view(request):
    """Présentation des formules (Pass 1 Mois, Pass Saison 3 Mois, Pass Annuel)."""
    # Si la table est vide, assurer l'initialisation automatique
    if not SubscriptionPlan.objects.exists():
        SubscriptionPlan.objects.create(
            plan_type='monthly', name='Pass 1 Mois', description='Découverte sans engagement',
            price=2500.00, currency='XOF', approx_eur='~4€', discount_badge='', duration_days=30, order=1
        )
        SubscriptionPlan.objects.create(
            plan_type='seasonal', name='Pass Saison (3 Mois)', description='1 cycle complet de culture maraîchère',
            price=5000.00, currency='XOF', approx_eur='~8€', discount_badge='⭐ Recommandé', duration_days=90, is_featured=True, order=2
        )
        SubscriptionPlan.objects.create(
            plan_type='yearly', name='Pass Annuel', description='Accès illimité toute l\'année',
            price=15000.00, currency='XOF', approx_eur='~23€', discount_badge='-50%', duration_days=365, order=3
        )

    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('order', 'price')
    context = {
        'plans': plans,
        'active_tab': 'subscription',
    }
    return render(request, 'web/subscription.html', context)

@login_required(login_url='web:login')
def checkout_view(request, plan_type):
    """Initie la session de paiement Chariow et redirige l'utilisateur."""
    plan = get_object_or_404(SubscriptionPlan, plan_type=plan_type, is_active=True)
    redirect_url = request.build_absolute_uri('/profil/')
    customer_ip = request.META.get('REMOTE_ADDR')

    result = ChariowService.create_checkout_session(
        user=request.user,
        plan_type=plan_type,
        redirect_url=redirect_url,
        customer_ip=customer_ip
    )

    if result.get('success') and result.get('payment_url'):
        return redirect(result['payment_url'])
    else:
        err_msg = result.get('error') or "Impossible d'initier le paiement en ligne. Veuillez réessayer."
        messages.error(request, f"Erreur de paiement : {err_msg}")
        return redirect('web:subscription')

# ==============================================================================
# AUTHENTIFICATION & PROFIL UTILISATEUR
# ==============================================================================

def login_view(request):
    """Connexion d'un utilisateur par email ou nom d'utilisateur."""
    if request.user.is_authenticated:
        return redirect('web:home')

    next_url = request.GET.get('next') or 'web:home'
    form = WebLoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        login_val = form.cleaned_data['login'].strip()
        pwd = form.cleaned_data['password']

        target_email = login_val
        if '@' not in login_val:
            u_obj = User.objects.filter(username__iexact=login_val).first()
            if u_obj:
                target_email = u_obj.email

        user = authenticate(request, username=target_email, password=pwd)
        if user is None:
            user = authenticate(request, email=target_email, password=pwd)

        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} !")
            return redirect(next_url)
        else:
            messages.error(request, "Email / nom d'utilisateur ou mot de passe incorrect.")

    context = {
        'form': form,
        'active_tab': 'login',
    }
    return render(request, 'web/login.html', context)

def register_view(request):
    """Inscription maraîchère avec choix de zone climatique et type de potager."""
    if request.user.is_authenticated:
        return redirect('web:home')

    form = WebRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        # Profil utilisateur créé via signal, mise à jour des préférences
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.climate_zone = form.cleaned_data['climate_zone']
        profile.garden_type = form.cleaned_data['garden_type']
        profile.country = form.cleaned_data.get('country') or "Sénégal"
        profile.save()

        # Connexion automatique
        login(request, user)
        messages.success(request, "Votre compte maraîcher a été créé avec succès !")
        return redirect('web:home')

    context = {
        'form': form,
        'active_tab': 'register',
    }
    return render(request, 'web/register.html', context)

def logout_view(request):
    """Déconnexion de l'utilisateur."""
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('web:home')

@login_required(login_url='web:login')
def profile_view(request):
    """Tableau de bord du profil maraîcher et gestion des paramètres."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            u = request.user
            u.username = form.cleaned_data['username']
            u.save()
            form.save()
            messages.success(request, "Votre profil maraîcher a été mis à jour.")
            return redirect('web:profile')
    else:
        form = UserProfileUpdateForm(instance=profile, initial={'username': request.user.username})

    active_sub = Subscription.objects.filter(user=request.user, status='active').order_by('-end_date').first()

    context = {
        'form': form,
        'profile': profile,
        'active_sub': active_sub,
        'active_tab': 'profile',
    }
    return render(request, 'web/profile.html', context)

# ==============================================================================
# À PROPOS & MISSION
# ==============================================================================

def about_view(request):
    """Présentation du Guide du Potager Tropical, mission agro-écologique & contact."""
    about = AboutPage.get_solo()
    context = {
        'about': about,
        'active_tab': 'about',
    }
    return render(request, 'web/about.html', context)
