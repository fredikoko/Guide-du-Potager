from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.content.rendering import ContentRenderer, render_content
from apps.content.templatetags.content_markup import render_content_filter
from apps.blog.models import Category, Post
from apps.content.models import Part, Chapter
from apps.blog.serializers import PostDetailSerializer
from apps.content.serializers import ChapterDetailSerializer

User = get_user_model()

class ContentRendererTestCase(TestCase):
    def test_markdown_headings(self):
        md = "# Titre 1\n\n## Titre 2\n\n### Titre 3"
        html = render_content(md)
        self.assertIn("<h1>Titre 1</h1>", html)
        self.assertIn("<h2>Titre 2</h2>", html)
        self.assertIn("<h3>Titre 3</h3>", html)

    def test_markdown_headings_without_blank_lines(self):
        # Cas réel où les sous-titres ### ne sont séparés que par un simple saut de ligne \n
        md = (
            "## 1. Le sur-arrosage en saison des pluies\n"
            "### Pourquoi elle est fréquente en climat tropical\n"
            "Quand il fait chaud, on imagine que les plantes ont tout le temps soif.\n"
            "### Conséquences concrètes\n"
            "Asphyxie des racines."
        )
        html = render_content(md)
        self.assertIn("<h2>1. Le sur-arrosage en saison des pluies</h2>", html)
        self.assertIn("<h3>Pourquoi elle est fréquente en climat tropical</h3>", html)
        self.assertIn("<h3>Conséquences concrètes</h3>", html)
        self.assertNotIn("###", html)
        self.assertNotIn("##", html)

    def test_markdown_headings_with_spaces_and_trailing_hashes(self):
        md = "   ### Sous-titre avec espaces ###\nTexte sous le titre"
        html = render_content(md)
        self.assertIn("<h3>Sous-titre avec espaces</h3>", html)
        self.assertNotIn("###", html)

    def test_markdown_headings_wrapped_in_html_tags(self):
        html_input = "<p>### Titre dans paragraphe</p>"
        rendered = render_content(html_input)
        self.assertIn("<h3>Titre dans paragraphe</h3>", rendered)
        self.assertNotIn("###", rendered)

    def test_markdown_inlines(self):
        md = "Un texte avec du **gras**, de l'*italique*, du `code` et ~~barré~~."
        html = render_content(md)
        self.assertIn("<strong>gras</strong>", html)
        self.assertIn("<em>italique</em>", html)
        self.assertIn("<code", html)
        self.assertIn("code</code>", html)
        self.assertIn("<del>barré</del>", html)

    def test_markdown_links_and_images(self):
        md = "Voici un [lien](https://example.com) et une image ![Logo](/media/logo.png)."
        html = render_content(md)
        self.assertIn('<a href="https://example.com"', html)
        self.assertIn('lien</a>', html)
        self.assertIn('<img src="/media/logo.png" alt="Logo"', html)

    def test_markdown_lists(self):
        md = "- Puce 1\n- Puce 2\n- Puce 3"
        html = render_content(md)
        self.assertIn("<ul>", html)
        self.assertIn("<li>Puce 1</li>", html)
        self.assertIn("<li>Puce 2</li>", html)
        self.assertIn("</ul>", html)

        md_ord = "1. Premier\n2. Deuxième"
        html_ord = render_content(md_ord)
        self.assertIn("<ol>", html_ord)
        self.assertIn("<li>Premier</li>", html_ord)
        self.assertIn("</ol>", html_ord)

    def test_markdown_table(self):
        md = "| Légume | Saison |\n| --- | --- |\n| Tomate | Chaude |\n| Carotte | Fraîche |"
        html = render_content(md)
        self.assertIn("<table", html)
        self.assertIn("<th>Légume</th>", html)
        self.assertIn("<td>Tomate</td>", html)

    def test_markdown_blockquote(self):
        md = "> La terre nourricière mérite du compost mûr."
        html = render_content(md)
        self.assertIn("<blockquote>", html)
        self.assertIn("La terre nourricière", html)

    def test_markdown_fenced_code_block(self):
        md = "```python\ndef arroser():\n    print('arrosage')\n```"
        html = render_content(md)
        self.assertIn('<pre><code class="language-python">', html)
        self.assertIn("def arroser():", html)

    def test_html_passthrough_and_preservation(self):
        html_raw = '<div class="alert alert-success"><span style="color:#47C26B;">Bio & Naturel</span></div>'
        rendered = render_content(html_raw)
        self.assertIn('<div class="alert alert-success">', rendered)
        self.assertIn('color:#47C26B;', rendered)

    def test_mixed_markdown_and_html(self):
        mixed = (
            "## Guide de fertilisation\n\n"
            "<div class=\"bg-green-50 p-4\">\n"
            "<strong>Important :</strong> Bien doser l'azote.\n"
            "</div>\n\n"
            "- Apport de compost au repiquage\n"
            "- Arrosage régulier"
        )
        rendered = render_content(mixed)
        self.assertIn("<h2>Guide de fertilisation</h2>", rendered)
        self.assertIn('<div class="bg-green-50 p-4">', rendered)
        self.assertIn("<strong>Important :</strong>", rendered)
        self.assertIn("<ul>", rendered)
        self.assertIn("<li>Apport de compost au repiquage</li>", rendered)

    def test_plain_text_with_linebreaks(self):
        text = "Premier paragraphe.\nAvec une deuxième ligne.\n\nDeuxième paragraphe indépendant."
        rendered = render_content(text)
        self.assertIn("<p>Premier paragraphe.<br/>\nAvec une deuxième ligne.</p>", rendered)
        self.assertIn("<p>Deuxième paragraphe indépendant.</p>", rendered)

    def test_template_filter(self):
        filtered = render_content_filter("### Sous-titre")
        self.assertIn("<h3>Sous-titre</h3>", filtered)


class PostAndChapterModelRenderingTestCase(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            email='testauthor@potager.fr',
            username='testauthor',
            password='Password123!'
        )
        self.category = Category.objects.create(name="Technique", slug="technique")
        self.part = Part.objects.create(title="Partie 1", order=1)

        self.post = Post.objects.create(
            title="Culture du piment habanero",
            slug="culture-piment-habanero",
            author=self.author,
            category=self.category,
            excerpt="Tout savoir sur le piment.",
            content="## Semis et repiquage\n\nLe piment apprécie la **forte chaleur**.\n\n- Semis en pépinière\n- Repiquage à 45 jours",
            is_published=True
        )

        self.chapter = Chapter.objects.create(
            part=self.part,
            title="Gestion des ravageurs sahéliens",
            order=1,
            content="## Ravageurs majeurs\n\nSurveiller les **acariens** et les mouches blanches.\n\n> Traiter à l'huile de neem le soir.",
        )

    def test_post_rendered_content_property(self):
        rendered = self.post.rendered_content
        self.assertIn("<h2>Semis et repiquage</h2>", rendered)
        self.assertIn("<strong>forte chaleur</strong>", rendered)
        self.assertIn("<ul>", rendered)
        self.assertIn("<li>Semis en pépinière</li>", rendered)
        # Content remains raw for editing in admin
        self.assertEqual(self.post.content, "## Semis et repiquage\n\nLe piment apprécie la **forte chaleur**.\n\n- Semis en pépinière\n- Repiquage à 45 jours")

    def test_chapter_rendered_content_property(self):
        rendered = self.chapter.rendered_content
        self.assertIn("<h2>Ravageurs majeurs</h2>", rendered)
        self.assertIn("<strong>acariens</strong>", rendered)
        self.assertIn("<blockquote>", rendered)
        self.assertIn("Traiter à l'huile de neem", rendered)

    def test_post_detail_serializer(self):
        serializer = PostDetailSerializer(self.post)
        data = serializer.data
        self.assertIn("<h2>Semis et repiquage</h2>", data['rendered_content'])
        self.assertIn("## Semis et repiquage", data['content'])

    def test_chapter_detail_serializer(self):
        serializer = ChapterDetailSerializer(self.chapter)
        data = serializer.data
        self.assertIn("<h2>Ravageurs majeurs</h2>", data['rendered_content'])
        self.assertIn("## Ravageurs majeurs", data['content'])

    def test_web_views_render_rich_content(self):
        # Web blog detail
        res_blog = self.client.get(reverse('web:blog_detail', kwargs={'slug': self.post.slug}))
        self.assertEqual(res_blog.status_code, 200)
        self.assertContains(res_blog, "<h2>Semis et repiquage</h2>")
        self.assertContains(res_blog, "<strong>forte chaleur</strong>")

        # Web chapter detail
        res_chap = self.client.get(reverse('web:chapter_detail', kwargs={'chapter_id': self.chapter.id}))
        self.assertEqual(res_chap.status_code, 200)
        self.assertContains(res_chap, "<h2>Ravageurs majeurs</h2>")
        self.assertContains(res_chap, "<strong>acariens</strong>")
