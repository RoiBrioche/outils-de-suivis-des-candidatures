from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import transaction
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import (
    PeriodeRecherche, Candidature, PisteCandidature, Statut, DocumentCandidature, Priorite
)
from .forms import (
    PeriodeRechercheForm, CandidatureForm, PisteCandidatureForm, 
    StatutForm, DocumentCandidatureForm, CandidatureSearchForm
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
    paginate_by = 20
    
    allowed_sort_fields = {
        'entreprise': 'entreprise',
        'poste': 'poste',
        'statut': 'statut__nom',
        'date_candidature': 'date_candidature',
        'priorite': 'priorite',
    }

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
            # Remove leading dash for field lookup
            sort_field = sort_param.lstrip('-')
            if sort_field in self.allowed_sort_fields:
                # Use the actual field mapping for ordering
                order_field = self.allowed_sort_fields[sort_field]
                if sort_param.startswith('-'):
                    order_field = f'-{order_field}'
                queryset = queryset.order_by(order_field)
        else:
            # Default ordering
            queryset = queryset.order_by('-date_candidature')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CandidatureSearchForm(self.request.GET)
        context['current_sort'] = self.request.GET.get('sort', '')
        return context


class CandidatureDetailView(DetailView):
    model = Candidature
    template_name = 'candidatures/candidature_detail.html'
    context_object_name = 'candidature'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = self.object.documents.all()
        return context



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
            extra=0,
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

    def form_valid(self, form):
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

    def form_valid(self, form):
        messages.success(self.request, 'Piste de candidature créée avec succès.')
        return super().form_valid(form)


class PisteCandidatureUpdateView(UpdateView):
    model = PisteCandidature
    form_class = PisteCandidatureForm
    template_name = 'candidatures/piste_form.html'
    success_url = reverse_lazy('candidatures:piste-list')

    def form_valid(self, form):
        messages.success(self.request, 'Piste de candidature mise à jour avec succès.')
        return super().form_valid(form)


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
