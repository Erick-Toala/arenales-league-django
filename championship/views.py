from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import CreateChampionshipForm
from .models import Championship, Team, Player, PlayerTeam
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse


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

    # Contexto para la plantilla
    context = {
        'championship': championship,
        'team': team,
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