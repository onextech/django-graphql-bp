from django.contrib.auth.models import AnonymousUser
from django_graphql_bp.graphql.tests import constructors, cases
from django_graphql_bp.user.tests import UserTestCase
from django_graphql_bp.article.models import Article, ArticleImage


class ArticleTestCase(UserTestCase):
    model_class = Article

    def setUp(self):
        super(ArticleTestCase, self).setUp()
        self.article = Article.objects.create(author=self.user, content='article', subtitle='article', title='article')


class ArticleImageTestCase(ArticleTestCase):
    model_class = ArticleImage

    def setUp(self):
        super(ArticleImageTestCase, self).setUp()
        self.article_image = ArticleImage.objects.create(article=self.article, image='test')


class CreateArticleTestCase(ArticleTestCase, cases.MutationTestCase):
    def get_mutation(self) -> constructors.Mutation:
        return constructors.Mutation('createArticle', {'ok': '', 'validationErrors': ''}, {
            'content': 'createArticle',
            'title': 'createArticle',
            'subtitle': 'createArticle'
        })

    def test_create_article_by_unauthorized_user(self):
        self.create_raised_error_test(self.get_unauthorized_message())

    def test_create_article_by_not_staff(self):
        self.create_raised_error_test(self.get_forbidden_access_message(), self.get_context_value(self.user))

    def test_create_article_by_staff(self):
        self.create_success_test(self.get_context_value(self.staff))


class UpdateArticleTestCase(ArticleTestCase, cases.MutationTestCase):
    def get_mutation(self) -> constructors.Mutation:
        return constructors.Mutation('updateArticle', {'ok': '', 'validationErrors': ''}, {
            'pk': self.article.pk,
            'content': 'updateArticle',
            'title': 'updateArticle',
            'subtitle': 'updateArticle'
        })

    def test_update_article_by_unauthorized_user(self):
        self.update_raised_error_test(self.article, 'title', self.get_unauthorized_message())

    def test_update_article_by_not_staff(self):
        self.update_raised_error_test(
            self.article, 'title', self.get_forbidden_access_message(), self.get_context_value(self.user))

    def test_update_article_by_staff(self):
        self.update_success_test(self.article, 'title', self.get_context_value(self.staff))


class DeleteArticleTestCase(ArticleTestCase, cases.MutationTestCase):
    def get_mutation(self) -> constructors.Mutation:
        return constructors.Mutation('deleteArticle', {'ok': ''}, {'pk': self.article.pk})

    def test_delete_article_by_unauthorized_user(self):
        self.delete_raised_error_test(self.get_unauthorized_message())

    def test_delete_article_by_not_staff(self):
        self.delete_raised_error_test(self.get_forbidden_access_message(), self.get_context_value(self.user))

    def test_delete_article_by_staff(self):
        self.delete_success_test(self.get_context_value(self.staff))


class CreateArticleImageTestCase(ArticleImageTestCase, cases.MutationTestCase):
    def get_mutation(self) -> constructors.Mutation:
        return constructors.Mutation(
            'createArticleImage', {'ok': '', 'validationErrors': ''}, {'article': self.article.pk})

    def test_create_article_image_by_unauthorized_user(self):
        self.create_raised_error_test(
            self.get_unauthorized_message(), self.get_context_value(AnonymousUser(), {'image': 'test.png'}))

    def test_create_article_image_by_not_staff(self):
        self.create_raised_error_test(
            self.get_forbidden_access_message(), self.get_context_value(self.user, {'image': 'test.png'}))

    def test_create_article_image_by_staff(self):
        self.create_success_test(self.get_context_value(self.staff, {'image': 'test.png'}))


class UpdateArticleImageTestCase(ArticleImageTestCase, cases.MutationTestCase):
    def get_mutation(self) -> constructors.Mutation:
        return constructors.Mutation(
            'updateArticleImage', {'ok': '', 'validationErrors': ''}, {
                'pk': self.article_image.pk,
                'article': self.article.pk,
                'isFeatured': True
            })

    def test_update_article_image_by_unauthorized_user(self):
        self.update_raised_error_test(
            self.article_image, 'is_featured', self.get_unauthorized_message(),
            self.get_context_value(AnonymousUser(), {'image': 'test.png'}))

    def test_update_article_image_by_not_staff(self):
        self.update_raised_error_test(
            self.article_image, 'is_featured', self.get_forbidden_access_message(),
            self.get_context_value(self.user, {'image': 'test.png'}))

    def test_update_article_image_by_staff(self):
        self.update_success_test(
            self.article_image, 'is_featured', self.get_context_value(self.staff, {'image': 'test.png'}))


class DeleteArticleImageTestCase(ArticleImageTestCase, cases.MutationTestCase):
    def get_mutation(self) -> constructors.Mutation:
        return constructors.Mutation(
            'deleteArticleImage', {'ok': ''}, {'pk': self.article_image.pk})

    def test_delete_article_image_by_unauthorized_user(self):
        self.delete_raised_error_test(self.get_unauthorized_message())

    def test_delete_article_image_by_not_staff(self):
        self.delete_raised_error_test(self.get_forbidden_access_message(), self.get_context_value(self.user))

    def test_delete_article_image_by_staff(self):
        self.delete_success_test(self.get_context_value(self.staff))


class ArticlesTestCase(ArticleTestCase, cases.QueryTestCase):
    def get_query(self) -> constructors.Query:
        return constructors.Query('articles', {
            'edges': {
                'node': {
                    'pk': ''
                }
            }
        })

    def test_articles(self):
        self.collection_success_test()