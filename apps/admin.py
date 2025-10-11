# register user model in admin site
from django.contrib import admin

from .users.models import User

admin.site.register(User)
