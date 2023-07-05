from django.contrib import admin
from django.urls import path, include
from django.urls import path
from . import views
from rest_framework import routers


urlpatterns = [
    path('fixtures/', views.match_fixtures, name='match_fixtures'),
    path('results/', views.match_results, name='results'),
    path('individual_match/<int:match_id>/', views.individual_matches, name="individual_match"),
    path('standings/', views.standings, name='standings'),
    path('about/', views.about, name='about'),
    path('compare_players', views.compare_players, name='compare_players'),
    path('team_chart/', views.team_plot_chart, name='team_chart'),
    path('scrape_news/', views.scrape_news, name='scrape_news'),
    path('set_favorite_team/', views.set_favorite_team, name='set_favorite_team'),
    path('favorite_team/', views.show_favorite_team, name='show_favorite_team'),
    path('scrape_news/<str:team>/', views.scrape_news, name='scrape_news'),
    path('scrape_news/<str:team>/<str:hide_names>/', views.scrape_news, name='scrape_news')
]
