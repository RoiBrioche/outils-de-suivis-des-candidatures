from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    PeriodeRecherche, Candidature, PisteCandidature, Statut, DocumentCandidature,
    TypeContrat, Priorite, SourcePriorite, EtatPiste, TypeDocument
)


class PeriodeRechercheForm(forms.ModelForm):
    class Meta:
        model = PeriodeRecherche
        fields = ['nom', 'description', 'date_debut', 'date_fin']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_debut': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'  
            ),
            'date_fin': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'  
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')

        # -------------------------------
        # Règle : cohérence des dates
        # -------------------------------
        if date_debut and date_fin:
            if date_fin < date_debut:
                raise ValidationError(
                    'La date de fin ne peut pas être antérieure à la date de début.'
                )

        return cleaned_data


class StatutForm(forms.ModelForm):
    class Meta:
        model = Statut
        fields = ['nom', 'code', 'actif', 'ordre_affichage']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ordre_affichage': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PisteCandidatureForm(forms.ModelForm):
    class Meta:
        model = PisteCandidature
        fields = ['periode_recherche', 'entreprise', 'poste_cible', 'source', 'contact', 'url_annonce', 'commentaires', 'etat', 'candidature']
        widgets = {
            'periode_recherche': forms.Select(attrs={'class': 'form-control'}),
            'entreprise': forms.TextInput(attrs={'class': 'form-control'}),
            'poste_cible': forms.TextInput(attrs={'class': 'form-control'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'url_annonce': forms.URLInput(attrs={'class': 'form-control'}),
            'commentaires': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'etat': forms.Select(attrs={'class': 'form-control'}),
            'candidature': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['candidature'].required = False
        self.fields['candidature'].empty_label = "Aucune candidature"

    def clean(self):
        cleaned_data = super().clean()
        etat = cleaned_data.get('etat')
        candidature = cleaned_data.get('candidature')

        if etat == EtatPiste.TRANSFORMEE and not candidature:
            raise ValidationError('Une piste transformée doit être associée à une candidature.')

        return cleaned_data


class CandidatureForm(forms.ModelForm):
    class Meta:
        model = Candidature
        fields = [
            'periode_recherche',
            'statut',
            'entreprise',
            'poste',
            'localisation',
            'contrat',
            'canal',
            'date_candidature',
            'commentaires',
            'statut_contextuel',
            'priorite',
            'priorite_source',
        ]
        widgets = {
            'periode_recherche': forms.Select(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'entreprise': forms.TextInput(attrs={'class': 'form-control'}),
            'poste': forms.TextInput(attrs={'class': 'form-control'}),
            'localisation': forms.TextInput(attrs={'class': 'form-control'}),
            'contrat': forms.Select(attrs={'class': 'form-control'}),
            'canal': forms.TextInput(attrs={'class': 'form-control'}),
            'date_candidature': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'  # <-- format compatible HTML5
            ),
            'date_statut': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'
            ),
            'commentaires': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'statut_contextuel': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2}
            ),
            'priorite': forms.Select(attrs={'class': 'form-control'}),
            'priorite_source': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:  # seulement si le formulaire n'est pas lié à POST
            self.fields['date_candidature'].initial = self.fields['date_candidature'].initial or timezone.now().date()

    def clean(self):
        cleaned_data = super().clean()

        date_candidature = cleaned_data.get('date_candidature')
        periode = cleaned_data.get('periode_recherche')
        priorite = cleaned_data.get('priorite')
        source = cleaned_data.get('priorite_source')

        # Cohérence période / date
        if date_candidature and periode:
            if date_candidature < periode.date_debut:
                raise ValidationError(
                    "La date de candidature est antérieure au début de la période."
                )
            if periode.date_fin and date_candidature > periode.date_fin:
                raise ValidationError(
                    "La date de candidature est postérieure à la fin de la période."
                )

        # Règles priorité
        if priorite and not source:
            raise ValidationError(
                "La source doit être définie lorsque la priorité est renseignée."
            )

        if source and not priorite:
            raise ValidationError(
                "La priorité doit être définie lorsque la source est renseignée."
            )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if (
            instance.priorite
            and instance.priorite_source == SourcePriorite.AUTOMATIQUE
            and not instance.date_priorite
        ):
            instance.date_priorite = timezone.now().date()

        if commit:
            instance.save()

        return instance


class DocumentCandidatureForm(forms.ModelForm):
    class Meta:
        model = DocumentCandidature
        fields = ['type_document', 'chemin_fichier', 'commentaire']
        widgets = {
            'type_document': forms.Select(attrs={'class': 'form-control'}),
            'chemin_fichier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'C:\\Users\\Nom\\Documents\\mon_cv.pdf'
            }),
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2,
                'placeholder': 'Notes sur ce document...'
            }),
        }


class CandidatureSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par entreprise ou poste...'
        })
    )
    statut = forms.ModelChoiceField(
        queryset=Statut.objects.all(),
        required=False,
        empty_label="Tous les statuts",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    periode_recherche = forms.ModelChoiceField(
        queryset=PeriodeRecherche.objects.all(),
        required=False,
        empty_label="Toutes les périodes",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    contrat = forms.ChoiceField(
        choices=[('', 'Tous les types')] + list(TypeContrat.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
