from django.forms import ModelForm
from .models import Championship

class CreateChampionshipForm(ModelForm):
    class Meta:
        model= Championship
        fields = ['nombre', 'temporada','num_equipos','fecha_inicio','fecha_fin','imagen']