from django.contrib import admin

from .models import SubscribeAuthor, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active')
    list_filter = ('username', 'email',)


class SubscribeAuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', )
    list_filter = ('author',)


admin.site.register(User, UserAdmin)
admin.site.register(SubscribeAuthor, SubscribeAuthorAdmin)
