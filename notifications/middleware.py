from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from django.contrib.auth.models import AnonymousUser


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        from django.contrib.auth import get_user_model 

        User = get_user_model()

        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token")

        if token:
            try:
                UntypedToken(token[0])
                decoded_data = jwt_decode(
                    token[0],
                    settings.SECRET_KEY,
                    algorithms=["HS256"],
                )
                user = await database_sync_to_async(User.objects.get)(
                    id=decoded_data["user_id"]
                )
                print(f"DEBUG: Middleware found user {user.id}")
                scope["user"] = user

            except (InvalidToken, TokenError, User.DoesNotExist) as e:
                print(f"DEBUG: Middleware Auth Failed: {e}")
                scope["user"] = AnonymousUser()
        else:
            print("DEBUG: Middleware: No token provided")
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
