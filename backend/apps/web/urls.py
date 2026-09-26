from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    # Accueil & Guide numérique
    path('', views.home_view, name='home'),
    path('guide/chapitre/<int:chapter_id>/', views.chapter_detail_view, name='chapter_detail'),

    # Fiches Légumes & Variétés
    path('legumes/', views.vegetables_list_view, name='vegetables_list'),
    path('legumes/<int:vegetable_id>/', views.vegetable_detail_view, name='vegetable_detail'),

    # Simulateur Calendrier Cultural
    path('calendrier/', views.calendar_view, name='calendar'),

    # Familles Botaniques
    path('familles/', views.families_list_view, name='families_list'),

    # Outils Maraîchers
    path('outils/', views.tools_list_view, name='tools_list'),
    path('outils/<int:tool_id>/', views.tool_detail_view, name='tool_detail'),

    # Maladies & Soins
    path('maladies/', views.diseases_list_view, name='diseases_list'),
    path('maladies/<int:disease_id>/', views.disease_detail_view, name='disease_detail'),

    # Insectes Nuisibles & Biocontrôle
    path('insectes/', views.insects_list_view, name='insects_list'),
    path('insectes/<int:insect_id>/', views.insect_detail_view, name='insect_detail'),

    # Blog & Actualités
    path('blog/', views.blog_list_view, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail_view, name='blog_detail'),

    # Formules d'Abonnement & Paiement Chariow
    path('abonnement/', views.subscription_view, name='subscription'),
    path('abonnement/checkout/<str:plan_type>/', views.checkout_view, name='checkout'),

    # Authentification & Profil
    path('connexion/', views.login_view, name='login'),
    path('inscription/', views.register_view, name='register'),
    path('deconnexion/', views.logout_view, name='logout'),
    path('profil/', views.profile_view, name='profile'),

    # À Propos & Contact
    path('a-propos/', views.about_view, name='about'),
]
