from . import views, ajax
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('character', views.character, name='character'),
    path('war/create', views.createWar, name='createWar'),
    path('war/id/<str:warName>', views.war, name='war'),
    path('war/id/<str:warName>/auto', views.warAutoCreate, name='warAutoCreate'),

    path('login/', views.login, name='login'),
    path('logout', views.logout, name='logout'),

    path('ajax/kick', views.ajaxKick, name='ajaxKick'),
    path('ajax/return', views.ajaxReturn, name='ajaxReturn'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)