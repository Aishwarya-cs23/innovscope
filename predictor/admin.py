from django.contrib import admin
from .models import StartupIdea


@admin.register(StartupIdea)
class StartupIdeaAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'idea',
        'result',
        'score',
        'demand',
        'competition',
        'feasibility',
        'created_at'
    )

    search_fields = (
        'idea',
        'result',
        'user__username'
    )

    list_filter = (
        'result',
        'created_at'
    )