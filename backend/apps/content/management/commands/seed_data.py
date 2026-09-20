from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.content.models import Part, Chapter
from apps.glossary.models import PlantFamily, Vegetable, Tool
from apps.pests.models import Disease, Insect
from apps.subscriptions.models import Subscription, SubscriptionPlan
from apps.blog.models import Category as BlogCategory, Post as BlogPost, Comment as BlogComment

User = get_user_model()

class Command(BaseCommand):
    help = 'Alimente la base de données avec des données éducatives complètes pour le Guide du Potager Tropical'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Création des données de test...'))

        # 0. Formules d'Abonnement administrables
        plan_monthly, _ = SubscriptionPlan.objects.get_or_create(
            plan_type='monthly',
            defaults={
                'name': 'Mensuel',
                'price': 2500.00,
                'currency': 'XOF',
                'approx_eur': '~4€',
                'discount_badge': '',
                'duration_days': 30,
                'order': 1,
                'is_active': True
            }
        )
        plan_yearly, _ = SubscriptionPlan.objects.get_or_create(
            plan_type='yearly',
            defaults={
                'name': 'Annuel',
                'price': 20000.00,
                'currency': 'XOF',
                'approx_eur': '~30€',
                'discount_badge': '-30%',
                'duration_days': 365,
                'order': 2,
                'is_active': True
            }
        )

        # 1. Création des Utilisateurs
        user_free, created = User.objects.get_or_create(
            email='demo@potager.fr',
            defaults={'username': 'JardinierDebutant', 'is_staff': False}
        )
        if created:
            user_free.set_password('potager123')
            user_free.save()

        user_premium, created = User.objects.get_or_create(
            email='premium@potager.fr',
            defaults={'username': 'MaîtreJardinier', 'is_staff': False}
        )
        if created:
            user_premium.set_password('potager123')
            user_premium.save()
            user_premium.profile.subscription_active = True
            user_premium.profile.subscription_end_date = timezone.now() + timedelta(days=365)
            user_premium.profile.save()
            Subscription.objects.create(
                user=user_premium,
                plan_type='yearly',
                amount=20000,
                status='active',
                end_date=user_premium.profile.subscription_end_date
            )

        # 2. Création des Parties & Chapitres
        part1, _ = Part.objects.get_or_create(
            order=1,
            defaults={
                'title': 'Partie 1 : Les Fondamentaux du Potager',
                'description': 'Bases essentielles pour concevoir, préparer et réussir son potager biologique.',
                'is_premium': False,
                'icon': 'sprout'
            }
        )

        part2, _ = Part.objects.get_or_create(
            order=2,
            defaults={
                'title': 'Partie 2 : Calendrier de Semis & Gestes Techniques',
                'description': 'Planification des cultures au fil des saisons et techniques de plantation.',
                'is_premium': False,
                'icon': 'calendar-month'
            }
        )

        part3, _ = Part.objects.get_or_create(
            order=3,
            defaults={
                'title': 'Partie 3 : Permaculture & Techniques Avancées',
                'description': 'Associations bénéfiques, mulching, compostage à chaud et rendement élevé.',
                'is_premium': True,
                'icon': 'leaf'
            }
        )

        # Chapitres Partie 1
        Chapter.objects.get_or_create(
            part=part1, order=1,
            defaults={
                'title': '1. Choisir l\'emplacement idéal',
                'is_premium': False,
                'estimated_reading_time': 6,
                'content': (
                    "<h3>Orientation et Ensoleillement</h3>"
                    "<p>Le choix de l'emplacement est décisif. La plupart des légumes ont besoin de <b>6 à 8 heures de soleil direct</b> par jour pour assurer une bonne photosynthèse.</p>"
                    "<ul>"
                    "<li><b>Exposition Sud / Sud-Est :</b> Idéale pour les Solanacées (tomates, poivrons).</li>"
                    "<li><b>Ombre partielle :</b> Convient aux salades, épinards et radis.</li>"
                    "<li><b>Protection contre les vents dominants :</b> Utilisez des haies vivantes ou des brise-vents.</li>"
                    "</ul>"
                    "<h3>Qualité du Sol</h3>"
                    "<p>Un sol équilibré (limono-argileux) retenant l'eau sans créer d'asphyxie racinaire est idéal. En cas de sol lourd, apportez du compost mûr et de la matière organique.</p>"
                )
            }
        )

        Chapter.objects.get_or_create(
            part=part1, order=2,
            defaults={
                'title': '2. Comprendre et Nourrir la Vie du Sol',
                'is_premium': False,
                'estimated_reading_time': 8,
                'content': (
                    "<h3>Le Sol est un Organisme Vivant</h3>"
                    "<p>Un cuillérée à soupe de terre fertile contient plus de micro-organismes que d'êtres humains sur Terre ! Le rôle du jardinier est de nourrir le sol et non la plante directement.</p>"
                    "<h4>Les 3 Piliers de la Fertilité :</h4>"
                    "<ol>"
                    "<li><b>Ne jamais laisser le sol nu :</b> Utiliser un paillage (paille, tontes sèches, feuilles).</li>"
                    "<li><b>Éviter de retourner la terre :</b> Bannir le motoculteur pour préserver les vers de terre et vers anéciques. Privilégier la grelinette.</li>"
                    "<li><b>Apports réguliers :</b> Ajouter du compost mûr à l'automne ou au début du printemps.</li>"
                    "</ol>"
                )
            }
        )

        # Chapitres Partie 2
        Chapter.objects.get_or_create(
            part=part2, order=1,
            defaults={
                'title': '3. Préparation des Planches & Pépinière Tropicale',
                'is_premium': False,
                'estimated_reading_time': 6,
                'content': (
                    "<h3>Confection de la Pépinière Tropicale</h3>"
                    "<p>En climat tropical, la pépinière doit être <b>abritée du soleil ardent et des fortes averses</b> grâce à une ombrière (voile d'ombrage 50%).</p>"
                    "<h4>Règles d'or du semis :</h4>"
                    "<ul>"
                    "<li>Utiliser un substrat drainant : 50% terreau/compost mûr + 50% sable de rivière lavé.</li>"
                    "<li>Semer en lignes espacées de 10 cm pour faciliter l'aération et éviter la fonte des semis.</li>"
                    "<li>Arroser au pulvérisateur ou arrosoir à pomme très fine 2 fois par jour (tôt le matin et en fin d'après-midi).</li>"
                    "</ul>"
                )
            }
        )

        Chapter.objects.get_or_create(
            part=part2, order=2,
            defaults={
                'title': '4. Le Repiquage et la Gestion de l\'Eau en Saison Sèche',
                'is_premium': True,
                'estimated_reading_time': 8,
                'content': (
                    "<h3>Le Moment Idéal pour le Repiquage</h3>"
                    "<p>Repiquez toujours <b>en fin d'après-midi</b> pour éviter le choc thermique lié à la chaleur tropicale diurne.</p>"
                    "<h4>Technique du paillage protecteur :</h4>"
                    "<p>Couvrez immédiatement le sol d'une couche de 5 à 10 cm de paille sèche (herbes coupées, paille de riz). Cela réduit l'évaporation de l'eau de plus de 60% et maintient les racines au frais.</p>"
                )
            }
        )

        # Chapitres Partie 3 (Premium)
        Chapter.objects.get_or_create(
            part=part3, order=1,
            defaults={
                'title': '5. Guildes Végétales & Compagnonnage en Climat Chaud',
                'is_premium': True,
                'estimated_reading_time': 10,
                'content': (
                    "<h3>Principes des Associations Agro-écologiques Tropicales</h3>"
                    "<p>Associer des plantes complémentaires améliore la résistance aux ravageurs tropicaux et optimise l'ombrage naturel.</p>"
                    "<h4>L'Association Tropicale Tripartite :</h4>"
                    "<ul>"
                    "<li><b>Maïs ou Sorgho :</b> Procure un ombrage partiel bienvenu et sert de tuteur vertical.</li>"
                    "<li><b>Niébé (Haricot local) :</b> Fixe l'azote de l'air et enrichit le sol sahélien ou tropical.</li>"
                    "<li><b>Patate douce ou Courge locale :</b> Couvre le sol comme un paillis vivant retenant l'humidité.</li>"
                    "</ul>"
                )
            }
        )

        # 3. Création des Familles Botaniques Tropicales
        f_solanaceae, _ = PlantFamily.objects.get_or_create(
            name='Solanacées Tropicales',
            defaults={
                'description': 'Famille pilier des potagers tropicaux (tomates adaptées, piments forts, aubergines locales).',
                'characteristics': 'Exigeante en compost et en arrosage régulier. Sensible au flétrissement bactérien et aux viroses transmises par les aleurodes.',
                'is_premium': False
            }
        )

        f_malvaceae, _ = PlantFamily.objects.get_or_create(
            name='Malvacées Tropicales',
            defaults={
                'description': 'Famille reine des tropiques comprenant le Gombo (Okra) et le Bissap (Oseille de Guinée).',
                'characteristics': 'Remarquable résistance à la chaleur et à la sécheresse. Croissance rapide et grande rusticité.',
                'is_premium': False
            }
        )

        f_cucurbitaceae, _ = PlantFamily.objects.get_or_create(
            name='Cucurbitacées Tropicales',
            defaults={
                'description': 'Légumes fruits rampants ou grimpants (concombre tropical, courge locale, melon).',
                'characteristics': 'Plantes gourmandes en eau et en fumure organique bien décomposée. Sensibles aux mouches des fruits.',
                'is_premium': False
            }
        )

        f_fabaceae, _ = PlantFamily.objects.get_or_create(
            name='Fabacées (Légumineuses & Niébé)',
            defaults={
                'description': 'Légumineuses fixatrices d\'azote (Niébé / Vigna unguiculata, arachide, haricot kilomètre).',
                'characteristics': 'Enrichissent naturellement les sols tropicaux pauvres. Parfaites en engrais vert ou rotation.',
                'is_premium': False
            }
        )

        # 4. Légumes Tropicaux Emblématiques
        v_gombo, _ = Vegetable.objects.get_or_create(
            name='Gombo (Okra)',
            defaults={
                'family': f_malvaceae,
                'scientific_name': 'Abelmoschus esculentus',
                'sowing_period': 'Toute l\'année avec irrigation, idéalement de Mai à Août (Hivernage)',
                'harvest_period': '60 jours après semis, récolte tous les 2-3 jours',
                'care_tips': 'Semer en poquets de 3 graines espacés de 50 cm. Butter légèrement les tiges. Récolter jeune pour éviter la fibrosité.',
                'tropical_season': 'toute_annee',
                'heat_tolerance': 'haute',
                'water_requirement': 'modere',
                'sun_exposure': 'plein_soleil',
                'tropical_varieties': 'Clemson Spineless, Kirene, Indiana, Sabal F1',
                'cycle_duration_days': 65,
                'is_premium': False
            }
        )

        v_piment, _ = Vegetable.objects.get_or_create(
            name='Piment Habanero / Antillais',
            defaults={
                'family': f_solanaceae,
                'scientific_name': 'Capsicum chinense',
                'sowing_period': 'Octobre à Février (Pépinière puis repiquage)',
                'harvest_period': '90 à 120 jours après repiquage, production continue sur 8-12 mois',
                'care_tips': 'Exige un sol chaud et très bien drainé. Pailler pour limiter les nématodes. Arrosage régulier sans excès.',
                'tropical_season': 'toute_annee',
                'heat_tolerance': 'haute',
                'water_requirement': 'modere',
                'sun_exposure': 'plein_soleil',
                'tropical_varieties': 'Scotch Bonnet, Big Sun, Piment de Cayenne, Bresse',
                'cycle_duration_days': 110,
                'is_premium': False
            }
        )

        v_tomate, _ = Vegetable.objects.get_or_create(
            name='Tomate Tropicale',
            defaults={
                'family': f_solanaceae,
                'scientific_name': 'Solanum lycopersicum',
                'sowing_period': 'Octobre - Janvier (Saison sèche fraîche)',
                'harvest_period': 'Janvier - Avril',
                'care_tips': 'Privilégier impérativement des variétés hybrides tropicalisées résistantes au TYLCV et au flétrissement bactérien. Tuteurer fermement.',
                'tropical_season': 'saison_seche_fraiche',
                'heat_tolerance': 'moyenne',
                'water_requirement': 'eleve',
                'sun_exposure': 'plein_soleil',
                'tropical_varieties': 'Mongal F1, Nadira F1, Cobra F1, Jagala F1',
                'cycle_duration_days': 85,
                'is_premium': False
            }
        )

        v_patate, _ = Vegetable.objects.get_or_create(
            name='Patate Douce',
            defaults={
                'family': f_cucurbitaceae,
                'scientific_name': 'Ipomoea batatas',
                'sowing_period': 'Juin à Septembre (Boutures en saison des pluies ou toute l\'année en billons irrigués)',
                'harvest_period': '90 à 120 jours après bouturage',
                'care_tips': 'Planter les boutures de tiges sur des billons surélevés pour faciliter le développement des tubercules.',
                'tropical_season': 'toute_annee',
                'heat_tolerance': 'haute',
                'water_requirement': 'modere',
                'sun_exposure': 'plein_soleil',
                'tropical_varieties': 'Beauregard (chair orange), Boniato (chair blanche), TIB-4',
                'cycle_duration_days': 110,
                'is_premium': True
            }
        )

        # 5. Outils Adaptés au Maraîchage Tropical
        Tool.objects.get_or_create(
            name='Daba (Houe sahélienne)',
            defaults={
                'category': 'travail_du_sol',
                'description': 'Outil traditionnel d\'Afrique de l\'Ouest à manche court et fer large recourbé, parfait pour travailler la terre avec précision.',
                'usage_tips': 'Idéale pour confectionner les planches surélevées et les billons de drainage avant les pluies d\'hivernage.',
                'tropical_tips': 'Permet de biner efficacement les sols sablo-limoneux sans détruire la micro-structure sous-jacente.',
                'is_premium': False
            }
        )

        Tool.objects.get_or_create(
            name='Ombrière Maraîchère (Filet d\'ombrage 50%)',
            defaults={
                'category': 'protection',
                'description': 'Structure légère en bois ou bambou recouverte d\'une toile d\'ombrage 30% à 50% filtrant le soleil zénithal tropical.',
                'usage_tips': 'Indispensable pour protéger les jeunes pépinières et cultures sensibles (salades, jeunes tomates) des brûlures foliaires.',
                'tropical_tips': 'Permet de baisser la température du sol de 4 à 6°C et de réduire l\'évapo-transpiration de moitié.',
                'is_premium': False
            }
        )

        Tool.objects.get_or_create(
            name='Arrosoir Maraîcher à Pomme Fine',
            defaults={
                'category': 'entretien_arrosage',
                'description': 'Arrosoir grande capacité (10-12L) avec pomme micro-perforée assurant une pluie très douce.',
                'usage_tips': 'Évite de déterrer les fines graines et de tasser la surface des planches de semis.',
                'tropical_tips': 'Arroser de préférence avant 8h le matin ou après 17h pour maximiser l\'infiltration dans le sol.',
                'is_premium': False
            }
        )

        Tool.objects.get_or_create(
            name='Filet Anti-Insectes 50 Mesh',
            defaults={
                'category': 'protection',
                'description': 'Filet barrière physique empêchant l\'accès aux micro-ravageurs (aleurodes, altises, mouches mineuses).',
                'usage_tips': 'Poser sur arceaux au-dessus des planches dès le repiquage pour une protection 100% sans pesticides.',
                'tropical_tips': 'Bloque les mouches blanches (Bemisia tabaci) responsables de la redoutable virose TYLCV de la tomate.',
                'is_premium': True
            }
        )

        # 6. Maladies Tropicales
        d_bacterien, _ = Disease.objects.get_or_create(
            name='Flétrissement Bactérien Tropical',
            defaults={
                'symptoms': 'Flétrissement brutal de la plante en pleine végétation, les feuilles restant vertes. Moelle de la tige brunie.',
                'treatment': 'Arracher et brûler immédiatement les plants atteints (bactérie Ralstonia solanacearum dans le sol).',
                'prevention': 'Pratiquer des rotations longues sans Solanacées (au moins 3 ans). Utiliser des variétés résistantes (Mongal F1).',
                'favorable_season': 'Saison des pluies et températures élevées (> 30°C)',
                'tropical_organic_treatment': 'Épandage de chaux agricole ou cendre pour neutraliser l\'acidité, rotation avec maïs ou sorgho.',
                'is_premium': True
            }
        )
        d_bacterien.affected_vegetables.add(v_tomate, v_piment)

        d_tylcv, _ = Disease.objects.get_or_create(
            name='Virose TYLCV (Feuilles Jaunes Cuillères)',
            defaults={
                'symptoms': 'Nanisme du plant, feuilles déformées enroulées en cuillère vers le haut, jaunissement interveinaire, arrêt de fructification.',
                'treatment': 'Aucun traitement curatif contre le virus. Lutter impérativement contre le vecteur (la mouche blanche).',
                'prevention': 'Protection physique sous filet anti-insectes 50 mesh dès la pépinière. Choix de semences hybrides tolérantes.',
                'favorable_season': 'Saison sèche chaude (pullulation maximale des aleurodes)',
                'tropical_organic_treatment': 'Pulvérisation hebdomadaire d\'huile de neem pressée à froid (5 ml/L + savon noir comme émulsifiant).',
                'is_premium': True
            }
        )
        d_tylcv.affected_vegetables.add(v_tomate)

        # 7. Insectes Nuisibles Tropicaux
        ins_mouche, _ = Insect.objects.get_or_create(
            name='Mouche Blanche / Aleurode (Bemisia tabaci)',
            defaults={
                'description': 'Minuscules insectes blancs ailés (1 mm) s\'envolant en nuée quand on secoue les feuilles.',
                'damage': 'Affaiblissement par succion de sève et transmission des pires viroses tropicales (TYLCV, mosaïque).',
                'solution': 'Pièges collants jaunes pour capture massive. Pulvérisation de solution de neem ou macération de piment-ail.',
                'favorable_season': 'Saison sèche chaude (harmattan)',
                'tropical_bio_control': 'Macération de 100g de piment fort + 100g d\'ail écrasé dans 1L d\'eau pendant 24h, dilué à 10% avec du savon noir.',
                'prevention_tips': 'Paillage réfléchissant, bandes de maïs brise-vent autour des parcelles, filets protecteurs.',
                'is_premium': True
            }
        )
        ins_mouche.affected_vegetables.add(v_tomate, v_gombo, v_piment)

        ins_chenille, _ = Insect.objects.get_or_create(
            name='Chenille Défoliatrice & Ver de la Tomate',
            defaults={
                'description': 'Chenilles voraces (Helicoverpa armigera / Spodoptera) perforant les fruits et dévorant les feuilles tendres.',
                'damage': 'Trous profonds dans les fruits provoquant leur pourriture rapide avant maturation.',
                'solution': 'Ramassage manuel à la tombée de la nuit. Traitement bio au Bacillus thuringiensis (Bt) ou décoction de feuilles de neem.',
                'favorable_season': 'Saison des pluies et début de saison sèche',
                'tropical_bio_control': 'Décoction de 500g de graines de neem séchées et broyées dans 10L d\'eau. Répulsif et perturbateur de croissance.',
                'prevention_tips': 'Planter des tagètes (œillets d\'Inde) et du basilic en bordure des planches pour troubler l\'odorat des papillons.',
                'is_premium': True
            }
        )
        ins_chenille.affected_vegetables.add(v_tomate, v_gombo)

        # 8. Blog & Articles d'Actualité
        cat_conseils, _ = BlogCategory.objects.get_or_create(
            name='Calendrier & Saisons Tropicales',
            defaults={'description': 'Guides pratiques pour optimiser son potager en saison sèche et en hivernage.'}
        )

        cat_perma, _ = BlogCategory.objects.get_or_create(
            name='Agro-écologie Tropicale',
            defaults={'description': 'Techniques de sol vivant sahélien, purin de neem, compostage tropical et paillage.'}
        )

        post1, _ = BlogPost.objects.get_or_create(
            title='Comment Réussir son Potager en Pleine Saison Sèche et Chaude',
            defaults={
                'author': user_premium,
                'category': cat_conseils,
                'excerpt': 'Protéger ses cultures maraîchères contre la chaleur accablante, le vent sec et le manque d\'eau.',
                'content': (
                    "<h2>Les Clés du Maraîchage en Saison Sèche Chaude</h2>"
                    "<p>Entre mars et juin, les températures dépassent souvent les 40°C sous les tropiques. Pour continuer à récolter, quelques règles sont indispensables :</p>"
                    "<h3>1. L'ombrière ou filet d'ombrage</h3>"
                    "<p>Installer une ombrière filtrant 30% à 50% du rayonnement solaire direct pour réduire le stress thermique des solanacées.</p>"
                    "<h3>2. Le goutte-à-goutte et paillage épais</h3>"
                    "<p>Arroser tôt le matin ou après le coucher du soleil et recouvrir le sol de 10 cm de paillis pour éviter la vaporisation instantanée.</p>"
                    "<h3>3. Privilégier les espèces adaptées</h3>"
                    "<p>Miser sur le gombo, la patate douce, le bissap ou les variétés tropicalisées résistantes aux nématodes.</p>"
                ),
                'is_published': True,
                'views_count': 142
            }
        )

        post2, _ = BlogPost.objects.get_or_create(
            title='Le Paillage Écologique : Pourquoi et Comment Pailler son Potager ?',
            defaults={
                'author': user_premium,
                'category': cat_perma,
                'excerpt': 'Économisez jusqu\'à 70% d\'eau d\'arrosage et protégez la microfaune de votre sol grâce au paillage organique.',
                'content': (
                    "<h2>Les Avantages Incomparables du Paillage</h2>"
                    "<p>Le sol nu est une anomalie dans la nature. En recouvrant vos planches de culture d'une couche de paille ou de feuilles mortes, vous créez un véritable bouclier thermique.</p>"
                    "<ul>"
                    "<li><b>Conservation de l'humidité :</b> Réduction drastique de l'évaporation d'eau.</li>"
                    "<li><b>Désherbage naturel :</b> Blocage de la germination des adventices indésirables.</li>"
                    "<li><b>Nourriture du sol :</b> Décomposition lente apportant de la matière organique aux vers de terre.</li>"
                    "</ul>"
                ),
                'is_premium': True,
                'is_published': True,
                'views_count': 98
            }
        )

        BlogComment.objects.get_or_create(
            post=post1, author=user_free,
            defaults={'content': 'Merci pour ces excellents conseils ! Mes semis de tomates ont très bien démarré.'}
        )

        self.stdout.write(self.style.SUCCESS('Base de données alimentée avec succès pour le Guide du Potager Tropical !'))
