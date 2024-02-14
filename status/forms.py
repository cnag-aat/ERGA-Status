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
        profile.orcid = self.cleaned_data['orcid']
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
        exclude = ('user',)
    # first_name = forms.CharField(max_length=30, label='First Name')
    # middle_name = forms.CharField(max_length=30, label='Middle Name',required=False)
    # last_name = forms.CharField(max_length=30, label='Last Name')
    # orcid = forms.CharField(max_length=30, label='ORCID',required=False)
    affiliation = forms.ModelMultipleChoiceField(
        queryset=Affiliation.objects.all().order_by('affiliation'),
        widget=AddAnotherWidgetWrapper(forms.SelectMultiple,reverse_lazy('create_affiliation')),
        required=True
    )

    # roles = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=ROLE_CHOICES)
    # lead =forms.BooleanField(widget=forms.CheckboxInput,required=False)
class NewSpeciesForm(ModelForm):
    class Meta:
        model = TargetSpecies
        fields = ('taxon_id',)
        widgets = {
            'taxon_id': forms.TextInput(attrs={'class':'form-control'})
        }
