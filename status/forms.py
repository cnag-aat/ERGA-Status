from allauth.account.forms import SignupForm
from django import forms
from status.models import *
from django.contrib import admin
from django.urls import reverse
from django_addanother.widgets import AddAnotherWidgetWrapper

ROLE_CHOICES = (
('sample_handling_team', 'Sample Handling Team'),
('sample_coordinator', 'Sample Coordinator'),
('collection_team', 'Collection Team'),
('taxonomy_team', 'Taxonomy Team'),
('vouchering_team', 'Vouchering Team'),
('barcoding_team', 'Barcoding Team'),
('sequencing_team', 'Sequencing Team'),
('assembly_team', 'Assembly Team'),
('community_annotation_team_', 'Community Annotation Team'),
('annotation_team', 'Annotation Team'),
# ('sample_reception', 'Sample Reception'),
# ('assembly_curation', 'Assembly Curation'),
)
class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    middle_name = forms.CharField(max_length=30, label='Middle Name',required=False)
    last_name = forms.CharField(max_length=30, label='Last Name')
    orcid = forms.CharField(max_length=30, label='ORCID',required=False)
    # affiliation = forms.ModelMultipleChoiceField(
    #     queryset=Affiliation.objects.all(),
    #     # widget=admin.widgets.RelatedFieldWidgetWrapper(
    #     #     widget=admin.widgets.FilteredSelectMultiple('Affiliation', False),
    #     #     rel=UserProfile.affiliation.rel,
    #     #     admin_site=admin.site
    #     # ),
    #     # required=False,
    # )
    affiliation = forms.ModelMultipleChoiceField(
        queryset=Affiliation.objects.all().order_by('affiliation'),
        widget=AddAnotherWidgetWrapper(forms.SelectMultiple,reverse('create_affiliation')),
        required=True
    )
    # class Meta:
    #     widgets = {
    #          'affiliation': AddAnotherWidgetWrapper(
    #              forms.SelectMultiple,
    #              reverse('create_affiliation'),
    #          )
    #      }
    #affiliation = forms.CharField(max_length=100, label='Affiliation')
    roles = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=ROLE_CHOICES)
    lead =forms.BooleanField(widget=forms.CheckboxInput,required=False)
    # class Meta():
    #     model = User
    #     fields = ('roles', 'email','first_name','last_name','username')
    policy =forms.BooleanField(widget=forms.CheckboxInput,required=True,label='I have read and agree to the privacy policy')
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
        profile.roles = self.cleaned_data['roles']
        profile.lead = self.cleaned_data['lead']
        profile.save()
        profile.affiliation.set(self.cleaned_data['affiliation'])
        profile.save()
        return user
