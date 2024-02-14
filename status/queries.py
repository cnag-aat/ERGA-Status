import django
from status.models import *
gts = GenomeTeam.objects.all()
for gt in gts:
    sep = "\t"
    if(gt.sample_coordinator):
        print(sep.join([gt.sample_coordinator.first_name,
                        gt.sample_coordinator.middle_name if gt.sample_coordinator.middle_name else "",
                        gt.sample_coordinator.last_name,
                        gt.sample_coordinator.user.email,
                        gt.sample_coordinator.orcid if gt.sample_coordinator.orcid else ""]))
	