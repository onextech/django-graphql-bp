from django.db import models


class Article(models.Model):
    author = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True, related_name='articles')
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    last_modified = models.DateTimeField(auto_now=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    slug = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    title = models.CharField(max_length=255)


class ArticleImage(models.Model):
    article = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True, related_name='images')
    image = models.ImageField()
    is_featured = models.BooleanField(default=False)