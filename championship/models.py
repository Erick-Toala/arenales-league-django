import os
import shutil
from django.utils.text import slugify
from django.db import models
from datetime import date
from django.core.exceptions import ValidationError


# Modelo para Campeonato
def championship_image_path(instance, filename):
    # Genera un nombre de archivo basado en el nombre y la temporada del campeonato
    filename_base, filename_ext = os.path.splitext(filename)
    new_filename = f"{slugify(instance.nombre)}_{
        slugify(instance.temporada)}{filename_ext}"
    return f'championship_images/{new_filename}'


class Championship(models.Model):
    CATEGORIA_CHOICES = [
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
    ]
    nombre = models.CharField(max_length=100)  # Nombre del campeonato
    temporada = models.CharField(max_length=20)  # Temporada del campeonato
    num_equipos = models.PositiveIntegerField()  # Número de equipos que participan
    fecha_inicio = models.DateField(blank=True)  # Fecha de inicio del campeonato
    fecha_fin = models.DateField(blank=True)  # Fecha de fin del campeonato
    imagen = models.ImageField(
        upload_to=championship_image_path, blank=True, null=True)
    categoria = models.CharField(max_length=10, choices=CATEGORIA_CHOICES, default='masculino')  # Categoría del campeonato

    def __str__(self):
        return f"{self.nombre} - {self.temporada}"

    class Meta:
        verbose_name = "Championship"
        verbose_name_plural = "Championships"
        ordering = ['-fecha_inicio']  # Ordenar por fecha de inicio descendente

    def save(self, *args, **kwargs):
        # Si la instancia ya existe en la base de datos (actualización), eliminar la imagen antigua
        if self.pk:
            try:
                old_instance = Championship.objects.get(pk=self.pk)
                if old_instance.imagen and old_instance.imagen != self.imagen:
                    # Eliminar el archivo de la imagen anterior
                    if os.path.isfile(old_instance.imagen.path):
                        os.remove(old_instance.imagen.path)
            except Championship.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.imagen:
            if os.path.isfile(self.imagen.path):
                os.remove(self.imagen.path)
        super().delete(*args, **kwargs)

# Modelo Teams
def team_image_path(instance, filename):
    # Genera una ruta de archivo basada en el nombre del equipo y el tipo de archivo
    folder_name = slugify(instance.nombre)
    filename_base, filename_ext = os.path.splitext(filename)
    
    # Asigna un nombre específico según si es el escudo o la foto
    if 'escudo' in filename_base.lower():
        new_filename = f"{folder_name}-escudo{filename_ext}"
    else:
        new_filename = f"{folder_name}-foto{filename_ext}"
        
    return os.path.join('teams_images', folder_name, new_filename)

class Team(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre del equipo
    color = models.CharField(max_length=30)  # Color del equipo
    escudo = models.ImageField(upload_to=team_image_path)  # Imagen del escudo del equipo
    foto = models.ImageField(upload_to=team_image_path, blank=True, null=True)  # Foto opcional del equipo
    campeonato = models.ForeignKey('championship.Championship', related_name='teams', on_delete=models.CASCADE)  # Relación con el campeonato
    
    def __str__(self):
        return f"{self.nombre} - {self.campeonato}"
    
    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"
        ordering = ['nombre']  # Ordenar por nombre ascendente

    def save(self, *args, **kwargs):
        # Si la instancia ya existe en la base de datos (actualización), eliminar las imágenes antiguas si cambian
        if self.pk:
            try:
                old_instance = Team.objects.get(pk=self.pk)
                if old_instance.escudo and old_instance.escudo != self.escudo:
                    if os.path.isfile(old_instance.escudo.path):
                        os.remove(old_instance.escudo.path)
                if old_instance.foto and old_instance.foto != self.foto:
                    if os.path.isfile(old_instance.foto.path):
                        os.remove(old_instance.foto.path)
            except Team.DoesNotExist:
                pass
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Al eliminar un equipo, eliminar la carpeta que contiene las imágenes
        folder_name = slugify(self.nombre)
        folder_path = os.path.join('media', 'teams_images', folder_name)
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)  # Eliminar la carpeta y todo su contenido
        super().delete(*args, **kwargs)
        

# Modelo para Jugadores      
def player_image_path(instance, filename):
    # Genera una ruta de archivo para la foto del jugador
    filename_base, filename_ext = os.path.splitext(filename)
    new_filename = f"{slugify(instance.nombre)}_{slugify(instance.apellido)}{filename_ext}"
    return os.path.join('players_images', new_filename)


class Player(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('suspendido', 'Suspendido'),
    ]

    SEXO_CHOICES = [
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=10, unique=True)
    dorsal = models.PositiveIntegerField(blank=True, null=True)  # No obligatorio
    direccion = models.CharField(max_length=255, blank=True, null=True)  # No obligatorio
    telefono = models.CharField(max_length=15, blank=True, null=True)  # No obligatorio
    fecha_nacimiento = models.DateField()
    foto = models.ImageField(upload_to=player_image_path)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, default='masculino')  # Sexo del jugador

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    @property
    def edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    class Meta:
        verbose_name = "Player"
        verbose_name_plural = "Players"
        ordering = ['nombre', 'apellido']

    def save(self, *args, **kwargs):
        # Si la instancia ya existe en la base de datos (actualización), eliminar la imagen antigua si cambia
        if self.pk:
            try:
                old_instance = Player.objects.get(pk=self.pk)
                if old_instance.foto and old_instance.foto != self.foto:
                    if os.path.isfile(old_instance.foto.path):
                        os.remove(old_instance.foto.path)
            except Player.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Eliminar la imagen si existe
        if self.foto:
            if os.path.isfile(self.foto.path):
                os.remove(self.foto.path)
        super().delete(*args, **kwargs)


class PlayerTeam(models.Model):
    player = models.ForeignKey(Player, related_name='player_teams', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='player_teams', on_delete=models.CASCADE)
    championship = models.ForeignKey(Championship, related_name='player_teams', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('player', 'championship')
        verbose_name = "Player Team"
        verbose_name_plural = "Player Teams"

    def __str__(self):
        return f"{self.player} - {self.team} ({self.championship})"
    

# Modelo para Jornadas
class Day(models.Model):
    campeonato = models.ForeignKey(Championship, related_name='days', on_delete=models.CASCADE)
    numero = models.PositiveIntegerField()  # Número de la jornada dentro del campeonato
    fecha = models.DateField()  # Fecha de la jornada
    lugar = models.CharField(max_length=255, blank=True, null=True) # Lugar donde se juega el partido

    def __str__(self):
        return f"Jornada {self.numero} - {self.campeonato}"

    class Meta:
        verbose_name = "Day"
        verbose_name_plural = "Days"
        ordering = ['fecha', 'numero']

# Modelo para Partidos
class Match(models.Model):
    jornada = models.ForeignKey('Day', related_name='matches', on_delete=models.CASCADE)
    equipo_local = models.ForeignKey('Team', related_name='home_matches', on_delete=models.CASCADE)
    equipo_visitante = models.ForeignKey('Team', related_name='away_matches', on_delete=models.CASCADE)
    goles_local = models.PositiveIntegerField(blank=True, null=True)  # Goles del equipo local
    goles_visitante = models.PositiveIntegerField(blank=True, null=True)  # Goles del equipo visitante
    fecha_hora = models.DateTimeField()  # Fecha y hora del partido
    lugar = models.CharField(max_length=255, blank=True, null=True)  # Lugar donde se juega el partido

    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} - Jornada {self.jornada.numero}"

    def clean(self):
        # Validación para asegurar que un equipo no juegue contra sí mismo
        if self.equipo_local == self.equipo_visitante:
            raise ValidationError("Un equipo no puede jugar contra sí mismo.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matches"
        ordering = ['fecha_hora']