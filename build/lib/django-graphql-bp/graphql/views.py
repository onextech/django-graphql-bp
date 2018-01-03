from app.graphql.middleware import CookieMiddleware
from graphene_django.views import GraphQLView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie


class PrivateGraphQLView(UserPassesTestMixin, GraphQLView):
    def test_func(self):
        user = self.request.user
        if settings.DEBUG:
            return True
        return user.is_authenticated and user.is_superuser

    def dispatch(self, request, *args, **kwargs):
        messages.error(request, _('403 Forbidden Access'))
        return super(PrivateGraphQLView, self).dispatch(request, *args, **kwargs)

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        response = super(UserPassesTestMixin, self).dispatch(request, *args, **kwargs)
        # Set response cookies defined in middleware
        if response.status_code == 200:
            try:
                response_cookies = getattr(request, CookieMiddleware.MIDDLEWARE_COOKIES)
            except:
                pass
            else:
                for cookie in response_cookies:
                    response.set_cookie(cookie.get('key'), cookie.get('value'), **cookie.get('kwargs'))
        return response

    def parse_body(self, request):
        data = super(UserPassesTestMixin, self).parse_body(request)
        content_type = self.get_content_type(request)
        if content_type in ['application/x-www-form-urlencoded', 'multipart/form-data'] and self.batch:
            # Handle file batching for FormData content_type by returning QueryDict in array
            return [request.POST]
        return data
