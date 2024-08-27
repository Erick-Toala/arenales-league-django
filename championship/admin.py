from django.contrib import admin
from .models import Championship, Team, Player, PlayerTeam, Day, Match

# Register your models here.
admin.site.register(Championship)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(PlayerTeam)
admin.site.register(Day)
admin.site.register(Match)