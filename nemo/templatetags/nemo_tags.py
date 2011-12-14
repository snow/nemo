from django import template
from django.conf import settings

from ..models import UserProfile

register = template.Library()

@register.simple_tag
def nemo_root():
    return settings.NEMO_URI_ROOT

@register.simple_tag
def project_name():
    return settings.PROJECT_NAME.capitalize()

@register.simple_tag
def user_votes_left(user):
    return UserProfile.objects.filter(user=user).get().votes_left()