"""
URL configuration for arenalesleague project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from championship import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    path('championship/', views.championship, name='championship'),
    path('championship/<int:championship_id>', views.championship_view, name='championship_view'),
    path('championship/<int:championship_id>/delete', views.championship_delete, name='championship_delete'),
    path('championship/create/', views.create_championship,
         name='create_championship'),
    #aqui voy a mostrar los equipos de un campeonato especifico
    path('championship/<int:championship_id>/teams/', views.championship_teams_view, name='championship_teams_view'),
    path('championship/<int:championship_id>/teams/<int:team_id>/players/', views.players_team_view, name='players_team_view'),
    #path('championship/<int:championship_id>/teams/<int:team_id>/players/', views.players_team_view, name='players_team_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
