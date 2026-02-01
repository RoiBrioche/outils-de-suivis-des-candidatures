from django.urls import path
from . import views

app_name = 'candidatures'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Période de recherche URLs
    path('periodes/', views.PeriodeRechercheListView.as_view(), name='periode-list'),
    path('periodes/<uuid:pk>/', views.PeriodeRechercheDetailView.as_view(), name='periode-detail'),
    path('periodes/create/', views.PeriodeRechercheCreateView.as_view(), name='periode-create'),
    path('periodes/<uuid:pk>/update/', views.PeriodeRechercheUpdateView.as_view(), name='periode-update'),
    path('periodes/<uuid:pk>/delete/', views.PeriodeRechercheDeleteView.as_view(), name='periode-delete'),
    
    # Candidature URLs
    path('candidatures/', views.CandidatureListView.as_view(), name='candidature-list'),
    path('candidatures/<uuid:pk>/', views.CandidatureDetailView.as_view(), name='candidature-detail'),
    path('candidatures/create/', views.CandidatureCreateView.as_view(), name='candidature-create'),
    path('candidatures/<uuid:pk>/update/', views.CandidatureUpdateView.as_view(), name='candidature-update'),
    path('candidatures/<uuid:pk>/delete/', views.CandidatureDeleteView.as_view(), name='candidature-delete'),
    
    # Piste de candidature URLs
    path('pistes/', views.PisteCandidatureListView.as_view(), name='piste-list'),
    path('pistes/<uuid:pk>/', views.PisteCandidatureDetailView.as_view(), name='piste-detail'),
    path('pistes/create/', views.PisteCandidatureCreateView.as_view(), name='piste-create'),
    path('pistes/<uuid:pk>/update/', views.PisteCandidatureUpdateView.as_view(), name='piste-update'),
    path('pistes/<uuid:pk>/delete/', views.PisteCandidatureDeleteView.as_view(), name='piste-delete'),
    
    # Statut URLs
    path('statuts/', views.StatutListView.as_view(), name='statut-list'),
    path('statuts/<uuid:pk>/', views.StatutDetailView.as_view(), name='statut-detail'),
    path('statuts/create/', views.StatutCreateView.as_view(), name='statut-create'),
    path('statuts/<uuid:pk>/update/', views.StatutUpdateView.as_view(), name='statut-update'),
    
    # Document URLs
    path('documents/create/', views.DocumentCandidatureCreateView.as_view(), name='document-create'),
    path('documents/<uuid:pk>/delete/', views.DocumentCandidatureDeleteView.as_view(), name='document-delete'),
]
