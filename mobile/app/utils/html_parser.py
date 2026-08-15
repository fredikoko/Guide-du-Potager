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
