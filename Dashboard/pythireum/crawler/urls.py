from django.urls import path

from . import views

app_name = 'crawler'
urlpatterns = [
    path('', views.main, name='main'),
    path('datasource/<str:datasource_type>/', views.datasource_list, name='datasourceList'),
    path('datasource/<str:datasource_type>/<str:datasource_name>', views.datasource, name='datasource'),
    path('search/', views.search, name='search'),
    path('search/<str:search_name>', views.searchpage, name='searchpage'),
    path('searchlist/', views.searchlist, name='searchlist'),
    path('blockchain/', views.blockchain, name='blockchain'),
]