from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import CreateChampionshipForm
from .models import Championship, Team, Player, PlayerTeam, Day, Match
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

# Create your views here.

def home(request):
    return render(request, 'home.html')

def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                # register user
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('championship')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'El usuario ya existe'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Las contraseñas no coinciden'
        })

def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'El usuario o la contraseña es incorrecto'
            })
        else:
            login(request, user)
            return redirect('championship')

@login_required
def championship(request):
    championships = Championship.objects.all()
    return render(request, 'championship.html', {
        'championships': championships
    })

@login_required
def create_championship(request):
    if request.method == 'GET':
        return render(request, 'create_championship.html', {
            'form': CreateChampionshipForm
        })
    else:
        try:
            form = CreateChampionshipForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('championship')
        except ValueError:
            return render(request, 'create_championship.html', {
                'form': CreateChampionshipForm,
                'error': 'Los datos no son válidos.'
            })

@login_required
def championship_detail(request, championship_id):
    if request.method == 'GET':
        championship = get_object_or_404(Championship, pk=championship_id)
        form = CreateChampionshipForm(instance=championship)
        return render(request, 'championship/championship_detail.html', {
            'championship': championship,
            'form': form
        })
    else:
        try:
            championship = get_object_or_404(Championship, pk=championship_id)
            form = CreateChampionshipForm(request.POST, request.FILES, instance=championship)
            if form.is_valid():
                form.save()
                return redirect('championship')
            else:
                return render(request, 'championship/championship_detail.html', {
                    'championship': championship,
                    'form': form,
                    'error': 'Error actualizando campeonato'
                })
        except ValueError:
            return render(request, 'championship/championship_detail.html', {
                'championship': championship,
                'form': form,
                'error': 'Error actualizando campeonato'
            })

@login_required
def championship_delete(request, championship_id):
    championship = get_object_or_404(Championship, pk=championship_id)
    if request.method == 'POST':
        championship.delete()
        return redirect('championship')
    
@login_required
def championship_view(request, championship_id):
    championship = get_object_or_404(Championship, pk=championship_id)
    return render(request, 'championship/championship_view.html', {
        'championship': championship
    })

@login_required
def championship_teams_view(request, championship_id):
    # Obtén el campeonato
    championship = get_object_or_404(Championship, id=championship_id)
    
    # Obtén la consulta de búsqueda y el número de página de los parámetros GET
    search_query = request.GET.get('search_query', '')
    page_number = request.GET.get('page', 1)
    
    # Filtra los equipos basados en la búsqueda y el campeonato
    if search_query:
        teams = Team.objects.filter(campeonato=championship, nombre__icontains=search_query)
    else:
        teams = Team.objects.filter(campeonato=championship)

    # Paginación
    paginator = Paginator(teams, 6)
    page_obj = paginator.get_page(page_number)
    
    # Obtén el equipo seleccionado
    selected_team_id = request.GET.get('team_id')
    selected_team = None
    if selected_team_id:
        selected_team = get_object_or_404(Team, id=selected_team_id)
    
    # Contexto para la plantilla
    context = {
        'championship': championship,
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_team': selected_team,
        'current_page': page_number,  # Añadido para la paginación
    }
    
    return render(request, 'championship/teams/championship_teams_view.html', context)

@login_required
def championship_players_view(request, championship_id):
    # Obtén el campeonato
    championship = get_object_or_404(Championship, id=championship_id)

    # Filtrar objetos PlayerTeam que pertenecen al campeonato actual
    player_teams = PlayerTeam.objects.filter(championship=championship)

    # Extraer jugadores únicos de esos PlayerTeam
    players = Player.objects.filter(id__in=player_teams.values('player')).distinct()

    # Obtener equipos de esos PlayerTeam
    teams = Team.objects.filter(id__in=player_teams.values('team')).distinct()

    # Obtener la consulta de búsqueda del parámetro GET
    search_query = request.GET.get('query', '').strip()

    # Aplicar filtro de búsqueda por nombre o apellido
    if search_query:
        players = players.filter(Q(nombre__icontains=search_query) | Q(apellido__icontains=search_query))

    # Paginación: Mostrar solo 10 jugadores por página
    paginator = Paginator(players, 10)  # Mostrar 10 jugadores por página
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Procesar el filtro de equipo si se ha seleccionado uno
    selected_team_id = request.GET.get('team')
    if selected_team_id:
        players_with_teams = [
            {
                'player': player,
                'team': player_teams.filter(player=player).first().team  # Obtener el equipo del PlayerTeam
            }
            for player in page_obj if player_teams.filter(player=player, team_id=selected_team_id).exists()
        ]
    else:
        # Lista de jugadores con sus respectivos equipos dentro del campeonato actual
        players_with_teams = [
            {
                'player': player,
                'team': player_teams.filter(player=player).first().team  # Obtener el equipo del PlayerTeam
            }
            for player in page_obj
        ]

    # Obtener jugadores sin equipo ni campeonato (jugadores que no están en PlayerTeam)
    players_free = Player.objects.exclude(id__in=player_teams.values('player')).filter(sexo=championship.categoria).distinct()

    # Filtrar jugadores sin equipo ni campeonato con la búsqueda
    if search_query:
        players_free = players_free.filter(Q(nombre__icontains=search_query) | Q(apellido__icontains=search_query))

    # Para los jugadores sin equipo, agregamos el campo de equipo "Sin equipo"
    for player in players_free:
        player.team_name = "Sin equipo"

    return render(request, 'championship/players/players_championship_view.html', {
        'championship': championship,
        'players_with_teams': players_with_teams,
        'players_free': players_free,
        'teams': teams,
        'page_obj': page_obj,  # Para la paginación
        'search_query': search_query,  # Para mantener la búsqueda
        'current_page': page_number,  # Página actual para la paginación
    })

@login_required
def players_team_view(request, championship_id, team_id):
    championship = get_object_or_404(Championship, pk=championship_id)
    team = get_object_or_404(Team, pk=team_id)

    # Obtén la consulta de búsqueda y el número de página de los parámetros GET
    search_query = request.GET.get('search_query', '')
    page_number = request.GET.get('page', 1)

    # Filtra los jugadores basados en la búsqueda y el equipo usando PlayerTeam
    if search_query:
        player_teams = PlayerTeam.objects.filter(
            team=team,
            player__nombre__icontains=search_query
        ).select_related('player')
    else:
        player_teams = PlayerTeam.objects.filter(team=team).select_related('player')

    players = [pt.player for pt in player_teams]

    # Paginación
    paginator = Paginator(players, 8)  # Cambia el número de elementos por página según tu preferencia
    page_obj = paginator.get_page(page_number)

    # Obtén el jugador seleccionado
    selected_player_id = request.GET.get('player_id')
    selected_player = None
    if selected_player_id:
        selected_player = get_object_or_404(Player, id=selected_player_id)

    # Obtener los IDs de los jugadores que ya están registrados en el equipo de este campeonato
    player_teams_in_championship = PlayerTeam.objects.filter(championship=championship).values_list('player_id', flat=True)
    
    # Filtrar jugadores que NO están en el equipo en este campeonato específico
    # También filtrar jugadores que NO tienen ningún registro en PlayerTeam
    # Filtrar jugadores según el género del campeonato
    players_availables = Player.objects.filter(
        Q(player_teams__isnull=True) | ~Q(id__in=player_teams_in_championship),
        sexo=championship.categoria  # Filtra por género del campeonato
    ).distinct()

    # Contexto para la plantilla
    context = {
        'championship': championship,
        'team': team,
        'players_availables': players_availables,
        'page_obj': page_obj,
        'search_query': search_query,
        'current_page': page_number,  # Añadido para la paginación
        'selected_player': selected_player,
    }

    return render(request, 'championship/players/players_team_view.html', context)

@login_required
def create_teams(request, championship_id):
    championship = get_object_or_404(Championship, pk=championship_id)

    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.POST.get('nombre')
        color = request.POST.get('color')
        escudo = request.FILES.get('escudo')
        foto = request.FILES.get('foto')

        # Crear el nuevo equipo
        new_team = Team(
            nombre=nombre,
            color=color,
            escudo=escudo,
            foto=foto,
            campeonato=championship
        )
        new_team.save()

        # Redirigir a la vista de equipos del campeonato
        return redirect('championship_teams_view', championship_id=championship.id)

    return render(request, 'championship/admin/team_form.html', {
        'championship': championship
    })
    
@login_required
def create_players(request, championship_id, team_id):
    championship = get_object_or_404(Championship, id=championship_id)
    team = get_object_or_404(Team, id=team_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        cedula = request.POST.get('cedula')
        dorsal = request.POST.get('dorsal')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        foto = request.FILES.get('foto')

        # Verificar si la cédula ya existe
        if Player.objects.filter(cedula=cedula).exists():
            messages.error(request, 'El jugador con esta cédula ya existe.')
            return render(request, 'championship/admin/player_create_form.html', {
                'team': team,
                'championship': championship,
                'cedula': cedula  # Pasar el valor de cédula para que el usuario no lo pierda
            })

        # Determinar el sexo del jugador basado en la categoría del campeonato
        if championship.categoria == 'masculino':
            sexo = 'masculino'
        else:
            sexo = 'femenino'

        # Crear el objeto Player
        player = Player(
            nombre=nombre,
            apellido=apellido,
            cedula=cedula,
            dorsal=dorsal,
            direccion=direccion,
            telefono=telefono,
            fecha_nacimiento=fecha_nacimiento,
            foto=foto,
            sexo=sexo  # Asignar el sexo determinado
        )
        player.save()

        # Crear la relación en PlayerTeam
        player_team = PlayerTeam(
            player=player,
            team=team,
            championship=championship
        )
        player_team.save()

        messages.success(request, 'Jugador creado exitosamente.')
        return redirect('players_team_view', championship_id=championship.id, team_id=team.id)

    return render(request, 'championship/admin/player_create_form.html', {
        'team': team,
        'championship': championship
    })
    
def validate_cedula(request):
    if request.method == 'GET':
        cedula = request.GET.get('cedula')
        exists = Player.objects.filter(cedula=cedula).exists()
        return JsonResponse({'exists': exists})
    
@login_required
def respaldo(request, championship_id, team_id):
    # Obtener el campeonato y el equipo seleccionados
    championship = get_object_or_404(Championship, id=championship_id)
    team = get_object_or_404(Team, id=team_id)

    # Obtener los IDs de los jugadores que ya están registrados en el equipo de este campeonato
    player_teams_in_championship = PlayerTeam.objects.filter(championship=championship).values_list('player_id', flat=True)
    
    # Filtrar jugadores que NO están en el equipo en este campeonato específico
    # También filtrar jugadores que NO tienen ningún registro en PlayerTeam
    jugadores_disponibles = Player.objects.filter(
        Q(player_teams__isnull=True) | ~Q(id__in=player_teams_in_championship)
    ).distinct()

    context = {
        'championship': championship,
        'team': team,
        'jugadores_disponibles': jugadores_disponibles,
    }
    return render(request, 'championship/admin/players/player_add_existing_form.html', context)

@login_required
def add_existing_players_view(request, championship_id, team_id):
    championship = get_object_or_404(Championship, id=championship_id)
    team = get_object_or_404(Team, id=team_id)
    
    # Obtener el jugador a agregar del parámetro GET
    player_id = request.GET.get('player_id')
    if player_id:
        player = get_object_or_404(Player, id=player_id)
        
        # Verificar si el jugador ya está en el equipo en este campeonato
        if PlayerTeam.objects.filter(player=player, team=team, championship=championship).exists():
            messages.warning(request, f'El jugador {player.nombre} {player.apellido} ya está en este equipo.')
        else:
            # Añadir jugador al equipo
            PlayerTeam.objects.create(player=player, team=team, championship=championship)
            messages.success(request, f'El jugador {player.nombre} {player.apellido} ha sido añadido al equipo.')
    
    # Redirigir de nuevo a la vista de jugadores del equipo
    return redirect('players_team_view', championship_id=championship_id, team_id=team_id)

#Partidos (matches)
def matches_championship_view(request, championship_id):
    # Obtener el campeonato específico
    championship = get_object_or_404(Championship, pk=championship_id)
    
    # Obtener todas las jornadas del campeonato
    days = Day.objects.filter(campeonato=championship).order_by('numero')
    
    # Obtener la jornada seleccionada desde el parámetro GET, si existe
    selected_day_id = request.GET.get('day')
    if selected_day_id:
        selected_day = get_object_or_404(Day, pk=selected_day_id, campeonato=championship)
    else:
        # Si no se selecciona una jornada, elegir la primera jornada por defecto
        selected_day = days.first()

    # Obtener los partidos de la jornada seleccionada
    matches = Match.objects.filter(jornada=selected_day).order_by('fecha_hora')
    
    # Paginación de las jornadas (puedes ajustar el número de jornadas por página)
    paginator = Paginator(days, 1)  # Muestra una jornada por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Renderizar la plantilla con los datos necesarios
    return render(request, 'championship/matches/matches_campionship_view.html', {
        'championship': championship,
        'days': days,
        'selected_day': selected_day,
        'matches': matches,
        'page_obj': page_obj,
    })

#Jornadas (Days)

#Obtener las jornadas de un campeonato, los partidos de esa jornada, y añadir jornadas a ese campeonato    
@login_required
def days_matches_championship_view(request, championship_id):
    championship = get_object_or_404(Championship, pk=championship_id)
    return render(request, 'championship/admin/days/days_matches_championship_view.html', {
        'championship': championship
    })