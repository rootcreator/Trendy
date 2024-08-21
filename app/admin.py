from django.contrib import admin
from .models import Trend, UserProfile, TrendCategory


@admin.register(Trend)
class TrendAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'date')
    search_fields = ('title', 'description', 'source')
    filter_horizontal = ('categories',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'birth_date')
    search_fields = ('user__username', 'location')


@admin.register(TrendCategory)
class TrendCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
