import re

class HTMLParser:
    @staticmethod
    def to_markup(html_content):
        if not html_content:
            return ""

        text = html_content

        # Headings
        text = re.sub(r'<h1>(.*?)</h1>', r'\n[size=24][b]\1[/b][/size]\n', text, flags=re.DOTALL)
        text = re.sub(r'<h2>(.*?)</h2>', r'\n[size=22][b]\1[/b][/size]\n', text, flags=re.DOTALL)
        text = re.sub(r'<h3>(.*?)</h3>', r'\n[size=20][b]\1[/b][/size]\n', text, flags=re.DOTALL)
        text = re.sub(r'<h4>(.*?)</h4>', r'\n[size=18][b]\1[/b][/size]\n', text, flags=re.DOTALL)

        # Bold & Italic
        text = re.sub(r'<b>(.*?)</b>', r'[b]\1[/b]', text, flags=re.DOTALL)
        text = re.sub(r'<strong>(.*?)</strong>', r'[b]\1[/b]', text, flags=re.DOTALL)
        text = re.sub(r'<i>(.*?)</i>', r'[i]\1[/i]', text, flags=re.DOTALL)
        text = re.sub(r'<em>(.*?)</em>', r'[i]\1[/i]', text, flags=re.DOTALL)

        # Paragraphs & Lists
        text = re.sub(r'<p>(.*?)</p>', r'\1\n\n', text, flags=re.DOTALL)
        text = re.sub(r'<li>(.*?)</li>', r'  • \1\n', text, flags=re.DOTALL)
        text = re.sub(r'<ul.*?>(.*?)</ul>', r'\1\n', text, flags=re.DOTALL)
        text = re.sub(r'<ol.*?>(.*?)</ol>', r'\1\n', text, flags=re.DOTALL)

        # Strip remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Clean up multi newlines
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
