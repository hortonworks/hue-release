# -*- coding: utf-8 -*-

from django import template
from django.conf import settings

from social_auth.models import UserSocialAuth
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def get_user_social_auth(context, user, provider):
    provider_dict = {'google-oauth': 'Google',
                     'facebook': 'Facebook'}
    users_accounts = UserSocialAuth.objects.filter(user=user, provider=provider)
    if users_accounts:
        users_account = users_accounts[0]
        if users_account.provider in settings.SOCIAL_AUTH_ENABLED_BACKENDS:
            return mark_safe(
                "<a href='%s' style='color: grey;'>%s disconect</a>" % (reverse(
                    'socialauth_disconnect',
                    kwargs=dict(backend=provider)),
                    provider_dict[provider]))
    return mark_safe("<a href='%s'>%s</a>" % (reverse(
        'socialauth_associate_begin',
        kwargs=dict(backend=provider)),
        provider_dict[provider]))