from allauth.account.forms import SignupForm
from django import forms
from status.models import *

ROLE_CHOICES = (
('assembly_team_lead', 'Assembly Team Lead'),
('sequencing_team_lead', 'Sequencing Team Lead'),
('annotation_team_lead', 'Annotation Team Lead'),
('sample_coordinator', 'Sample Coordinator'),
('genome_team_coordinator', 'Genome Team Coordinator'),
('sample_reception', 'Sample Reception'),
('assembly_curation', 'Assembly Curation'),
('assembly_team_lead', 'Assembly Team Lead')
)
class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    affiliation = forms.CharField(max_length=100, label='Affiliation')
    roles = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=ROLE_CHOICES)
    # class Meta():
    #     model = User
    #     fields = ('roles', 'email','first_name','last_name','username')

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        profile = UserProfile()
        #profile.save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        user.profile = profile
        profile.user = user
        profile.roles = self.cleaned_data['roles']
        profile.affiliation = self.cleaned_data['affiliation']
        profile.save()
        return user
