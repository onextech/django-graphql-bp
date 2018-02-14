from django_graphql_bp.article.models import Article, ArticleImage
from django_graphql_bp.graphql.forms import UpdateForm


class ArticleForm(UpdateForm):
    class Meta:
        model = Article
        fields = ['author', 'content', 'is_active', 'subtitle', 'title']


class ArticleImageForm(UpdateForm):
    class Meta:
        model = ArticleImage
        fields = ['article', 'image', 'is_featured']


