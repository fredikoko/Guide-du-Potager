import re
import html

class HTMLParser:
    @staticmethod
    def to_markup(html_content):
        """
        Convertit du code HTML riche (titres, paragraphes, gras, couleurs, listes, tableaux)
        en balises de formatage Kivy Markup compatibles :
        [b], [/b], [i], [/i], [u], [/u], [size=...], [/size], [color=...], [/color].
        """
        if not html_content:
            return ""

        text = html_content

        # 1. Remplacement des entités courantes et espaces insécables
        text = text.replace('&nbsp;', ' ')

        # 2. Suppression des icônes de polices vides (ex: <i class="fa-solid fa-leaf"></i>)
        text = re.sub(r'<i\s+class=["\'][^"\']*fa-[^"\']*["\'][^>]*>\s*</i>', '', text, flags=re.IGNORECASE)

        # 3. Badges numérotés dans les titres (ex: <span ...>1</span> Titre -> 1. Titre)
        text = re.sub(
            r'<h([1-6])[^>]*>\s*<span[^>]*>([0-9]+|[A-Z])</span>\s*(.*?)</h\1>',
            r'<h\1>\2. \3</h\1>',
            text, flags=re.DOTALL | re.IGNORECASE
        )

        # 4. Conversion des couleurs explicites
        # Style inline : style="...color: #47C26B..."
        text = re.sub(
            r'<span[^>]*style=["\'][^"\']*color:\s*#?([0-9a-fA-F]{6})[^"\']*["\'][^>]*>(.*?)</span>',
            r'[color=\1]\2[/color]',
            text, flags=re.DOTALL | re.IGNORECASE
        )
        # Classes Tailwind hexadécimales : text-[#47C26B], text-[#1E592E], text-[#3D7A42]
        text = re.sub(
            r'<span[^>]*class=["\'][^"\']*text-\[#([0-9a-fA-F]{6})\][^"\']*["\'][^>]*>(.*?)</span>',
            r'[color=\1]\2[/color]',
            text, flags=re.DOTALL | re.IGNORECASE
        )
        text = re.sub(
            r'<strong[^>]*class=["\'][^"\']*text-\[#([0-9a-fA-F]{6})\][^"\']*["\'][^>]*>(.*?)</strong>',
            r'[color=\1][b]\2[/b][/color]',
            text, flags=re.DOTALL | re.IGNORECASE
        )

        # Classes Tailwind sémantiques vers couleurs de la palette
        text = re.sub(
            r'<span[^>]*class=["\'][^"\']*text-(?:emerald|green)-[0-9]{3}[^"\']*["\'][^>]*>(.*?)</span>',
            r'[color=3D7A42]\1[/color]',
            text, flags=re.DOTALL | re.IGNORECASE
        )
        text = re.sub(
            r'<span[^>]*class=["\'][^"\']*text-amber-[0-9]{3}[^"\']*["\'][^>]*>(.*?)</span>',
            r'[color=47C26B]\1[/color]',
            text, flags=re.DOTALL | re.IGNORECASE
        )
        text = re.sub(
            r'<span[^>]*class=["\'][^"\']*text-red-[0-9]{3}[^"\']*["\'][^>]*>(.*?)</span>',
            r'[color=DC2626]\1[/color]',
            text, flags=re.DOTALL | re.IGNORECASE
        )

        # 5. Titres HTML avec n'importe quels attributs (class, style...)
        text = re.sub(r'<h1(?:\s+[^>]*)?>(.*?)</h1>', r'\n\n[size=22][b][color=1E592E]\1[/color][/b][/size]\n\n', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<h2(?:\s+[^>]*)?>(.*?)</h2>', r'\n\n[size=19][b][color=1E592E]\1[/color][/b][/size]\n\n', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<h3(?:\s+[^>]*)?>(.*?)</h3>', r'\n\n[size=17][b][color=3D7A42]\1[/color][/b][/size]\n\n', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<h4(?:\s+[^>]*)?>(.*?)</h4>', r'\n\n[size=16][b][color=3D7A42]\1[/color][/b][/size]\n\n', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<h[5-6](?:\s+[^>]*)?>(.*?)</h[5-6]>', r'\n\n[size=15][b][color=543826]\1[/color][/b][/size]\n\n', text, flags=re.DOTALL | re.IGNORECASE)

        # 6. Gras, Italique, Souligné avec attributs éventuels
        text = re.sub(r'<b(?:\s+[^>]*)?>(.*?)</b>', r'[b]\1[/b]', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<strong(?:\s+[^>]*)?>(.*?)</strong>', r'[b]\1[/b]', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<i(?:\s+[^>]*)?>(.*?)</i>', r'[i]\1[/i]', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<em(?:\s+[^>]*)?>(.*?)</em>', r'[i]\1[/i]', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<u(?:\s+[^>]*)?>(.*?)</u>', r'[u]\1[/u]', text, flags=re.DOTALL | re.IGNORECASE)

        # 7. Sauts de ligne et paragraphes
        text = re.sub(r'<br\s*/?>', r'\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<p(?:\s+[^>]*)?>(.*?)</p>', r'\1\n\n', text, flags=re.DOTALL | re.IGNORECASE)

        # 8. Listes à puces et ordonnées
        text = re.sub(r'<li(?:\s+[^>]*)?>(.*?)</li>', r'  • \1\n', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'</?(?:ul|ol)(?:\s+[^>]*)?>', r'\n', text, flags=re.IGNORECASE)

        # 9. Tableaux HTML -> Affichage structuré et lisible pour mobile
        def format_tr(m):
            row_html = m.group(1)
            cells = re.findall(r'<(?:th|td)(?:\s+[^>]*)?>(.*?)</(?:th|td)>', row_html, flags=re.DOTALL | re.IGNORECASE)
            clean_cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
            clean_cells = [c for c in clean_cells if c]
            if not clean_cells:
                return ""
            if '<th' in row_html.lower():
                return "\n• [b]" + "  |  ".join(clean_cells) + "[/b]\n"
            else:
                return "  • " + " — ".join(clean_cells) + "\n"

        text = re.sub(r'<tr(?:\s+[^>]*)?>(.*?)</tr>', format_tr, text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'</?(?:table|thead|tbody|tfoot)(?:\s+[^>]*)?>', r'\n', text, flags=re.IGNORECASE)

        # 10. Citations et encarts div
        text = re.sub(r'<blockquote(?:\s+[^>]*)?>(.*?)</blockquote>', r'\n[i]« \1 »[/i]\n', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<div(?:\s+[^>]*)?>', r'\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</div>', r'\n', text, flags=re.IGNORECASE)

        # 11. Nettoyage des balises HTML restantes
        text = re.sub(r'<[^>]+>', '', text)

        # 12. Décodage des entités HTML (&eacute;, &amp;...)
        text = html.unescape(text)

        # 13. Suppression des balises Kivy vides résiduelles
        text = re.sub(r'\[(b|i|u|s)\]\s*\[/\1\]', '', text)

        # 14. Normalisation des espaces et sauts de ligne multiples
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r' \n', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    @staticmethod
    def parse_blocks(html_content, base_url="http://127.0.0.1:8000"):
        if not html_content:
            return []

        img_pattern = re.compile(r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>', re.IGNORECASE)
        blocks = []
        last_idx = 0

        for match in img_pattern.finditer(html_content):
            start, end = match.span()
            text_part = html_content[last_idx:start]

            if text_part.strip():
                markup = HTMLParser.to_markup(text_part)
                if markup.strip():
                    blocks.append({'type': 'text', 'content': markup})

            img_src = match.group(1)
            if img_src.startswith('/'):
                img_url = f"{base_url.rstrip('/')}{img_src}"
            else:
                img_url = img_src

            blocks.append({'type': 'image', 'url': img_url})
            last_idx = end

        remaining = html_content[last_idx:]
        if remaining.strip():
            markup = HTMLParser.to_markup(remaining)
            if markup.strip():
                blocks.append({'type': 'text', 'content': markup})

        return blocks
