from django.contrib import admin
from .models import (
    PeriodeRecherche, Candidature, PisteCandidature, Statut, DocumentCandidature, Contact
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


# Créez une classe Inline pour afficher les pistes dans la fiche Contact
class PisteRechercheInline(admin.TabularInline):
    # On cible la table intermédiaire générée par Django pour le ManyToMany
    model = PisteCandidature.contacts.through
    extra = 0
    verbose_name = "Piste de candidature associée"
    verbose_name_plural = "Pistes de candidature associées"
    can_delete = True


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    # 1. On ajoute 'afficher_pistes' dans la liste des colonnes
    list_display = ('nom_complet', 'afficher_pistes', 'email', 'poste_occupe', 'telephone', 'created_at')
    
    # L'inline reste ici (pour voir le détail dans la fiche)
    inlines = [PisteRechercheInline]
    
    list_filter = ('poste_occupe', 'created_at')
    search_fields = ('nom', 'prenom', 'email', 'poste_occupe')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    # ... (vos fieldsets restent inchangés) ...
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'prenom', 'poste_occupe')
        }),
        ('Coordonnées', {
            'fields': ('email', 'telephone', 'linkedin_url')
        }),
        ('Informations supplémentaires', {
            'fields': ('commentaires',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def nom_complet(self, obj):
        return obj.nom_complet
    nom_complet.short_description = 'Nom complet'
    nom_complet.admin_order_field = 'nom'

    # 2. La fonction pour récupérer et afficher les pistes liées
    def afficher_pistes(self, obj):
        # On utilise le related_name défini dans votre modèle PisteCandidature
        pistes = obj.pistes_candidature.all()
        # On crée une liste de chaînes (ex: "Google - En cours")
        pistes_str = [str(p) for p in pistes]
        
        # Astuce visuelle : Si la liste est longue, on peut limiter l'affichage
        if not pistes_str:
            return "-"
        return ", ".join(pistes_str)

    afficher_pistes.short_description = "Pistes rattachées"

    # 3. OPTIMISATION (Très important)
    # Sans cela, Django ferait une requête SQL par contact affiché pour chercher les pistes (problème N+1)
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('pistes_candidature')


@admin.register(PisteCandidature)
class PisteCandidatureAdmin(admin.ModelAdmin):
    # 1. Ajouter une colonne contacts dans la liste globale
    list_display = ('entreprise', 'poste_cible', 'periode_recherche', 'etat', 'afficher_contacts', 'created_at')
    
    # 2. Améliorer le widget de sélection dans le formulaire
    filter_horizontal = ('contacts',)  # Crée une interface à deux colonnes (Dispo / Choisi)
    search_fields = ('entreprise', 'poste_cible', 'source')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Informations générales', {
            'fields': ('periode_recherche', 'entreprise', 'poste_cible')
        }),
        ('Détails', {
            # Note : 'contacts' utilisera maintenant le widget filter_horizontal
            'fields': ('source', 'contacts', 'url_annonce', 'commentaires')
        }),
        ('État', {
            'fields': ('etat', 'candidature')
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Fonction pour afficher les contacts proprement dans list_display
    def afficher_contacts(self, obj):
        # On récupère tous les contacts liés et on affiche leurs noms
        return ", ".join([c.nom_complet for c in obj.contacts.all()])
    
    afficher_contacts.short_description = "Contacts associés"


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
            'fields': ('commentaires', 'statut_contextuel', 'contacts')
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
