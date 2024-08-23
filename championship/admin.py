from django.contrib import admin
from .models import Championship, Team, Player

# Register your models here.
admin.site.register(Championship)
admin.site.register(Team)
admin.site.register(Player)