from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import transaction
from django.forms import inlineformset_factory, modelformset_factory
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
import json

from .models import (
    PeriodeRecherche, Candidature, PisteCandidature, Statut, DocumentCandidature, Contact, Priorite
)
from .forms import (
    PeriodeRechercheForm, CandidatureForm, PisteCandidatureForm, 
    StatutForm, DocumentCandidatureForm, CandidatureSearchForm, ContactForm
)

# Formset pour les contacts
ContactFormSet = modelformset_factory(
    Contact,
    form=ContactForm,
    extra=1,  # Nombre de formulaires vides à afficher
    can_delete=True,  # Permet de supprimer des contacts
    can_order=True,   # Permet de réordonner les contacts
)


class PeriodeRechercheListView(ListView):
    model = PeriodeRecherche
    template_name = 'candidatures/periode_list.html'
    context_object_name = 'periodes'
    paginate_by = 10

    def get_queryset(self):
        return PeriodeRecherche.objects.all()


class PeriodeRechercheDetailView(DetailView):
    model = PeriodeRecherche
    template_name = 'candidatures/periode_detail.html'
    context_object_name = 'periode'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidatures'] = self.object.candidatures.all()
        context['pistes'] = self.object.pistes.all()
        return context


class PeriodeRechercheCreateView(CreateView):
    model = PeriodeRecherche
    form_class = PeriodeRechercheForm
    template_name = 'candidatures/periode_form.html'
    success_url = reverse_lazy('candidatures:periode-list')

    def form_valid(self, form):
        messages.success(self.request, 'Période de recherche créée avec succès.')
        return super().form_valid(form)


class PeriodeRechercheUpdateView(UpdateView):
    model = PeriodeRecherche
    form_class = PeriodeRechercheForm
    template_name = 'candidatures/periode_form.html'
    success_url = reverse_lazy('candidatures:periode-list')

    def form_valid(self, form):
        messages.success(self.request, 'Période de recherche mise à jour avec succès.')
        return super().form_valid(form)


class PeriodeRechercheDeleteView(DeleteView):
    model = PeriodeRecherche
    template_name = 'candidatures/periode_confirm_delete.html'
    success_url = reverse_lazy('candidatures:periode-list')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if not pk:
            raise AttributeError("PeriodeRechercheDeleteView must be called with a pk")
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['periode'] = self.object
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Période de recherche supprimée avec succès.')
        return super().delete(request, *args, **kwargs)


class CandidatureListView(ListView):
    model = Candidature
    template_name = 'candidatures/candidature_list.html'
    context_object_name = 'candidatures'
    paginate_by = 20  # Valeur par défaut
    
    allowed_sort_fields = {
        'entreprise': 'entreprise',
        'poste': 'poste',
        'statut': 'statut__nom',
        'date_candidature': 'date_candidature',
        'priorite': 'priorite',
    }
    
    # Options disponibles pour le nombre d'éléments par page
    paginate_by_options = [15, 30, 60]
    
    def get_paginate_by(self, queryset):
        """
        Récupère le nombre d'éléments par page depuis les paramètres GET
        """
        per_page = self.request.GET.get('per_page')
        if per_page and per_page.isdigit():
            per_page = int(per_page)
            if per_page in self.paginate_by_options:
                return per_page
        return self.paginate_by
    
    def get_queryset(self):
        queryset = Candidature.objects.select_related('periode_recherche', 'statut')
        
        form = CandidatureSearchForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get('search')
            statut = form.cleaned_data.get('statut')
            periode_recherche = form.cleaned_data.get('periode_recherche')
            contrat = form.cleaned_data.get('contrat')
            if search:
                queryset = queryset.filter(
                    Q(entreprise__icontains=search) | Q(poste__icontains=search)
                )
            if statut:
                queryset = queryset.filter(statut=statut)
            if periode_recherche:
                queryset = queryset.filter(periode_recherche=periode_recherche)
            if contrat:
                queryset = queryset.filter(contrat=contrat)
        
        # Handle sorting
        sort_param = self.request.GET.get('sort')
        if sort_param:
            sort_field = sort_param.lstrip('-')
            if sort_field in self.allowed_sort_fields:
                order_field = self.allowed_sort_fields[sort_field]
                if sort_param.startswith('-'):
                    order_field = f'-{order_field}'
                queryset = queryset.order_by(order_field)
        else:
            queryset = queryset.order_by('-date_candidature')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CandidatureSearchForm(self.request.GET)
        context['current_sort'] = self.request.GET.get('sort', '')
        context['paginate_by_options'] = self.paginate_by_options
        context['current_per_page'] = self.get_paginate_by(None)
        
        # Ajouter les statuts disponibles pour l'édition inline
        context['statuts_disponibles'] = Statut.objects.filter(actif=True).order_by('ordre_affichage', 'nom')
        
        # Pour conserver les paramètres de requête dans la pagination
        # en supprimant page et per_page pour éviter les duplications
        querystring = self.request.GET.copy()
        querystring.pop('page', None)
        querystring.pop('per_page', None)
        context['clean_querystring'] = querystring.urlencode()
        
        return context


class CandidatureDetailView(DetailView):
    model = Candidature
    template_name = 'candidatures/candidature_detail.html'
    context_object_name = 'candidature'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = self.object.documents.all()
        
        # Créer le formset pour les documents
        DocumentFormSet = modelformset_factory(
            DocumentCandidature,
            form=DocumentCandidatureForm,
            extra=1,
            can_delete=False
        )
        
        if self.request.method == 'POST':
            context['formset'] = DocumentFormSet(
                self.request.POST,
                self.request.FILES,
                queryset=DocumentCandidature.objects.none()
            )
        else:
            context['formset'] = DocumentFormSet(
                queryset=DocumentCandidature.objects.none()
            )
        
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        DocumentFormSet = modelformset_factory(
            DocumentCandidature,
            form=DocumentCandidatureForm,
            extra=1,
            can_delete=False
        )
        
        formset = DocumentFormSet(
            request.POST,
            request.FILES,
            queryset=DocumentCandidature.objects.none()
        )
        
        if formset.is_valid():
            with transaction.atomic():
                instances = formset.save(commit=False)
                for instance in instances:
                    # Gérer le fichier uploadé
                    if hasattr(instance, 'fichier') and instance.fichier:
                        instance.chemin_fichier = instance.fichier.name
                        instance.mime_type = instance.fichier.content_type
                        instance.taille = instance.fichier.size
                    
                    # Associer la candidature courante
                    instance.candidature = self.object
                    instance.save()
                
                messages.success(request, f'{len(instances)} document(s) ajouté(s) avec succès.')
        
        return redirect(reverse_lazy('candidatures:candidature-detail', kwargs={'pk': self.object.pk}))



class CandidatureCreateView(CreateView):
    model = Candidature
    form_class = CandidatureForm
    template_name = 'candidatures/candidature_form.html'
    success_url = reverse_lazy('candidatures:candidature-list')

    def get_initial(self):
        initial = super().get_initial()

        # Date par défaut
        initial['date_candidature'] = timezone.now().date()
        initial['date_statut'] = timezone.now().date()
        # Période active unique
        periods = PeriodeRecherche.objects.filter(active=True)
        if periods.count() == 1:
            initial['periode_recherche'] = periods.first()

        initial['priorite'] = Priorite.FAIBLE  

        # Statut "ENVOYE" si existant
        try:
            initial['statut'] = Statut.objects.get(code='ENVOYE')
        except Statut.DoesNotExist:
            pass

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        DocumentFormSet = inlineformset_factory(
            Candidature,
            DocumentCandidature,
            form=DocumentCandidatureForm,
            extra=1,
            can_delete=True,
        )

        if self.request.POST:
            context['document_formset'] = DocumentFormSet(
                self.request.POST
            )
        else:
            context['document_formset'] = DocumentFormSet()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['document_formset']

        with transaction.atomic():
            self.object = form.save()

            if formset.is_valid():
                formset.instance = self.object
                formset.save()
            else:
                return self.form_invalid(form)

        messages.success(self.request, "Candidature créée avec succès.")
        return super().form_valid(form)


class CandidatureUpdateView(UpdateView):
    model = Candidature
    form_class = CandidatureForm
    template_name = 'candidatures/candidature_form.html'
    success_url = reverse_lazy('candidatures:candidature-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        DocumentFormSet = inlineformset_factory(
            Candidature,
            DocumentCandidature,
            form=DocumentCandidatureForm,
            extra=1,
            can_delete=True,
        )

        if self.request.POST:
            context['document_formset'] = DocumentFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            context['document_formset'] = DocumentFormSet(
                instance=self.object
            )

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['document_formset']

        with transaction.atomic():
            self.object = form.save()

            if formset.is_valid():
                formset.save()
            else:
                return self.form_invalid(form)

        messages.success(self.request, 'Candidature mise à jour avec succès.')
        return super().form_valid(form)


class CandidatureDeleteView(DeleteView):
    model = Candidature
    template_name = 'candidatures/candidature_confirm_delete.html'
    success_url = reverse_lazy('candidatures:candidature-list')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if not pk:
            raise AttributeError("CandidatureDeleteView must be called with a pk")
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidature'] = self.object
        context['documents'] = self.object.documents.all()
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Candidature supprimée avec succès.')
        return super().delete(request, *args, **kwargs)


class PisteCandidatureListView(ListView):
    model = PisteCandidature
    template_name = 'candidatures/piste_list.html'
    context_object_name = 'pistes'
    paginate_by = 20

    def get_queryset(self):
        return PisteCandidature.objects.select_related('periode_recherche')


class PisteCandidatureDetailView(DetailView):
    model = PisteCandidature
    template_name = 'candidatures/piste_detail.html'
    context_object_name = 'piste'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Since PisteCandidature has a ForeignKey to Candidature (not ManyToMany),
        # we access the single related object, not a queryset
        if self.object.candidature:
            context['candidature'] = self.object.candidature
        return context


class PisteCandidatureCreateView(CreateView):
    model = PisteCandidature
    form_class = PisteCandidatureForm
    template_name = 'candidatures/piste_form.html'
    success_url = reverse_lazy('candidatures:piste-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'contact_formset' not in context:
            context['contact_formset'] = ContactFormSet(
                queryset=Contact.objects.none(),
                prefix='contact'
            )
        return context

    
    def form_valid(self, form):
        with transaction.atomic():
            # Sauvegarder d'abord la piste
            self.object = form.save()
            
            # Instancier le formset avec les données POST et le bon préfixe
            contact_formset = ContactFormSet(
                self.request.POST,
                queryset=Contact.objects.none(),
                prefix='contact'
            )
            
            # Valider et sauvegarder les contacts
            if contact_formset.is_valid():
                contacts = contact_formset.save()
                
                # Associer les contacts à la piste
                for contact in contacts:
                    self.object.contacts.add(contact)
                
                messages.success(self.request, 'Piste de candidature créée avec succès.')
                return super().form_valid(form)
            else:
                # Si le formset n'est pas valide, réafficher le formulaire avec les erreurs
                return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la création. Veuillez vérifier les informations.')
        return super().form_invalid(form)


class PisteCandidatureUpdateView(UpdateView):
    model = PisteCandidature
    form_class = PisteCandidatureForm
    template_name = 'candidatures/piste_form.html'
    success_url = reverse_lazy('candidatures:piste-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'contact_formset' not in context:
            context['contact_formset'] = ContactFormSet(
                queryset=self.object.contacts.all(),
                prefix='contact'
            )
        return context

    
    def form_valid(self, form):
        with transaction.atomic():
            # Sauvegarder d'abord la piste
            self.object = form.save()
            
            # Instancier le formset avec les données POST et le bon préfixe
            contact_formset = ContactFormSet(
                self.request.POST,
                queryset=self.object.contacts.all(),
                prefix='contact'
            )
            
            # Valider et sauvegarder les contacts
            if contact_formset.is_valid():
                contacts = contact_formset.save()
                
                # Mettre à jour les relations ManyToMany
                # D'abord supprimer toutes les relations existantes
                self.object.contacts.clear()
                
                # Ensuite ajouter tous les contacts (y compris les nouveaux et les existants)
                for contact in contacts:
                    self.object.contacts.add(contact)
                
                messages.success(self.request, 'Piste de candidature mise à jour avec succès.')
                return super().form_valid(form)
            else:
                # Si le formset n'est pas valide, réafficher le formulaire avec les erreurs
                return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la mise à jour. Veuillez vérifier les informations.')
        return super().form_invalid(form)


class PisteCandidatureDeleteView(DeleteView):
    model = PisteCandidature
    template_name = 'candidatures/piste_confirm_delete.html'
    success_url = reverse_lazy('candidatures:piste-list')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if not pk:
            raise AttributeError("PisteCandidatureDeleteView must be called with a pk")
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['piste'] = self.object
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Piste de candidature supprimée avec succès.')
        return super().delete(request, *args, **kwargs)


class StatutListView(ListView):
    model = Statut
    template_name = 'candidatures/statut_list.html'
    context_object_name = 'statuts'
    paginate_by = 20


class StatutDetailView(DetailView):
    model = Statut
    template_name = 'candidatures/statut_detail.html'
    context_object_name = 'statut'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidatures'] = self.object.candidatures.all()
        return context


class StatutCreateView(CreateView):
    model = Statut
    form_class = StatutForm
    template_name = 'candidatures/statut_form.html'
    success_url = reverse_lazy('candidatures:statut-list')

    def form_valid(self, form):
        messages.success(self.request, 'Statut créé avec succès.')
        return super().form_valid(form)


class StatutUpdateView(UpdateView):
    model = Statut
    form_class = StatutForm
    template_name = 'candidatures/statut_form.html'
    success_url = reverse_lazy('candidatures:statut-list')

    def form_valid(self, form):
        messages.success(self.request, 'Statut mis à jour avec succès.')
        return super().form_valid(form)


class DocumentCandidatureCreateView(CreateView):
    model = DocumentCandidature
    form_class = DocumentCandidatureForm
    template_name = 'candidatures/document_form.html'

    def get_initial(self):
        initial = super().get_initial()
        candidature_id = self.request.GET.get('candidature')
        if candidature_id:
            try:
                candidature = get_object_or_404(Candidature, pk=candidature_id)
                initial['candidature'] = candidature
            except:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        candidature_id = self.request.GET.get('candidature')
        if candidature_id:
            context['candidature_id'] = candidature_id
        return context

    def get_success_url(self):
        return reverse_lazy('candidatures:candidature-detail', kwargs={'pk': self.object.candidature.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Document ajouté avec succès.')
        return super().form_valid(form)


class DocumentCandidatureDeleteView(DeleteView):
    model = DocumentCandidature
    template_name = 'candidatures/document_confirm_delete.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if not pk:
            raise AttributeError("DocumentCandidatureDeleteView must be called with a pk")
        return super().get_object(queryset)

    def get_success_url(self):
        return reverse_lazy('candidatures:candidature-detail', kwargs={'pk': self.object.candidature.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Document supprimé avec succès.')
        return super().delete(request, *args, **kwargs)


def dashboard(request):
    active_period = PeriodeRecherche.objects.filter(active=True).first()
    recent_candidatures = Candidature.objects.select_related('statut').order_by('-created_at')[:5]
    
    context = {
        'active_period': active_period,
        'recent_candidatures': recent_candidatures,
        'total_candidatures': Candidature.objects.count(),
        'total_pistes': PisteCandidature.objects.count(),
    }
    
    return render(request, 'candidatures/dashboard.html', context)


@require_http_methods(["POST"])
def contact_remove_from_piste(request):
    """
    Vue AJAX pour retirer un contact d'une piste de candidature
    """
    try:
        data = json.loads(request.body)
        contact_id = data.get('contact_id')
        piste_id = data.get('piste_id')
        
        print(f"DEBUG: contact_id={contact_id}, piste_id={piste_id}")  # Debug
        
        if not contact_id or not piste_id:
            print("DEBUG: Données manquantes")
            return JsonResponse({
                'success': False,
                'error': 'Données manquantes'
            })
        
        # Récupérer la piste et le contact
        piste = get_object_or_404(PisteCandidature, pk=piste_id)
        contact = get_object_or_404(Contact, pk=contact_id)
        
        print(f"DEBUG: piste={piste}, contact={contact}")  # Debug
        
        # Vérifier que le contact est bien associé à la piste
        if not piste.contacts.filter(pk=contact_id).exists():
            print("DEBUG: Contact non associé à la piste")
            return JsonResponse({
                'success': False,
                'error': 'Ce contact n\'est pas associé à cette piste'
            })
        
        # Retirer le contact de la piste (ne pas supprimer le contact lui-même)
        piste.contacts.remove(contact)
        print("DEBUG: Contact retiré avec succès")  # Debug
        
        return JsonResponse({
            'success': True,
            'message': 'Contact retiré de la piste avec succès'
        })
        
    except json.JSONDecodeError as e:
        print(f"DEBUG: JSONDecodeError: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Format de données invalide'
        })
    except Exception as e:
        print(f"DEBUG: Exception générale: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["POST"])
@csrf_exempt
def contact_add_ajax(request):
    """
    Vue AJAX pour ajouter un ou plusieurs contacts à une piste de candidature
    """
    try:
        data = json.loads(request.body)
        piste_id = data.get('piste_id')
        contacts_data = data.get('contacts', [])
        
        if not piste_id or not contacts_data:
            return JsonResponse({
                'success': False,
                'error': 'Données manquantes'
            })
        
        # Récupérer la piste
        piste = get_object_or_404(PisteCandidature, pk=piste_id)
        
        # Créer les contacts et les associer à la piste
        created_contacts = []
        with transaction.atomic():
            for contact_data in contacts_data:
                # Valider que le nom est présent
                if not contact_data.get('nom', '').strip():
                    return JsonResponse({
                        'success': False,
                        'error': 'Le nom du contact est obligatoire'
                    })
                
                # Créer le contact
                contact = Contact.objects.create(
                    nom=contact_data.get('nom', '').strip(),
                    prenom=contact_data.get('prenom', '').strip() or None,
                    poste_occupe=contact_data.get('poste_occupe', '').strip() or None,
                    email=contact_data.get('email', '').strip() or None,
                    telephone=contact_data.get('telephone', '').strip() or None,
                    linkedin_url=contact_data.get('linkedin_url', '').strip() or None
                )
                
                # Associer le contact à la piste
                piste.contacts.add(contact)
                created_contacts.append(contact)
        
        return JsonResponse({
            'success': True,
            'message': f'{len(created_contacts)} contact(s) ajouté(s) avec succès',
            'contacts_count': piste.contacts.count()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Format de données invalide'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["POST"])
def candidature_update_field(request, pk):
    """
    Vue AJAX pour mettre à jour un champ spécifique d'une candidature
    Champs acceptés : "statut", "priorite"
    """
    try:
        # Récupérer la candidature
        candidature = get_object_or_404(Candidature, pk=pk)
        
        # Parser les données JSON
        data = json.loads(request.body)
        field_name = data.get('field')
        field_value = data.get('value')
        
        # Valider le champ
        allowed_fields = ['statut', 'priorite']
        if field_name not in allowed_fields:
            return JsonResponse({
                'success': False,
                'error': f'Champ "{field_name}" non autorisé'
            }, status=400)
        
        # Mettre à jour le champ selon son type
        if field_name == 'statut':
            # Le statut est un ForeignKey, on s'attend à un UUID
            if field_value:
                try:
                    statut = get_object_or_404(Statut, pk=field_value)
                    candidature.statut = statut
                except (ValueError, Statut.DoesNotExist):
                    return JsonResponse({
                        'success': False,
                        'error': 'Statut invalide'
                    }, status=400)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Le statut ne peut pas être vide'
                }, status=400)
                
        elif field_name == 'priorite':
            # La priorité est un CharField avec choices
            if field_value:
                valid_priorities = [choice[0] for choice in Priorite.choices]
                if field_value not in valid_priorities:
                    return JsonResponse({
                        'success': False,
                        'error': f'Priorité invalide. Valeurs acceptées : {", ".join(valid_priorities)}'
                    }, status=400)
                candidature.priorite = field_value
            else:
                candidature.priorite = ''
        
        # Sauvegarder les modifications
        candidature.save()
        
        # Retourner la réponse de succès avec les nouvelles valeurs
        response_data = {
            'success': True,
            'message': f'Champ "{field_name}" mis à jour avec succès'
        }
        
        # Ajouter les valeurs d'affichage pour le frontend
        if field_name == 'statut':
            response_data['display_value'] = str(candidature.statut)
        elif field_name == 'priorite':
            response_data['display_value'] = candidature.get_priorite_display() if candidature.priorite else ''
            
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Format de données JSON invalide'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur serveur : {str(e)}'
        }, status=500)
