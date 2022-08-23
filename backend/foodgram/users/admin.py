from django.contrib import admin

from .models import User, SubscribeAuthor

admin.site.register(User)
admin.site.register(SubscribeAuthor)