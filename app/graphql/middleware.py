from datetime import datetime
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
from rest_framework.request import Request
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings


def get_user_jwt(request):
    """
    Replacement for django session auth get_user & auth.get_user
     JSON Web Token authentication. Inspects the token for the user_id,
     attempts to get that user from the DB & assigns the user on the
     request object. Otherwise it defaults to AnonymousUser.

    This will work with existing decorators like LoginRequired  ;)

    Returns: instance of user object or AnonymousUser object
    """
    user = None
    try:
        user_jwt = JSONWebTokenAuthentication().authenticate(Request(request))
        if user_jwt is not None:
            # store the first part from the tuple (user, obj)
            user = user_jwt[0]
            user.is_authenticated = True
    except:
        pass
    return user or AnonymousUser()


class JWTAuthenticationMiddleware(object):
    """ Middleware for authenticating JSON Web Tokens in Authorize Header """

    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: get_user_jwt(request))


class CookieMiddleware(object):
    MIDDLEWARE_COOKIES = 'middleware_cookies'

    def resolve(self, next, root, args, context, info):
        """
        Set cookies based on the name/type of the GraphQL operation
        :param next:
        :param root:
        :param args:
        :param context:
        :param info:
        :return:
        @examples
            info.operation.operation == 'mutation'
            info.operation.name.value == 'currentUserMutation'
            info.field_name == 'currentUser':
        """

        if info.field_name in ['loginUser', 'createUser']:
            try:
                from django.contrib.auth import get_user_model, forms
                from saleor.userprofile.schema import get_token_from_user
                User = get_user_model()

                input = args.get('input')
                data = {
                    'username': input.get(User.USERNAME_FIELD, ''),
                    'password': input.get('password')
                }

                if info.field_name == 'createUser':
                    from saleor.userprofile.forms import UserCreationForm
                    data['email'] = data['username']
                    form = UserCreationForm(data)
                    form.is_valid()
                    # Needs to save with commit False, as actual save to db
                    # is made after this middleware completes
                    user = form.save(False)

                if info.field_name == 'loginUser':
                    form = forms.AuthenticationForm(context, data=data)
                    form.is_valid()
                    form.clean()
                    user = form.get_user()

                token = get_token_from_user(user)
            except:
                pass
            else:
                expiration = (datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA)
                jwt_cookie = self.define_middleware_cookies(api_settings.JWT_AUTH_COOKIE, token, expires=expiration,
                                                            httponly=True)
                self.set_middleware_cookies(context, jwt_cookie)

        if info.field_name == 'logoutUser':
            try:
                context.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
            except:
                pass
            else:
                jwt_cookie = self.define_middleware_cookies(api_settings.JWT_AUTH_COOKIE, '')
                self.set_middleware_cookies(context, jwt_cookie)

        return next(root, args, context, info)

    @staticmethod
    def define_middleware_cookies(key, value='', **kwargs):
        """
        Generates the shape required for setting a cookie later
        :param key: string
        :param value: any
        :param kwargs: dict
        :return: dict
        @example:
            # Simple example, name and value of cookie
            my_cookie = define_middleware_cookies('MY_COOKIE', 'foo')
            # Additional kwargs as defined by Django.http.response.set_cookie
            my_cookie_2 = define_middleware_cookies('MY_COOKIE_2', 'bar', httponly=True, secure=True)
        """
        return {'key': key, 'value': value, 'kwargs': kwargs}

    @staticmethod
    def set_middleware_cookies(context, *cookies):
        """
        Sets the cookies in the context to pass on
        :param context: dict
        :param cookies: dict
        :return: dict
        @example:
            # set single cookie
            set_middleware_cookies(context, my_cookie)
            # or many cookies
            set_middleware_cookies(context, my_cookie, my_cookie_2)
        """
        setattr(context, CookieMiddleware.MIDDLEWARE_COOKIES, [*cookies])
        return context
