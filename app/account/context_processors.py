# coding: utf-8

from django.core.context_processors import PermWrapper
from django.conf import settings

def auth(request):
    """ 
    Returns context variables required by apps that use Django's authentication
    system.

    If there is no 'user' attribute in the request, uses AnonymousUser (from
    django.contrib.auth).
    """
    if hasattr(request, 'user'):
        user = request.user
    else:
        from account.models import AnonymousUser
        user = AnonymousUser()
    return {
        'user': user,
#        'messages': user.get_and_delete_messages(),
        'perms': PermWrapper(user),
    }
