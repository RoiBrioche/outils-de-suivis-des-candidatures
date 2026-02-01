from django.contrib import admin
from .models import (
    PeriodeRecherche, Candidature, PisteCandidature, Statut, DocumentCandidature
)


@admin.register(PeriodeRecherche)
class PeriodeRechercheAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_debut', 'date_fin', 'active', 'created_at')
    list_filter = ('active', 'date_debut', 'date_fin')
    search_fields = ('nom', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description', 'active')
        }),
        ('Période', {
            'fields': ('date_debut', 'date_fin')
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Statut)
class StatutAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code', 'actif', 'ordre_affichage', 'created_at')
    list_filter = ('actif', 'ordre_affichage')
    search_fields = ('nom', 'code')
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'code', 'actif', 'ordre_affichage')
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PisteCandidature)
class PisteCandidatureAdmin(admin.ModelAdmin):
    list_display = ('entreprise', 'poste_cible', 'periode_recherche', 'etat', 'created_at')
    list_filter = ('etat', 'periode_recherche')
    search_fields = ('entreprise', 'poste_cible', 'source', 'contact')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Informations générales', {
            'fields': ('periode_recherche', 'entreprise', 'poste_cible')
        }),
        ('Détails', {
            'fields': ('source', 'contact', 'url_annonce', 'commentaires')
        }),
        ('État', {
            'fields': ('etat', 'candidature')
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class DocumentCandidatureInline(admin.TabularInline):
    model = DocumentCandidature
    extra = 1
    readonly_fields = ('id', 'date_ajout')
    fields = ('type_document', 'nom_fichier', 'chemin_fichier', 'mime_type', 'taille', 'commentaire', 'date_ajout')


@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    list_display = ('entreprise', 'poste', 'statut', 'periode_recherche', 'date_candidature', 'contrat')
    list_filter = ('statut', 'contrat', 'periode_recherche', 'priorite')
    search_fields = ('entreprise', 'poste', 'localisation', 'commentaires')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [DocumentCandidatureInline]
    fieldsets = (
        ('Informations principales', {
            'fields': ('periode_recherche', 'statut', 'entreprise', 'poste')
        }),
        ('Détails du poste', {
            'fields': ('localisation', 'contrat', 'canal')
        }),
        ('Dates', {
            'fields': ('date_candidature', 'date_statut')
        }),
        ('Priorité', {
            'fields': ('priorite', 'priorite_source', 'date_priorite')
        }),
        ('Informations contextuelles', {
            'fields': ('commentaires', 'statut_contextuel')
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DocumentCandidature)
class DocumentCandidatureAdmin(admin.ModelAdmin):
    list_display = ('nom_fichier', 'candidature', 'type_document', 'taille', 'date_ajout')
    list_filter = ('type_document', 'date_ajout')
    search_fields = ('nom_fichier', 'commentaire', 'chemin_fichier')
    readonly_fields = ('id', 'date_ajout')
    fieldsets = (
        ('Informations générales', {
            'fields': ('candidature', 'type_document', 'nom_fichier')
        }),
        ('Stockage', {
            'fields': ('chemin_fichier', 'mime_type', 'taille')
        }),
        ('Informations supplémentaires', {
            'fields': ('commentaire',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'date_ajout'),
            'classes': ('collapse',)
        }),
    )
