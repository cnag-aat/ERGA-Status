from allauth.account.forms import SignupForm
from django import forms
from django.forms import ModelForm
from status.models import *
from django.contrib import admin
from django.urls import reverse_lazy
from django_addanother.widgets import AddAnotherWidgetWrapper
from django.contrib.auth.models import User

ROLE_CHOICES = (
('sample_handling_team', 'Sample Handling Team'),
('sample_coordinator', 'Sample Coordinator'),
('collection_team', 'Collection Team'),
('taxonomy_team', 'Taxonomy Team'),
('vouchering_team', 'Vouchering Team'),
('barcoding_team', 'Barcoding Team'),
('sequencing_team', 'Sequencing Team'),
('assembly_team', 'Assembly Team'),
('community_annotation_team', 'Community Annotation Team'),
('annotation_team', 'Annotation Team'),
('other', 'other'),
)
class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=60, label='First Name')
    middle_name = forms.CharField(max_length=60, label='Middle Name',required=False)
    last_name = forms.CharField(max_length=60, label='Last Name')
    orcid = forms.CharField(max_length=60, label='ORCID',required=False)
    research_group = forms.ModelChoiceField(
        queryset=ResearchGroup.objects.all().order_by('name'),
        widget=AddAnotherWidgetWrapper(forms.Select, reverse_lazy('create_research_group')),
        required=False,
        label='Research group',
        help_text='Your research group or lab (e.g. PI surname). Select an existing entry or add a new one. Used for conflict-of-interest checks in the EAR review process.'
    )
    affiliation = forms.ModelMultipleChoiceField(
        queryset=Affiliation.objects.all().order_by('affiliation'),
        widget=AddAnotherWidgetWrapper(forms.SelectMultiple,reverse_lazy('create_affiliation')),
        required=True
    )
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all().order_by('description'),
        #widget=AddAnotherWidgetWrapper(forms.SelectMultiple,reverse_lazy('create_affiliation')),
        #required=True
    )
    # roles = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=ROLE_CHOICES)
    lead =forms.BooleanField(widget=forms.CheckboxInput,required=False)
    policy =forms.BooleanField(widget=forms.CheckboxInput,required=True,label='I have read and agree to the <a target="_blank" href="/static/ERGA_Privacy_Notice_v1.pdf">ERGA Privacy Policy v1</a>')
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        profile = UserProfile()
        #profile.save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        #user.affiliation = self.affiliation
        user.save()
        #user.profile = profile
        profile.user = user
        profile.first_name = self.cleaned_data['first_name']
        profile.middle_name = self.cleaned_data['middle_name']
        profile.last_name = self.cleaned_data['last_name']
        profile.orcid = self.cleaned_data['orcid'].replace("https://orcid.org/",'')
        profile.research_group = self.cleaned_data['research_group']
        profile.lead = self.cleaned_data['lead']
        profile.save()
        profile.affiliation.set(self.cleaned_data['affiliation'])
        profile.save()
        profile.roles.set(self.cleaned_data['roles'])
        profile.save()
        return user

class ProfileUpdateForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'calling_score')
    affiliation = forms.ModelMultipleChoiceField(
        queryset=Affiliation.objects.all().order_by('affiliation'),
        widget=AddAnotherWidgetWrapper(forms.SelectMultiple, reverse_lazy('create_affiliation')),
        required=True
    )
    research_group = forms.ModelChoiceField(
        queryset=ResearchGroup.objects.all().order_by('name'),
        widget=AddAnotherWidgetWrapper(forms.Select, reverse_lazy('create_research_group')),
        required=False,
        label='Research group',
        help_text='Your research group or lab (e.g. PI surname). Select an existing entry or add a new one.'
    )
# class NewSpeciesForm(ModelForm):
#     class Meta:
#         model = TargetSpecies
#         fields = ('taxon_id',)
#         widgets = {
#             'taxon_id': forms.TextInput(attrs={'class':'form-control'})
#         }

class NewSpeciesListForm(ModelForm):
    class Meta:
        model = SpeciesUpload
        fields = ('file',)
        # widgets = {
        #     'taxon_id': forms.TextInput(attrs={'class':'form-control'})
        # }


class EARReviewCreateForm(forms.ModelForm):
    initial_comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'Anything reviewers should know about this assembly upfront…',
        }),
        required=False,
        label='Initial notes (optional)',
    )

    class Meta:
        model = EARReview
        fields = ('assembly_project', 'contig_level_assembly', 'ear_pdf', 'pretext_file')
        widgets = {
            'assembly_project': forms.Select(attrs={'class': 'form-control'}),
            'contig_level_assembly': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_contig_level_assembly'}),
            'ear_pdf': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'application/pdf,.pdf',
            }),
            'pretext_file': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': '.pretext',
                'id': 'id_pretext_file',
            }),
        }
        help_texts = {
            'assembly_project': 'Pick the assembly project this EAR is for.',
            'ear_pdf': 'The EAR report (PDF).',
            'pretext_file': 'The main Pretext contact map. Additional pretext files (hap2, alternate thresholds) can be uploaded as attachments to comments.',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        qs = AssemblyProject.objects.filter(ear_review__isnull=True)
        if user is not None:
            # Restrict to projects where the submitter is an assembly team member
            from status.models import AssemblyTeam
            species_ids = (
                AssemblyTeam.objects
                .filter(members__user=user)
                .values_list('genometeam__species_id', flat=True)
            )
            qs = qs.filter(species_id__in=species_ids)
        self.fields['assembly_project'].queryset = qs.order_by('species__scientific_name')
        # Pretext is nullable at model level (so post-acceptance delete works) but required to submit
        self.fields['pretext_file'].required = True

    def clean(self):
        cleaned_data = super().clean()
        contig_level = cleaned_data.get('contig_level_assembly')
        pretext = cleaned_data.get('pretext_file')
        if contig_level:
            # Pretext is optional for contig-level assemblies — clear any spurious required error
            self.fields['pretext_file'].required = False
            if 'pretext_file' in self._errors:
                del self._errors['pretext_file']
                cleaned_data['pretext_file'] = None
        elif not pretext:
            self.add_error('pretext_file', 'A Pretext map is required for chromosome-level assemblies.')
        return cleaned_data


class EARCommentForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=EARComment.objects.all(),
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = EARComment
        fields = ('body', 'parent')
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Write a comment…',
            }),
        }
