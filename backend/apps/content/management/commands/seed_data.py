from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.content.models import Part, Chapter
from apps.glossary.models import PlantFamily, Vegetable, Tool
from apps.pests.models import Disease, Insect
from apps.subscriptions.models import Subscription

User = get_user_model()

class Command(BaseCommand):
    help = 'Alimente la base de données avec des données éducatives complètes pour le Guide du Potager'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Création des données de test...'))

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
                'title': '3. Réussir ses Semis en Pépinière et sous Châssis',
                'is_premium': False,
                'estimated_reading_time': 10,
                'content': (
                    "<h3>Matériel nécessaire pour les semis</h3>"
                    "<p>Pour démarrer vos semis au sortir de l'hiver, préparez un terreau spécial semis, des plaques alvéolées ou godets réutilisables, et maintenez une température entre 18°C et 22°C.</p>"
                    "<h4>Étapes clés :</h4>"
                    "<ul>"
                    "<li>Remplir les godets sans trop tasser.</li>"
                    "<li>Déposer 2 à 3 graines par godet.</li>"
                    "<li>Recouvrir d'une fine couche de terreau (profondeur égale à 2 fois la taille de la graine).</li>"
                    "<li>Arroser en pluie fine avec un pulvérisateur.</li>"
                    "</ul>"
                )
            }
        )

        Chapter.objects.get_or_create(
            part=part2, order=2,
            defaults={
                'title': '4. Le Repiquage et la Plantation en Pleine Terre',
                'is_premium': True,
                'estimated_reading_time': 7,
                'content': (
                    "<h3>Moment opportun</h3>"
                    "<p>En région tempérée, attendez le passage des <b>Saints de Glace (mi-mai)</b> pour planter les légumes frileux (tomates, aubergines, courgettes).</p>"
                    "<h4>Technique d'enfoncement de la tige :</h4>"
                    "<p>Pour les tomates, enterrez la tige jusqu'aux premières feuilles pour stimuler l'apparition de nouvelles racines adventives vigoureuses.</p>"
                )
            }
        )

        # Chapitres Partie 3 (Premium)
        Chapter.objects.get_or_create(
            part=part3, order=1,
            defaults={
                'title': '5. Guildes Végétales & Compagnonnage Avancé',
                'is_premium': True,
                'estimated_reading_time': 12,
                'content': (
                    "<h3>Principes des Associations Synergiques</h3>"
                    "<p>La combinaison stratégique des plantes améliore la santé du potager et réduit naturellement l'attaque des ravageurs.</p>"
                    "<h4>La Guilde des 3 Sœurs (Milpa Aztec) :</h4>"
                    "<ul>"
                    "<li><b>Maïs :</b> Sert de tuteur naturel pour les haricots grimpants.</li>"
                    "<li><b>Haricot à rames :</b> Fixe l'azote atmosphérique dans le sol.</li>"
                    "<li><b>Courge :</b> Ses larges feuilles recouvrent le sol et conservent l'humidité.</li>"
                    "</ul>"
                )
            }
        )

        # 3. Création des Familles de Légumes & Légumes
        f_solanaceae, _ = PlantFamily.objects.get_or_create(
            name='Solanacées',
            defaults={
                'description': 'Famille exigeante en chaleur et en nutriments (tomates, piments, aubergines).',
                'characteristics': 'Plantes exigeantes, sensibilité aux maladies cryptogamiques (mildiou). Ne pas cultiver 2 ans de suite au même endroit.',
                'is_premium': False
            }
        )

        f_cucurbitaceae, _ = PlantFamily.objects.get_or_create(
            name='Cucurbitacées',
            defaults={
                'description': 'Légumes fruits rampants ou grimpants à grandes feuilles (courgettes, potirons, concombres).',
                'characteristics': 'Fort besoin en eau et compost mûr. Sensibles au mildiou et à l\'oïdium.',
                'is_premium': False
            }
        )

        f_fabaceae, _ = PlantFamily.objects.get_or_create(
            name='Fabacées (Légumineuses)',
            defaults={
                'description': 'Plantes capables de fixer l\'azote atmosphérique dans le sol (pois, haricots, fèves).',
                'characteristics': 'Enrichissent le sol en azote. Parfaites en rotation avant des légumes exigeants.',
                'is_premium': False
            }
        )

        f_brassicaceae, _ = PlantFamily.objects.get_or_create(
            name='Brassicacées (Crucifères)',
            defaults={
                'description': 'Famille des choux, radis, navets et roquette.',
                'characteristics': 'Riches en vitamines et minéraux, sensibles aux altises.',
                'is_premium': True
            }
        )

        # Légumes
        v_tomate, _ = Vegetable.objects.get_or_create(
            name='Tomate',
            defaults={
                'family': f_solanaceae,
                'scientific_name': 'Solanum lycopersicum',
                'sowing_period': 'Février - Mars (sous abri à 20°C)',
                'harvest_period': 'Juillet - Octobre',
                'care_tips': 'Pailler abondamment. Supprimer les gourmands si nécessaire. Arroser au pied sans mouiller le feuillage.',
                'is_premium': False
            }
        )

        v_courgette, _ = Vegetable.objects.get_or_create(
            name='Courgette',
            defaults={
                'family': f_cucurbitaceae,
                'scientific_name': 'Cucurbita pepo',
                'sowing_period': 'Avril (godet) - Mai (pleine terre)',
                'harvest_period': 'Juin - Septembre',
                'care_tips': 'Récolter régulièrement les jeunes fruits pour stimuler la floraison continuelle.',
                'is_premium': False
            }
        )

        v_haricot, _ = Vegetable.objects.get_or_create(
            name='Haricot Vert',
            defaults={
                'family': f_fabaceae,
                'scientific_name': 'Phaseolus vulgaris',
                'sowing_period': 'Mai - Juillet (sol chaud > 15°C)',
                'harvest_period': 'Juillet - Octobre',
                'care_tips': 'Butter les pieds lorsque la plante atteint 15 cm de hauteur.',
                'is_premium': False
            }
        )

        v_chou, _ = Vegetable.objects.get_or_create(
            name='Chou Cabus',
            defaults={
                'family': f_brassicaceae,
                'scientific_name': 'Brassica oleracea var. capitata',
                'sowing_period': 'Mars - Juin',
                'harvest_period': 'Août - Décembre',
                'care_tips': 'Utiliser un filet anti-insectes contre la piéride et les altises.',
                'is_premium': True
            }
        )

        # 4. Outils de Maraîchage
        Tool.objects.get_or_create(
            name='Grelinette (Aéro-bêche)',
            defaults={
                'category': 'travail_du_sol',
                'description': 'Outil écologique à deux manches à dents verticales permettant d\'aérer le sol sans le retourner.',
                'usage_tips': 'Enfoncer les dents verticalement, tirer légèrement vers soi sans soulever la terre pour préserver la faune du sol.',
                'is_premium': False
            }
        )

        Tool.objects.get_or_create(
            name='Transplantoir',
            defaults={
                'category': 'semis_plantation',
                'description': 'Petite pelle à main courbe essentielle pour planter les minimottes et creuser des trous de plantation.',
                'usage_tips': 'Prendre soin de ne pas casser la motte lors de l\'extraction du godet.',
                'is_premium': False
            }
        )

        Tool.objects.get_or_create(
            name='Serouette (ou Serfouette)',
            defaults={
                'category': 'entretien_arrosage',
                'description': 'Outil polyvalent doté d\'une panne (pour biner et désherber) et d\'une langue (pour tracer des sillons).',
                'usage_tips': 'Un binage vaut deux arrosages ! Utiliser la panne pour casser la croûte supérieure du sol.',
                'is_premium': False
            }
        )

        Tool.objects.get_or_create(
            name='Séquenceur de semis de précision',
            defaults={
                'category': 'semis_plantation',
                'description': 'Semoir à main avec sélecteur de diamètre pour doser et espacer finement les graines potagères.',
                'usage_tips': 'Réglage micrométrique pour les graines très fines de carottes et navets.',
                'is_premium': True
            }
        )

        # 5. Maladies & Insectes Nuisibles
        d_mildiou, _ = Disease.objects.get_or_create(
            name='Mildiou de la Tomate et Pomme de Terre',
            defaults={
                'symptoms': 'Taches d huile brunes sur les feuilles avec duvet blanc au revers. Dessèchement rapide des tiges et fruits impropres à la consommation.',
                'treatment': 'Supprimer immédiatement les feuilles atteintes. Pulvérisation de bicarbonate de potassium (5g/L) ou extrait fermenté de prêle.',
                'prevention': 'Espacer les plants, installer un toit abri pluie, éviter tout arrosage du feuillage.',
                'is_premium': True
            }
        )
        d_mildiou.affected_vegetables.add(v_tomate)

        d_oidium, _ = Disease.objects.get_or_create(
            name='Oïdium (Maladie du blanc)',
            defaults={
                'symptoms': 'Feutrage blanc poudreux sur le dessus des feuilles, déformation puis jaunissement des organes atteints.',
                'treatment': 'Pulvérisation d\'un mélange de lait de vache écrémé dilué à 10% dans l\'eau ou soufre pulvérisable.',
                'prevention': 'Maintenir une bonne circulation de l\'air autour des plants.',
                'is_premium': True
            }
        )
        d_oidium.affected_vegetables.add(v_courgette)

        ins_puceron, _ = Insect.objects.get_or_create(
            name='Pucerons (Verts et Noirs)',
            defaults={
                'description': 'Petits insectes piqueurs-suceurs se regroupant sous les jeunes pousses et les apex de tiges.',
                'damage': 'Crispation du feuillage, crispation des pousses, miellat collant favorisant la fumagine.',
                'solution': 'Pulvérisation de savon noir dilué (5%). Favoriser la présence des coccinelles, syrphes et chrysopes.',
                'is_premium': True
            }
        )
        ins_puceron.affected_vegetables.add(v_tomate, v_haricot, v_chou)

        ins_altise, _ = Insect.objects.get_or_create(
            name='Altises (Puces de jardin)',
            defaults={
                'description': 'Petits coléoptères noirs sauteurs perforant les feuilles de petits trous ronds.',
                'damage': 'Feuilles criblées de trous réduisant fortement la photosynthèse sur les jeunes semis.',
                'solution': 'Maintenir le sol et le feuillage humides (les altises détestent l\'humidité). Poser un voile anti-insectes fine maille.',
                'is_premium': True
            }
        )
        ins_altise.affected_vegetables.add(v_chou)

        self.stdout.write(self.style.SUCCESS('Base de données alimentée avec succès pour le Guide du Potager !'))
