import os
import shutil
from django.utils.text import slugify
from django.db import models

# Create your models here.

# Modelo para Campeonato


def championship_image_path(instance, filename):
    # Genera un nombre de archivo basado en el nombre y la temporada del campeonato
    filename_base, filename_ext = os.path.splitext(filename)
    new_filename = f"{slugify(instance.nombre)}_{
        slugify(instance.temporada)}{filename_ext}"
    return f'championship_images/{new_filename}'


class Championship(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre del campeonato
    temporada = models.CharField(max_length=20)  # Temporada del campeonato
    num_equipos = models.PositiveIntegerField()  # Número de equipos que participan
    # Fecha de inicio del campeonato
    fecha_inicio = models.DateField(blank=True)
    fecha_fin = models.DateField(blank=True)  # Fecha de fin del campeonato
    imagen = models.ImageField(
        upload_to=championship_image_path, blank=True, null=True)

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
        return self.nombre
    
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
        folder_path = os.path.join('media', 'teams', folder_name)
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

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=10, unique=True)
    dorsal = models.PositiveIntegerField(blank=True, null=True)  # No obligatorio
    direccion = models.CharField(max_length=255, blank=True, null=True)  # No obligatorio
    telefono = models.CharField(max_length=15, blank=True, null=True)  # No obligatorio
    fecha_nacimiento = models.DateField()
    foto = models.ImageField(upload_to=player_image_path, blank=True, null=True)  # No obligatorio
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    equipo = models.ForeignKey('Team', related_name='players', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.equipo.nombre}"

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
        if self.foto:
            if os.path.isfile(self.foto.path):
                os.remove(self.foto.path)
        super().delete(*args, **kwargs)