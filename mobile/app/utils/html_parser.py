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

        # 1.1 Support universel de la syntaxe Markdown (titres #, ##, ###, ####, #####, ######)
        # Gestion des titres enveloppés dans des balises HTML (<p>### ...</p> ou <br/>### ...)
        text = re.sub(
            r'<(?:p|div)[^>]*>\s*(#{1,6})\s*(.*?)(?:\s*#+)?\s*</(?:p|div)>',
            lambda m: f"<h{len(m.group(1))}>{m.group(2).strip()}</h{len(m.group(1))}>",
            text, flags=re.IGNORECASE
        )
        text = re.sub(
            r'(?:<br\s*/?>\s*)+(#{1,6})\s*(.*?)(?:\s*#+)?(?=<br\s*/?>|\n|$)',
            lambda m: f"<h{len(m.group(1))}>{m.group(2).strip()}</h{len(m.group(1))}>",
            text, flags=re.IGNORECASE
        )

        # Titres Markdown directs avec ou sans indentation, et suppression des trailing #
        def format_md_heading(m):
            lvl = len(m.group(1))
            heading_text = m.group(2).strip()
            sizes = {1: '22', 2: '19', 3: '17', 4: '16', 5: '15', 6: '14'}
            colors = {1: '1E592E', 2: '1E592E', 3: '3D7A42', 4: '3D7A42', 5: '543826', 6: '543826'}
            size_val = sizes.get(lvl, '16')
            color_val = colors.get(lvl, '3D7A42')
            return f"\n\n[size={size_val}][b][color={color_val}]{heading_text}[/color][/b][/size]\n\n"

        text = re.sub(r'^[ \t]*(#{1,6})\s*(.*?)(?:\s*#+)?$', format_md_heading, text, flags=re.MULTILINE)
        # Gras / Italique Markdown
        text = re.sub(r'(?:\*\*\*|___)(.*?)(?:\*\*\*|___)', r'[b][i]\1[/i][/b]', text)
        text = re.sub(r'(?:\*\*|__)(.*?)(?:\*\*|__)', r'[b]\1[/b]', text)
        text = re.sub(r'(?<![a-zA-Z0-9])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![a-zA-Z0-9])', r'[i]\1[/i]', text)
        text = re.sub(r'(?<![a-zA-Z0-9])_(?!\s)([^_\n]+?)(?<!\s)_(?![a-zA-Z0-9])', r'[i]\1[/i]', text)
        # Listes Markdown
        text = re.sub(r'^\s*[-*+]\s+(.+)$', r'  • \1', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*(\d+)\.\s+(.+)$', r'  \1. \2', text, flags=re.MULTILINE)
        # Citations Markdown
        text = re.sub(r'^>\s*(.+)$', r'\n[i]« \1 »[/i]\n', text, flags=re.MULTILINE)
        # Liens Markdown [texte](url)
        text = re.sub(r'(?<!!)\[(.*?)\]\((.*?)\)', r'[color=3D7A42][u]\1[/u][/color]', text)
        # Code inline `code`
        text = re.sub(r'`([^`]+)`', r'[color=1E592E]\1[/color]', text)

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

        # 13.5 Nettoyage résiduel de tout # Markdown orphelin en début de ligne
        text = re.sub(r'^[ \t]*#{1,6}\s*(.*?)(?:\s*#+)?$', r'[size=17][b][color=3D7A42]\1[/color][/b][/size]', text, flags=re.MULTILINE)

        # 14. Normalisation des espaces et sauts de ligne multiples
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r' \n', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    @staticmethod
    def parse_html_table(table_html):
        headers = []
        rows = []

        # En-têtes (th)
        th_matches = re.findall(r'<th(?:\s+[^>]*)?>(.*?)</th>', table_html, re.DOTALL | re.IGNORECASE)
        if th_matches:
            headers = [HTMLParser.to_markup(th).strip() for th in th_matches]

        # Lignes (tr)
        tr_matches = re.finditer(r'<tr(?:\s+[^>]*)?>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)
        for tr in tr_matches:
            tr_content = tr.group(1)
            td_matches = re.findall(r'<td(?:\s+[^>]*)?>(.*?)</td>', tr_content, re.DOTALL | re.IGNORECASE)
            if td_matches:
                row_cells = [HTMLParser.to_markup(td).strip() for td in td_matches]
                rows.append(row_cells)
            elif not headers:
                th_cells = re.findall(r'<th(?:\s+[^>]*)?>(.*?)</th>', tr_content, re.DOTALL | re.IGNORECASE)
                if th_cells:
                    headers = [HTMLParser.to_markup(th).strip() for th in th_cells]

        return headers, rows

    @staticmethod
    def parse_markdown_table(md_text):
        lines = [l.strip() for l in md_text.strip().split('\n') if l.strip()]
        if len(lines) < 2:
            return [], []

        def parse_row(r_str):
            cells = [HTMLParser.to_markup(c.strip()).strip() for c in r_str.strip().strip('|').split('|')]
            return cells

        headers = parse_row(lines[0])
        rows = []
        for l in lines[2:]:
            if '|' in l:
                rows.append(parse_row(l))

        return headers, rows

    @staticmethod
    def parse_blocks(html_content, base_url="http://127.0.0.1:8000"):
        if not html_content:
            return []

        # 1. Détection des tableaux HTML (<table...>...</table>)
        table_html_pattern = re.compile(
            r'(?:<div[^>]*class=["\'][^"\']*overflow-x-auto[^"\']*["\'][^>]*>\s*)?<table(?:\s+[^>]*)?>(.*?)</table>(?:\s*</div>)?',
            re.DOTALL | re.IGNORECASE
        )

        # 2. Détection des tableaux Markdown (| col 1 | col 2 |\n| --- | --- |\n| ...)
        table_md_pattern = re.compile(
            r'(?:^[ \t]*\|[^\n]+\|[ \t]*\n[ \t]*\|(?:\s*:?-+:?\s*\|)+\s*(?:\n[ \t]*\|[^\n]+\|[ \t]*)+)',
            re.MULTILINE
        )

        # 3. Détection des images (HTML <img> et Markdown ![alt](url))
        img_pattern = re.compile(
            r'(?:<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>|!\[(.*?)\]\(([^)\s]+)(?:\s+"[^"]*")?\))',
            re.IGNORECASE
        )

        elements = []

        # Collecte des tableaux HTML
        for match in table_html_pattern.finditer(html_content):
            headers, rows = HTMLParser.parse_html_table(match.group(1))
            if headers or rows:
                elements.append({
                    'start': match.start(),
                    'end': match.end(),
                    'type': 'table',
                    'headers': headers,
                    'rows': rows
                })

        # Collecte des tableaux Markdown (hors des tableaux HTML)
        table_spans = [(e['start'], e['end']) for e in elements]
        for match in table_md_pattern.finditer(html_content):
            if not any(ts <= match.start() and match.end() <= te for ts, te in table_spans):
                headers, rows = HTMLParser.parse_markdown_table(match.group(0))
                if headers or rows:
                    elements.append({
                        'start': match.start(),
                        'end': match.end(),
                        'type': 'table',
                        'headers': headers,
                        'rows': rows
                    })

        # Collecte des images (hors des tableaux)
        occupied_spans = [(e['start'], e['end']) for e in elements]
        for match in img_pattern.finditer(html_content):
            if not any(ts <= match.start() and match.end() <= te for ts, te in occupied_spans):
                img_src = match.group(1) or match.group(3)
                if img_src.startswith('/'):
                    img_url = f"{base_url.rstrip('/')}{img_src}"
                else:
                    img_url = img_src
                elements.append({
                    'start': match.start(),
                    'end': match.end(),
                    'type': 'image',
                    'url': img_url
                })

        # Trier tous les éléments par position
        elements.sort(key=lambda x: x['start'])

        blocks = []
        last_idx = 0

        for elem in elements:
            text_part = html_content[last_idx:elem['start']]
            if text_part.strip():
                markup = HTMLParser.to_markup(text_part)
                if markup.strip():
                    blocks.append({'type': 'text', 'content': markup})

            if elem['type'] == 'image':
                blocks.append({'type': 'image', 'url': elem['url']})
            elif elem['type'] == 'table':
                blocks.append({'type': 'table', 'headers': elem['headers'], 'rows': elem['rows']})

            last_idx = elem['end']

        remaining = html_content[last_idx:]
        if remaining.strip():
            markup = HTMLParser.to_markup(remaining)
            if markup.strip():
                blocks.append({'type': 'text', 'content': markup})

        return blocks
