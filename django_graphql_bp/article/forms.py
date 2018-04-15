from django_graphql_bp.article.models import Article, ArticleImage
from django_graphql_bp.graphql.forms import UpdateForm


class ArticleForm(UpdateForm):
    class Meta:
        fields = [
            'author',
            'content',
            'is_active',
            'subtitle',
            'title'
        ]
        model = Article


class ArticleImageForm(UpdateForm):
    class Meta:
        fields = [
            'article',
            'image',
            'is_featured'
        ]
        model = ArticleImage


