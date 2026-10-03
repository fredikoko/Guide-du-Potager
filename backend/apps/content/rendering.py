import re
import html

class ContentRenderer:
    """
    Moteur de rendu universel en pur Python sans dépendance externe.
    Prend en charge simultanément :
    - La syntaxe Markdown (titres #, gras **, italique *, code, listes, tableaux, citations, liens, images)
    - Les balises HTML natives (<div>, <p>, <strong>, <span> avec classes Tailwind, <img>, etc.)
    - Le texte brut avec sauts de lignes et mise en forme automatique
    """

    @classmethod
    def render(cls, text):
        if not text:
            return ""

        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 1. Extraction des blocs de code protégés ```lang ... ``` et ~~~ ... ~~~
        code_blocks = []
        def save_code_block(match):
            idx = len(code_blocks)
            lang = (match.group(1) or '').strip()
            code_content = match.group(2)
            escaped_code = html.escape(code_content.strip('\n'))
            lang_attr = f' class="language-{lang}"' if lang else ''
            code_blocks.append(f'<pre><code{lang_attr}>{escaped_code}</code></pre>')
            return f"<!--CODE_BLOCK_{idx}-->"

        pattern_fenced = re.compile(r'^(?:```|~~~)([a-zA-Z0-9_-]*)\n(.*?)\n(?:```|~~~)$', re.MULTILINE | re.DOTALL)
        text = pattern_fenced.sub(save_code_block, text)

        # 1.5 Isolation des titres et séparateurs Markdown pour éviter qu'ils ne soient fusionnés
        text = re.sub(r'([^\n])\n([ \t]{0,3}#{1,6}(?:[ \t]+.*)?)$', r'\1\n\n\2', text, flags=re.MULTILINE)
        text = re.sub(r'^([ \t]{0,3}#{1,6}(?:[ \t]+.*)?)\n([^\n])', r'\1\n\n\2', text, flags=re.MULTILINE)
        text = re.sub(r'([^\n])\n([ \t]{0,3}(?:-{3,}|\*{3,}|_{3,}))\n', r'\1\n\n\2\n', text, flags=re.MULTILINE)

        # 2. Découpage en blocs logiques séparés par au moins 2 sauts de ligne
        raw_blocks = re.split(r'\n{2,}', text)
        rendered_blocks = []

        for block in raw_blocks:
            block = block.strip()
            if not block:
                continue

            # Si c'est un placeholder de code block
            if block.startswith("<!--CODE_BLOCK_") and block.endswith("-->"):
                rendered_blocks.append(block)
                continue

            # Traitement selon le type de bloc
            rendered = cls._render_block(block)
            if rendered:
                rendered_blocks.append(rendered)

        result = "\n\n".join(rendered_blocks)

        # 3. Réinjection des blocs de code
        for idx, cb in enumerate(code_blocks):
            result = result.replace(f"<!--CODE_BLOCK_{idx}-->", cb)

        return result

    @classmethod
    def _render_block(cls, block):
        lines = block.split('\n')
        first_line = lines[0].strip()

        # A. Ligne horizontale Markdown (---, ***, ___)
        if re.match(r'^[ \t]{0,3}(?:-{3,}|\*{3,}|_{3,})$', first_line) and len(lines) == 1:
            return '<hr class="my-6 border-gray-200" />'

        # B. Titres Markdown uniques (^#{1,6}\s*)
        header_match = re.match(r'^[ \t]{0,3}(#{1,6})\s*(.+?)(?:\s*#+)?$', first_line)
        if header_match and len(lines) == 1:
            level = len(header_match.group(1))
            title_text = cls._render_inlines(header_match.group(2).strip())
            return f"<h{level}>{title_text}</h{level}>"

        # C. Si le bloc contient des titres Markdown mélangés avec des paragraphes
        if any(re.match(r'^[ \t]{0,3}#{1,6}(?:\s+.*)?$', l.strip()) for l in lines) and not first_line.startswith('<'):
            sub_rendered = []
            current_para = []
            for l in lines:
                hm = re.match(r'^[ \t]{0,3}(#{1,6})\s*(.*?)(?:\s*#+)?$', l.strip())
                if hm:
                    if current_para:
                        para_content = "<br/>\n".join([cls._render_inlines(pl) for pl in current_para])
                        sub_rendered.append(f"<p>{para_content}</p>")
                        current_para = []
                    lvl = len(hm.group(1))
                    tit = cls._render_inlines(hm.group(2).strip())
                    sub_rendered.append(f"<h{lvl}>{tit}</h{lvl}>")
                else:
                    current_para.append(l)
            if current_para:
                para_content = "<br/>\n".join([cls._render_inlines(pl) for pl in current_para])
                sub_rendered.append(f"<p>{para_content}</p>")
            return "\n\n".join(sub_rendered)

        # D. Citation Markdown (> ...)
        if all(re.match(r'^>\s?', line) for line in lines):
            quote_lines = [re.sub(r'^>\s?', '', line) for line in lines]
            quote_content = cls.render("\n".join(quote_lines))
            return f"<blockquote>{quote_content}</blockquote>"

        # E. Tableaux Markdown (| col 1 | col 2 |)
        if cls._is_markdown_table(lines):
            return cls._render_markdown_table(lines)

        # F. Listes (à puces - * + ou ordonnées 1. 2.)
        if cls._is_list(lines):
            return cls._render_list(lines)

        # G. Si le bloc commence par une balise HTML de bloc reconnue
        html_block_pattern = re.compile(
            r'^<(?:p|div|table|thead|tbody|tfoot|tr|th|td|blockquote|section|article|header|footer|aside|nav|details|summary|figure|figcaption|ul|ol|h[1-6]|hr|iframe)\b',
            re.IGNORECASE
        )
        if html_block_pattern.match(first_line):
            # Convertir d'éventuels titres Markdown enveloppés dans des balises <p> ou <div>
            processed_html = re.sub(
                r'<(?:p|div)[^>]*>\s*(#{1,6})\s*(.*?)(?:\s*#+)?\s*</(?:p|div)>',
                lambda m: f"<h{len(m.group(1))}>{cls._render_inlines(m.group(2).strip())}</h{len(m.group(1))}>",
                block, flags=re.IGNORECASE
            )
            return cls._render_inlines(processed_html)

        # H. Paragraphe standard de texte
        para_lines = [cls._render_inlines(line) for line in lines]
        para_content = "<br/>\n".join(para_lines)
        return f"<p>{para_content}</p>"

    @classmethod
    def _is_markdown_table(cls, lines):
        if len(lines) < 2:
            return False
        # Doit avoir au moins une ligne d'en-tête et une ligne de séparateur (| --- |)
        if '|' not in lines[0] or '|' not in lines[1]:
            return False
        clean_sep = lines[1].strip()
        parts = [p.strip() for p in clean_sep.strip('|').split('|')]
        return len(parts) >= 1 and all(bool(re.match(r'^:?-+:?$', p)) for p in parts if p)

    @classmethod
    def _render_markdown_table(cls, lines):
        def parse_row(row_str):
            cells = [c.strip() for c in row_str.strip().strip('|').split('|')]
            return cells

        headers = parse_row(lines[0])
        # Ligne de séparation (lines[1])
        body_rows = [parse_row(l) for l in lines[2:] if l.strip()]

        out = ['<div class="overflow-x-auto my-4">', '<table class="min-w-full">', '<thead>', '<tr>']
        for h in headers:
            out.append(f'<th>{cls._render_inlines(h)}</th>')
        out.extend(['</tr>', '</thead>', '<tbody>'])

        for row in body_rows:
            out.append('<tr>')
            for idx, c in enumerate(row):
                cell_content = cls._render_inlines(c)
                out.append(f'<td>{cell_content}</td>')
            out.append('</tr>')

        out.extend(['</tbody>', '</table>', '</div>'])
        return "".join(out)

    @classmethod
    def _is_list(cls, lines):
        return any(re.match(r'^\s*(?:[-*+]|\d+\.)\s+', l) for l in lines)

    @classmethod
    def _render_list(cls, lines):
        items = []
        is_ordered = bool(re.match(r'^\s*\d+\.\s+', lines[0]))

        current_item = []
        for line in lines:
            list_match = re.match(r'^\s*(?:[-*+]|\d+\.)\s+(.+)$', line)
            if list_match:
                if current_item:
                    items.append("\n".join(current_item))
                current_item = [list_match.group(1)]
            else:
                if current_item:
                    current_item.append(line.strip())
                else:
                    current_item = [line.strip()]

        if current_item:
            items.append("\n".join(current_item))

        tag = "ol" if is_ordered else "ul"
        out = [f"<{tag}>"]
        for item in items:
            out.append(f"<li>{cls._render_inlines(item)}</li>")
        out.append(f"</{tag}>")
        return "".join(out)

    @classmethod
    def _render_inlines(cls, text):
        if not text:
            return ""

        # 1. Images Markdown : ![alt](src "title") ou ![alt](src)
        def replace_img(m):
            alt = m.group(1) or ""
            src = m.group(2) or ""
            title = m.group(3)
            title_attr = f' title="{title}"' if title else ''
            return f'<img src="{src}" alt="{alt}"{title_attr} class="rounded-xl shadow-sm max-w-full h-auto my-3" />'

        text = re.sub(r'!\[(.*?)\]\((.*?)(?:\s+"(.*?)")?\)', replace_img, text)

        # 2. Liens Markdown : [texte](url "title") ou [texte](url)
        def replace_link(m):
            link_text = m.group(1) or ""
            url = m.group(2) or ""
            title = m.group(3)
            title_attr = f' title="{title}"' if title else ''
            return f'<a href="{url}"{title_attr} class="text-[#3D7A42] hover:text-[#1E592E] underline font-semibold">{link_text}</a>'

        text = re.sub(r'(?<!!)\[(.*?)\]\((.*?)(?:\s+"(.*?)")?\)', replace_link, text)

        # 3. Code en ligne : `code`
        text = re.sub(
            r'`([^`]+)`',
            r'<code class="bg-gray-100 text-[#1E592E] px-1.5 py-0.5 rounded text-sm font-mono">\1</code>',
            text
        )

        # 4. Gras et Italique combinés : ***texte*** ou ___texte___
        text = re.sub(r'(?:\*\*\*|___)(.*?)(?:\*\*\*|___)', r'<strong><em>\1</em></strong>', text)

        # 5. Gras : **texte** ou __texte__
        text = re.sub(r'(?:\*\*|__)(.*?)(?:\*\*|__)', r'<strong>\1</strong>', text)

        # 6. Italique : *texte* ou _texte_ (attention à ne pas attraper à l'intérieur des mots)
        text = re.sub(r'(?<![a-zA-Z0-9])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![a-zA-Z0-9])', r'<em>\1</em>', text)
        text = re.sub(r'(?<![a-zA-Z0-9])_(?!\s)([^_\n]+?)(?<!\s)_(?![a-zA-Z0-9])', r'<em>\1</em>', text)

        # 7. Texte barré : ~~texte~~
        text = re.sub(r'~~(.*?)~~', r'<del>\1</del>', text)

        return text

def render_content(raw_text):
    """Fonction utilitaire principale pour le rendu de contenu riche."""
    return ContentRenderer.render(raw_text)
