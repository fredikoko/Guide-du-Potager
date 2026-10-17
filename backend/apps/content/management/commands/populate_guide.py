import os
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from apps.content.models import Part, Chapter, ChapterImage

class Command(BaseCommand):
    help = "Alimente la base de données avec les 4 parties et 26 chapitres issus du Guide_du_Potager_Tropical.md"

    def handle(self, *args, **options):
        # 1. Localiser le fichier Guide_du_Potager_Tropical.md
        candidate_paths = [
            settings.BASE_DIR.parent / 'Guide_du_Potager_Tropical.md',
            settings.BASE_DIR / 'Guide_du_Potager_Tropical.md',
            Path('Guide_du_Potager_Tropical.md'),
        ]
        guide_path = None
        for p in candidate_paths:
            if p.exists():
                guide_path = p
                break

        if not guide_path:
            self.stderr.write(self.style.ERROR("Fichier Guide_du_Potager_Tropical.md introuvable."))
            return

        self.stdout.write(self.style.SUCCESS(f"Chargement du guide depuis : {guide_path}"))
        with open(guide_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 2. Définition des 4 parties
        PARTS_CONFIG = {
            1: {
                'title': "Partie 1 : Les Fondamentaux du Jardinage Potager",
                'description': "Bases essentielles, compréhension et préparation du sol tropical, planification, semis, entretien quotidien et récolte.",
                'is_premium': False,
                'icon': "seedling"
            },
            2: {
                'title': "Partie 2 : Guide Pratique par Famille de Légumes",
                'description': "Fiches techniques complètes tropicalisées : légumes-racines, légumes-feuilles, légumes-fruits, légumes-bulbes, légumineuses, cucurbitacées, solanacées et herbes aromatiques.",
                'is_premium': True,
                'icon': "carrot"
            },
            3: {
                'title': "Partie 3 : Techniques Avancées et Situations Particulières",
                'description': "Permaculture tropicale, gestion des saisons des pluies et des saisons sèches, cyclones, potager urbain, protection agroécologique intégrée, semences paysannes et sols difficiles.",
                'is_premium': True,
                'icon': "shield-halved"
            },
            4: {
                'title': "Partie 4 : Annexes & Outils Pratiques",
                'description': "Tableaux comparatifs et synthèses agronomiques, glossaire tropical commenté, répertoire de semenciers engagés, index thématique complet et manifeste.",
                'is_premium': True,
                'icon': "table-list"
            }
        }

        # 3. Définition des 26 chapitres et annexes
        CHAPTERS_CONFIG = [
            # Partie 1 : Les Fondamentaux (Ch 1 à 6)
            (1, 1, r'^##\s+Chapitre 1\s*:', 'Chapitre 1 : Introduction au jardinage potager', False),
            (1, 2, r'^##\s+Chapitre 2\s*:', 'Chapitre 2 : Comprendre et préparer son sol', False),
            (1, 3, r'^##\s+Chapitre 3\s*:', 'Chapitre 3 : Planification du potager', True),
            (1, 4, r'^##\s+Chapitre 4\s*:', 'Chapitre 4 : Semis et plantations', True),
            (1, 5, r'^##\s+Chapitre 5\s*:', 'Chapitre 5 : L’entretien quotidien du potager', True),
            (1, 6, r'^##\s+Chapitre 6\s*:', 'Chapitre 6 : Récolte et conservation', True),

            # Partie 2 : Guide par Famille (Ch 7 à 14)
            (2, 7, r'^##\s+Chapitre 7\s*:', 'Chapitre 7 : Les légumes-racines', True),
            (2, 8, r'^##\s+Chapitre 8\s*:', 'Chapitre 8 : Les légumes-feuilles', True),
            (2, 9, r'^##\s+Chapitre 9\s*:', 'Chapitre 9 : Les légumes-fruits', True),
            (2, 10, r'^##\s+Chapitre 10\s*:', 'Chapitre 10 : Les légumes-bulbes', True),
            (2, 11, r'^##\s+Chapitre 11\s*:', 'Chapitre 11 : Les légumineuses', True),
            (2, 12, r'^##\s+Chapitre 12\s*:', 'Chapitre 12 : Les cucurbitacées', True),
            (2, 13, r'^##\s+Chapitre 13\s*:', 'Chapitre 13 : Les solanacées', True),
            (2, 14, r'^##\s+Chapitre 14\s*:', 'Chapitre 14 : Les herbes aromatiques', True),

            # Partie 3 : Techniques Avancées (Ch 15 à 21)
            (3, 15, r'^####?\s+Chapitre 15\s*:', 'Chapitre 15 : Permaculture tropicale et agroforesterie nourricière', True),
            (3, 16, r'^####?\s+Chapitre 16\s*:', 'Chapitre 16 : Maîtriser les extrêmes climatiques : Saison des pluies vs Saison sèche', True),
            (3, 17, r'^####?\s+Chapitre 17\s*:', 'Chapitre 17 : Jardiner face aux aléas météo majeurs : Cyclones, tempêtes et vents violents', True),
            (3, 18, r'^####?\s+Chapitre 18\s*:', 'Chapitre 18 : Le potager urbain et périurbain sous les tropiques', True),
            (3, 19, r'^####?\s+Chapitre 19\s*:', 'Chapitre 19 : Gestion agroécologique intégrée des ravageurs et maladies tropicales', True),
            (3, 20, r'^####?\s+Chapitre 20\s*:', 'Chapitre 20 : Semences paysannes et autonomie semencière en milieu chaud et humide', True),
            (3, 21, r'^####?\s+Chapitre 21\s*:', 'Chapitre 21 : Gestion des sols difficiles tropicaux', True),

            # Partie 4 : Annexes & Outils Pratiques (Ch 22 à 26)
            (4, 22, r'^####\s+1\.\s+Tableaux\s+comparatifs', 'Annexe 1 : Tableaux comparatifs et synthèses agronomiques', True),
            (4, 23, r'^####\s+2\.\s+Glossaire\s+agronomique', 'Annexe 2 : Glossaire agronomique et tropical commenté', True),
            (4, 24, r'^####\s+3\.\s+Répertoire\s+de\s+ressources', 'Annexe 3 : Répertoire de ressources, semenciers engagés et lectures agronomiques', True),
            (4, 25, r'^####\s+4\.\s+Index\s+thématique', 'Annexe 4 : Index thématique et alphabétique des légumes du potager tropical', True),
            (4, 26, r'^####\s+5\.\s+Conclusion\s+et\s+manifeste', 'Annexe 5 : Conclusion et manifeste pour la résilience alimentaire tropicale', True),
        ]

        # 4. Localiser les points d'entrée de chaque chapitre
        extracted_chapters = []
        for p_order, c_order, pattern, default_title, is_prem in CHAPTERS_CONFIG:
            start_idx = None
            for idx, line in enumerate(lines):
                if re.search(pattern, line.strip(), re.IGNORECASE):
                    start_idx = idx
                    break

            if start_idx is None:
                self.stderr.write(self.style.ERROR(f"Impossible de localiser le chapitre {c_order}: {pattern}"))
                return

            extracted_chapters.append({
                'part_order': p_order,
                'chapter_order': c_order,
                'start_idx': start_idx,
                'title': default_title,
                'is_premium': is_prem
            })

        # 5. Découper et nettoyer le contenu markdown
        for i, item in enumerate(extracted_chapters):
            next_start = extracted_chapters[i + 1]['start_idx'] if (i + 1 < len(extracted_chapters)) else len(lines)
            raw_lines = lines[item['start_idx'] + 1 : next_start]
            content_text = "".join(raw_lines)
            
            # Nettoyer d'éventuels bandeaux de transition de partie en queue de chapitre
            content_text = re.sub(
                r'---\s*\n+#{1,3}\s+(?:PARTIE|ANNEXES).*$',
                '',
                content_text,
                flags=re.DOTALL | re.IGNORECASE
            ).strip()

            words = len(content_text.split())
            reading_time = max(3, round(words / 180))

            item['content'] = content_text
            item['reading_time'] = reading_time
            item['words'] = words

        # 6. Insertion / Mise à jour dans la base de données
        with transaction.atomic():
            parts_map = {}
            for p_order, p_data in PARTS_CONFIG.items():
                part, _ = Part.objects.update_or_create(
                    order=p_order,
                    defaults={
                        'title': p_data['title'],
                        'description': p_data['description'],
                        'is_premium': p_data['is_premium'],
                        'icon': p_data['icon']
                    }
                )
                parts_map[p_order] = part
                self.stdout.write(self.style.SUCCESS(f"  [OK] Partie {p_order} synchronisee : {part.title}"))

            # Synchroniser les chapitres
            saved_chapters = []
            valid_chapter_ids = []

            for item in extracted_chapters:
                part = parts_map[item['part_order']]
                
                # Chercher un chapitre avec cet ordre
                chapter = Chapter.objects.filter(order=item['chapter_order']).first()
                if chapter:
                    chapter.part = part
                    chapter.title = item['title']
                    chapter.content = item['content']
                    chapter.is_premium = item['is_premium']
                    chapter.estimated_reading_time = item['reading_time']
                    chapter.save()
                    action = "Mis a jour"
                else:
                    chapter = Chapter.objects.create(
                        part=part,
                        order=item['chapter_order'],
                        title=item['title'],
                        content=item['content'],
                        is_premium=item['is_premium'],
                        estimated_reading_time=item['reading_time']
                    )
                    action = "Cree"

                saved_chapters.append(chapter)
                valid_chapter_ids.append(chapter.id)
                status_icon = "[PREMIUM]" if chapter.is_premium else "[GRATUIT]"
                self.stdout.write(
                    f"    {status_icon} [{action}] Ch {chapter.order:02d} ({item['words']} mots, ~{chapter.estimated_reading_time} min) : {chapter.title}"
                )

            # Re-affecter les ChapterImages avant suppression des orphelins
            ch1 = Chapter.objects.filter(order=1).first()
            ch2 = Chapter.objects.filter(order=2).first()
            ch4 = Chapter.objects.filter(order=4).first()
            
            for img in ChapterImage.objects.all():
                if img.chapter_id not in valid_chapter_ids:
                    if "potager_tropical" in str(img.image):
                        img.chapter = ch1
                    elif "Tithonia" in str(img.image):
                        img.chapter = ch2
                    elif "filets_ombrage" in str(img.image):
                        img.chapter = ch4
                    else:
                        img.chapter = ch1
                    img.save()
                    self.stdout.write(f"    Image {img.id} reassociee au chapitre {img.chapter.order}")

            # Supprimer les anciens chapitres orphelins non inclus dans les 26
            stale_chapters = Chapter.objects.exclude(id__in=valid_chapter_ids)
            if stale_chapters.exists():
                count = stale_chapters.count()
                stale_chapters.delete()
                self.stdout.write(self.style.WARNING(f"  Supprime {count} ancien(s) chapitre(s) orphelin(s)."))

        self.stdout.write(self.style.SUCCESS(
            f"\nSucces : 4 parties et {len(saved_chapters)} chapitres et annexes du Guide du Potager Tropical sont enregistres en base !"
        ))
