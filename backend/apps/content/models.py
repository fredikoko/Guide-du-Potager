from django.db import models

class Part(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=1)
    is_premium = models.BooleanField(default=False)
    icon = models.CharField(max_length=50, blank=True, default='sprout')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Partie {self.order}: {self.title}"

class Chapter(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200)
    content = models.TextField()  # HTML or Markdown content
    order = models.IntegerField(default=1)
    is_premium = models.BooleanField(default=False)
    estimated_reading_time = models.IntegerField(default=5)  # minutes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Chapitre {self.order}: {self.title}"

class ChapterImage(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='chapters/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.chapter.title} ({self.caption or self.id})"
