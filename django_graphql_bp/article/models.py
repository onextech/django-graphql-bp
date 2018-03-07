from autoslug import AutoSlugField
from django.db import models
from django.template.defaultfilters import slugify
from uuid_upload_path import upload_to


class Article(models.Model):
    author = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True, related_name='articles')
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    last_modified = models.DateTimeField(auto_now=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    slug = AutoSlugField(always_update=True, populate_from='title', unique=True, unique_with='title')
    subtitle = models.CharField(max_length=255)
    title = models.CharField(max_length=255)

    def save(self, *args: tuple, **kwargs: dict):
        self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)


class ArticleImage(models.Model):
    article = models.ForeignKey('article.Article', on_delete=models.SET_NULL, null=True, related_name='images')
    image = models.ImageField(upload_to=upload_to)
    is_featured = models.BooleanField(default=False)