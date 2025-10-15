from urllib.parse import parse_qs
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

@sync_to_async
def get_user_from_session(session_key):
    """Retrieve user from session key."""
    try:
        session = Session.objects.get(session_key=session_key)
        user_id = session.get_decoded().get('_auth_user_id')
        return get_user_model().objects.get(id=user_id)
    except (Session.DoesNotExist, get_user_model().DoesNotExist):
        return AnonymousUser()

async def query_auth_middleware(inner, scope, receive, send):
    """Middleware function to authenticate WebSocket connections."""
    query_string = parse_qs(scope["query_string"].decode())
    session_key = query_string.get("sessionid", [None])[0]
    if session_key:
        scope["user"] = await get_user_from_session(session_key)
    else:
        scope["user"] = AnonymousUser()

    return await inner(scope, receive, send)

def QueryAuthMiddlewareStack(inner):
    """Wrapper function for middleware stack."""
    return AuthMiddlewareStack(lambda scope, receive, send: query_auth_middleware(inner, scope, receive, send))

