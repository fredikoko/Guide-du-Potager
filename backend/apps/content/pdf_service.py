import os
import re
import html
from io import BytesIO
from django.conf import settings
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, HRFlowable, KeepTogether, Preformatted
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# ==============================================================================
# ENREGISTREMENT POLICE MONOSPACE AVEC SUPPORT UNICODE (SCHÉMAS & DIAGRAMMES)
# ==============================================================================
MONO_FONT_NAME = 'Courier'

BOX_TO_ASCII = {
    '│': '|', '─': '-', '┌': '+', '┐': '+', '└': '+', '┘': '+',
    '╭': '+', '╮': '+', '╰': '+', '╯': '+',
    '├': '+', '┤': '+', '┬': '+', '┴': '+', '┼': '+',
    '═': '=', '║': '|', '╧': '=', '╤': '=', '╪': '=',
    '◄': '<', '►': '>', '▼': 'v', '▲': '^',
    '░': '.', '▒': ':', '▓': '#', '█': '#',
    '•': '*', '→': '->', '←': '<-',
    '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
}

def _register_monospace_font():
    global MONO_FONT_NAME
    candidates = [
        # Windows
        ("Consolas", "C:/Windows/Fonts/consola.ttf"),
        ("LucidaConsole", "C:/Windows/Fonts/lucon.ttf"),
        ("CourierNew", "C:/Windows/Fonts/cour.ttf"),
        # Linux / Docker
        ("DejaVuSansMono", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        ("FreeMono", "/usr/share/fonts/truetype/freefont/FreeMono.ttf"),
        ("UbuntuMono", "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf"),
    ]
    for font_name, font_path in candidates:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                MONO_FONT_NAME = font_name
                return
            except Exception:
                continue

_register_monospace_font()


# ==============================================================================
# COULEURS & CHARTE VISUELLE DU POTAGER TROPICAL
# ==============================================================================
COLOR_PRIMARY = colors.HexColor('#1E592E')      # Vert Forêt
COLOR_SECONDARY = colors.HexColor('#3D7A42')    # Vert Feuillage
COLOR_ACCENT = colors.HexColor('#47C26B')       # Vert Lumineux Exclusif
COLOR_DARK = colors.HexColor('#1A202C')         # Texte Sombre
COLOR_MUTED = colors.HexColor('#718096')        # Gris Atténué
COLOR_BG_CARD = colors.HexColor('#F7F5ED')      # Fond Crème Chaud
COLOR_BORDER = colors.HexColor('#E2E8F0')       # Ligne de séparation


# ==============================================================================
# CANVAS AVEC NUMÉROTATION DYNAMIQUE (Page X sur Y) & EN-TÊTE DE SECTION
# ==============================================================================
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Ne rien afficher sur la page de garde (page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(COLOR_MUTED)

        width, height = A4

        # En-tête (pages >= 2)
        self.drawString(54, height - 36, "Guide du Potager Tropical — Manuel Complet de Maraîchage")
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(54, height - 42, width - 54, height - 42)

        # Pied de page (pages >= 2)
        footer_text = f"Page {self._pageNumber} sur {page_count}"
        self.drawRightString(width - 54, 34, footer_text)
        self.drawString(54, 34, "© Guide du Potager Tropical • Pratiques Conventionnelles & Agro-écologiques")
        self.line(54, 46, width - 54, 46)

        self.restoreState()


# ==============================================================================
# FEUILLES DE STYLES TYPOGRAPHIQUES
# ==============================================================================
def get_pdf_styles():
    base_styles = getSampleStyleSheet()

    styles = {
        'CoverTitle': ParagraphStyle(
            'CoverTitle',
            parent=base_styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=28,
            leading=34,
            textColor=colors.white,
            alignment=1, # Centré
            spaceAfter=15,
        ),
        'CoverSubtitle': ParagraphStyle(
            'CoverSubtitle',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=13,
            leading=18,
            textColor=colors.HexColor('#E2E8F0'),
            alignment=1,
            spaceAfter=20,
        ),
        'CoverBadge': ParagraphStyle(
            'CoverBadge',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=14,
            textColor=COLOR_ACCENT,
            alignment=1,
            spaceAfter=15,
        ),
        'CoverMeta': ParagraphStyle(
            'CoverMeta',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#CBD5E1'),
            alignment=1,
        ),
        'TOCPart': ParagraphStyle(
            'TOCPart',
            parent=base_styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=COLOR_PRIMARY,
            spaceBefore=14,
            spaceAfter=6,
        ),
        'TOCChapter': ParagraphStyle(
            'TOCChapter',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=15,
            textColor=COLOR_DARK,
            leftIndent=15,
        ),
        'PartHeader': ParagraphStyle(
            'PartHeader',
            parent=base_styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=25,
            textColor=COLOR_PRIMARY,
            spaceBefore=15,
            spaceAfter=8,
        ),
        'PartDesc': ParagraphStyle(
            'PartDesc',
            parent=base_styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=10,
            leading=15,
            textColor=COLOR_MUTED,
            spaceAfter=15,
        ),
        'ChapterHeader': ParagraphStyle(
            'ChapterHeader',
            parent=base_styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=15,
            leading=20,
            textColor=COLOR_PRIMARY,
            spaceBefore=18,
            spaceAfter=8,
            keepWithNext=True,
        ),
        'ChapterMeta': ParagraphStyle(
            'ChapterMeta',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=13,
            textColor=COLOR_SECONDARY,
            spaceAfter=10,
            keepWithNext=True,
        ),
        'Body': ParagraphStyle(
            'Body',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=15,
            textColor=COLOR_DARK,
            spaceAfter=8,
        ),
        'Bullet': ParagraphStyle(
            'Bullet',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=COLOR_DARK,
            leftIndent=15,
            spaceAfter=4,
        ),
        'Quote': ParagraphStyle(
            'Quote',
            parent=base_styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor('#2D3748'),
            leftIndent=15,
            spaceBefore=6,
            spaceAfter=8,
        ),
        'Caption': ParagraphStyle(
            'Caption',
            parent=base_styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=11,
            textColor=COLOR_MUTED,
            alignment=1,
            spaceAfter=10,
        ),
        'ArticleTitle': ParagraphStyle(
            'ArticleTitle',
            parent=base_styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=27,
            textColor=COLOR_PRIMARY,
            spaceAfter=10,
        ),
    }

    return styles


# ==============================================================================
# PARSEUR DE TEXTE / HTML VERS FLOWABLES REPORTLAB
# ==============================================================================
def html_to_reportlab_paragraphs(raw_text, styles):
    """
    Nettoie et convertit un contenu riche (Markdown/HTML/Texte brut)
    en liste de Flowables compatibles ReportLab.
    """
    if not raw_text:
        return []

    from apps.content.rendering import render_content
    html_content = render_content(raw_text)

    flowables = []

    # Découpage par blocs de balises principales
    blocks = re.split(r'(<(?:h[1-6]|p|ul|ol|blockquote|pre)[^>]*>.*?</(?:h[1-6]|p|ul|ol|blockquote|pre)>|<hr[^>]*>)', html_content, flags=re.DOTALL | re.IGNORECASE)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Blocs de code ou schémas préformatés ASCII/Unicode <pre>
        m_pre = re.match(r'<pre[^>]*>(.*?)</pre>', block, re.DOTALL | re.IGNORECASE)
        if m_pre:
            code_card = _create_code_flowable(m_pre.group(1))
            if code_card:
                flowables.append(Spacer(1, 6))
                flowables.append(code_card)
                flowables.append(Spacer(1, 6))
            continue

        # Titres
        m_h1 = re.match(r'<h1[^>]*>(.*?)</h1>', block, re.DOTALL | re.IGNORECASE)
        m_h2 = re.match(r'<h2[^>]*>(.*?)</h2>', block, re.DOTALL | re.IGNORECASE)
        m_h3 = re.match(r'<h[3-6][^>]*>(.*?)</h[3-6]>', block, re.DOTALL | re.IGNORECASE)
        if m_h1 or m_h2 or m_h3:
            title_text = _clean_inline_html(m_h1.group(1) if m_h1 else (m_h2.group(1) if m_h2 else m_h3.group(1)))
            style = styles['ChapterHeader']
            flowables.append(Spacer(1, 6))
            flowables.append(Paragraph(title_text, style))
            continue

        # Citation / Blockquote
        m_quote = re.match(r'<blockquote[^>]*>(.*?)</blockquote>', block, re.DOTALL | re.IGNORECASE)
        if m_quote:
            quote_text = _clean_inline_html(m_quote.group(1))
            quote_para = Paragraph(f"« {quote_text} »", styles['Quote'])
            t = Table([[quote_para]], colWidths=[480])
            t.setStyle(TableStyle([
                ('LINEBEFORE', (0, 0), (0, -1), 3, COLOR_ACCENT),
                ('BACKGROUND', (0, 0), (0, -1), COLOR_BG_CARD),
                ('TOPPADDING', (0, 0), (0, -1), 6),
                ('BOTTOMPADDING', (0, 0), (0, -1), 6),
                ('LEFTPADDING', (0, 0), (0, -1), 10),
            ]))
            flowables.append(t)
            flowables.append(Spacer(1, 6))
            continue

        # Listes à puces
        m_list = re.match(r'<(?:ul|ol)[^>]*>(.*?)</(?:ul|ol)>', block, re.DOTALL | re.IGNORECASE)
        if m_list:
            items = re.findall(r'<li[^>]*>(.*?)</li>', m_list.group(1), re.DOTALL | re.IGNORECASE)
            for item in items:
                clean_item = _clean_inline_html(item)
                flowables.append(Paragraph(f"• {clean_item}", styles['Bullet']))
            flowables.append(Spacer(1, 4))
            continue

        # Séparateur horizontal
        if re.match(r'<hr[^>]*>', block, re.IGNORECASE):
            flowables.append(Spacer(1, 6))
            flowables.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER, spaceAfter=8, spaceBefore=4))
            continue

        # Paragraphes <p> ou blocs textuels
        m_p = re.match(r'<p[^>]*>(.*?)</p>', block, re.DOTALL | re.IGNORECASE)
        content_text = m_p.group(1) if m_p else block

        # Extraire les images insérées <img> s'il y en a
        img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', content_text)
        for img_url in img_matches:
            img_flowable = _load_image_flowable(img_url, max_width=450, max_height=200)
            if img_flowable:
                flowables.append(Spacer(1, 6))
                flowables.append(img_flowable)
                flowables.append(Spacer(1, 6))

        # Nettoyage du texte du paragraphe
        text_without_img = re.sub(r'<img[^>]*>', '', content_text)
        clean_text = _clean_inline_html(text_without_img)
        if clean_text:
            flowables.append(Paragraph(clean_text, styles['Body']))

    return flowables


def _create_code_flowable(raw_code_content):
    """
    Crée un Flowable adapté pour les blocs de code ou diagrammes ASCII/Unicode.
    Gère la largeur dynamique des caractères et le rendu avec bordure et fond contrasté.
    Découpe en tranches de 25 lignes pour permettre les sauts de page fluides sans LayoutError.
    """
    if not raw_code_content:
        return None

    # Extraire le texte brut en retirant l'éventuelle balise <code>
    clean = re.sub(r'<code[^>]*>', '', raw_code_content, flags=re.IGNORECASE)
    clean = re.sub(r'</code>', '', clean, flags=re.IGNORECASE)
    clean = html.unescape(clean)
    clean = clean.strip('\r\n')
    if not clean.strip():
        return None

    # Si la police est le Courier standard ReportLab (Type 1 sans glyphes Unicode étendus),
    # convertir les caractères de boîtes et flèches en équivalents ASCII lisibles
    if MONO_FONT_NAME == 'Courier':
        for ch, repl in BOX_TO_ASCII.items():
            clean = clean.replace(ch, repl)
        clean = clean.encode('latin-1', errors='replace').decode('latin-1')

    lines = clean.splitlines()
    max_len = max((len(line) for line in lines), default=0)

    # Calcul dynamique de la taille de police pour ne pas déborder de la page (485 pt)
    if max_len > 80:
        f_size, f_lead = 5.8, 7.2
    elif max_len > 65:
        f_size, f_lead = 6.6, 8.2
    elif max_len > 45:
        f_size, f_lead = 7.5, 9.5
    else:
        f_size, f_lead = 8.0, 10.5

    code_style = ParagraphStyle(
        f'PreFormatted_{f_size}',
        fontName=MONO_FONT_NAME,
        fontSize=f_size,
        leading=f_lead,
        textColor=COLOR_DARK,
    )

    # Découpage par paquets de 25 lignes pour que ReportLab puisse répartir
    # les très grands schémas / codes sur plusieurs pages sans dépasser la hauteur de page
    chunk_size = 25
    table_data = []
    for i in range(0, len(lines), chunk_size):
        chunk_text = '\n'.join(lines[i:i + chunk_size])
        table_data.append([Preformatted(chunk_text, code_style)])

    table = Table(table_data, colWidths=[485])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return table


def _clean_inline_html(text):
    """
    Ne conserve que les balises gérées par ReportLab Paragraph (b, strong, i, em, u, a).
    Supprime toutes les autres balises avec classes HTML.
    """
    if not text:
        return ""

    # Normaliser strong/em
    text = re.sub(r'<strong[^>]*>', '<b>', text, flags=re.IGNORECASE)
    text = text.replace('</strong>', '</b>')
    text = re.sub(r'<em[^>]*>', '<i>', text, flags=re.IGNORECASE)
    text = text.replace('</em>', '</i>')

    # Supprimer balises non supportées mais garder le texte intérieur
    text = re.sub(r'</?(?:div|span|section|article|code|pre|figure|figcaption)[^>]*>', '', text, flags=re.IGNORECASE)

    # Convertir <br> en <br/>
    text = re.sub(r'<br\s*/?>', '<br/>', text, flags=re.IGNORECASE)

    # Supprimer les balises restantes inconnues sauf a, b, i, u
    text = re.sub(r'<(?!\/?(?:b|i|u|a|br\/?)\b)[^>]*>', '', text, flags=re.IGNORECASE)

    return text.strip()


def _load_image_flowable(img_url, max_width=450, max_height=220):
    """Charge en toute sécurité un Flowable Image ReportLab à partir d'un chemin media local."""
    try:
        # Nettoyer l'URL pour retrouver le fichier sur le disque local
        clean_path = img_url.replace(settings.MEDIA_URL, '').lstrip('/')
        local_path = os.path.join(settings.MEDIA_ROOT, clean_path)

        if os.path.exists(local_path):
            from PIL import Image as PILImage
            with PILImage.open(local_path) as pil_img:
                w, h = pil_img.size
                ratio = min(max_width / w, max_height / h, 1.0)
                final_w = w * ratio
                final_h = h * ratio
                return Image(local_path, width=final_w, height=final_h)
    except Exception:
        pass
    return None


# ==============================================================================
# GÉNÉRATEUR : GUIDE COMPLET DU POTAGER (EBOOK PDF)
# ==============================================================================
def generate_guide_pdf(output_stream, user=None):
    """
    Compile l'ensemble des parties et chapitres du guide dans un document
    PDF complet de haute qualité avec couverture, sommaire et pagination.
    """
    from apps.content.models import Part, Chapter

    doc = SimpleDocTemplate(
        output_stream,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = get_pdf_styles()
    story = []

    # --------------------------------------------------------------------------
    # 1. PAGE DE COUVERTURE SOMPTUEUSE
    # --------------------------------------------------------------------------
    story.append(Spacer(1, 40))

    cover_badge = Paragraph("MANUEL PRATIQUE OFFICIEL", styles['CoverBadge'])
    cover_title = Paragraph("GUIDE COMPLET DU POTAGER TROPICAL", styles['CoverTitle'])
    cover_subtitle = Paragraph(
        "Itinéraires Techniques Conventionnels & Protocoles Agro-écologiques<br/>"
        "pour Réussir vos Cultures en Afrique Tropicale & Sahélienne",
        styles['CoverSubtitle']
    )

    meta_user = f"Exemplaire délivré à : {user.email}" if user and user.is_authenticated else "Édition Numérique Autorisée"
    meta_date = f"Mise à jour : {timezone.now().strftime('%B %Y')}"
    cover_meta = Paragraph(f"{meta_user}<br/>{meta_date}<br/>Tous droits réservés • Reproduction interdite", styles['CoverMeta'])

    # Boîte de couverture stylisée
    cover_data = [
        [Spacer(1, 15)],
        [cover_badge],
        [cover_title],
        [HRFlowable(width="60%", thickness=1, color=COLOR_ACCENT, spaceAfter=15, spaceBefore=5)],
        [cover_subtitle],
        [Spacer(1, 40)],
        [cover_meta],
        [Spacer(1, 15)],
    ]
    cover_table = Table(cover_data, colWidths=[485])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('LEFTPADDING', (0, 0), (-1, -1), 25),
        ('RIGHTPADDING', (0, 0), (-1, -1), 25),
    ]))

    story.append(cover_table)
    story.append(PageBreak())

    # --------------------------------------------------------------------------
    # 2. SOMMAIRE DU MANUEL (TABLE DES MATIÈRES)
    # --------------------------------------------------------------------------
    story.append(Paragraph("Sommaire Général du Guide", styles['PartHeader']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_PRIMARY, spaceAfter=15, spaceBefore=4))

    parts = Part.objects.prefetch_related('chapters').all().order_by('order')

    for part in parts:
        p_title = f"Partie {part.order} : {part.title}"
        if part.is_premium:
            p_title += " [★ Exclusif]"
        story.append(Paragraph(p_title, styles['TOCPart']))

        for chap in part.chapters.all().order_by('order'):
            c_title = f"• Chapitre {chap.order} : {chap.title}"
            story.append(Paragraph(c_title, styles['TOCChapter']))

    story.append(PageBreak())

    # --------------------------------------------------------------------------
    # 3. CONTENU DÉTAILLÉ DES PARTIES ET CHAPITRES
    # --------------------------------------------------------------------------
    for part in parts:
        # En-tête de Partie
        part_box_data = [
            [Paragraph(f"PARTIE {part.order} • {part.title.upper()}", styles['CoverTitle'])],
        ]
        if part.description:
            part_box_data.append([Paragraph(part.description, styles['CoverSubtitle'])])

        part_box = Table(part_box_data, colWidths=[485])
        part_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_SECONDARY),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 16),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))

        story.append(part_box)
        story.append(Spacer(1, 15))

        # Chapitres de cette partie
        for chap in part.chapters.all().order_by('order'):
            story.append(Spacer(1, 10))
            chap_badge = f"PARTIE {part.order} • CHAPITRE {chap.order}"
            if chap.is_premium:
                chap_badge += "  •  ★ CONTENU EXCLUSIF"
            
            story.append(Paragraph(chap_badge, styles['ChapterMeta']))
            story.append(Paragraph(chap.title, styles['ChapterHeader']))
            story.append(HRFlowable(width="100%", thickness=0.8, color=COLOR_ACCENT, spaceAfter=12, spaceBefore=2))

            # Images associées au chapitre
            for c_img in chap.images.all().order_by('order'):
                if c_img.image and os.path.exists(c_img.image.path):
                    flow_img = _load_image_flowable(c_img.image.url, max_width=460, max_height=220)
                    if flow_img:
                        story.append(flow_img)
                        if c_img.caption:
                            story.append(Paragraph(c_img.caption, styles['Caption']))
                        story.append(Spacer(1, 6))

            # Contenu riche textuel
            flowables = html_to_reportlab_paragraphs(chap.content, styles)
            story.extend(flowables)
            story.append(Spacer(1, 20))

        story.append(PageBreak())

    # Construction du document avec NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)


# ==============================================================================
# GÉNÉRATEUR : FICHE ARTICLE UNIQUE EN PDF
# ==============================================================================
def generate_post_pdf(post, output_stream, user=None):
    """
    Génère une fiche technique professionnelle en PDF pour un article de blog individuel.
    """
    doc = SimpleDocTemplate(
        output_stream,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = get_pdf_styles()
    story = []

    # En-tête de l'article
    cat_name = post.category.name if post.category else "Fiche Maraîchère"
    date_str = post.published_at.strftime("%d %B %Y") if post.published_at else ""
    meta_line = f"Catégorie : <b>{cat_name}</b>  •  Publié le {date_str}"
    if post.is_premium:
        meta_line += "  •  <b>★ Contenu Exclusif</b>"

    story.append(Paragraph(meta_line, styles['ChapterMeta']))
    story.append(Paragraph(post.title, styles['ArticleTitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_PRIMARY, spaceAfter=12, spaceBefore=4))

    # Image de couverture de l'article si existante
    if post.cover_image and os.path.exists(post.cover_image.path):
        cover_img = _load_image_flowable(post.cover_image.url, max_width=485, max_height=230)
        if cover_img:
            story.append(cover_img)
            story.append(Spacer(1, 10))

    # Extrait mis en valeur dans un encadré
    if post.excerpt:
        callout_p = Paragraph(f"<b>Résumé pratique :</b> {post.excerpt}", styles['Quote'])
        callout_table = Table([[callout_p]], colWidths=[485])
        callout_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_CARD),
            ('LINEBEFORE', (0, 0), (0, -1), 3.5, COLOR_PRIMARY),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(callout_table)
        story.append(Spacer(1, 12))

    # Contenu riche de l'article
    flowables = html_to_reportlab_paragraphs(post.content, styles)
    story.extend(flowables)

    # Foire aux questions FAQ associée à l'article
    faqs = post.faqs.all().order_by('order')
    if faqs.exists():
        story.append(Spacer(1, 15))
        story.append(Paragraph("Questions Fréquentes (FAQ)", styles['ChapterHeader']))
        story.append(HRFlowable(width="100%", thickness=0.8, color=COLOR_ACCENT, spaceAfter=10, spaceBefore=2))

        for faq in faqs:
            story.append(Paragraph(f"<b>Q : {faq.question}</b>", styles['Body']))
            story.append(Paragraph(faq.answer, styles['Quote']))
            story.append(Spacer(1, 6))

    # Bloc de signature et copyright
    story.append(Spacer(1, 20))
    buyer_note = f"Document réservé à : {user.email}" if user and user.is_authenticated else "Document officiel Guide du Potager"
    footer_card = Table([[
        Paragraph(f"<b>Guide du Potager Tropical</b> — Pratiques Sahéliennes & Équatoriales<br/>{buyer_note}", styles['Caption'])
    ]], colWidths=[485])
    footer_card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_CARD),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(footer_card)

    doc.build(story, canvasmaker=NumberedCanvas)
