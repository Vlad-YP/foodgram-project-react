from django.contrib import admin

from .models import SubscribeAuthor, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active')
    list_filter = ('username', 'email',)


@admin.register(SubscribeAuthor)
class SubscribeAuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', )
    list_filter = ('author',)
