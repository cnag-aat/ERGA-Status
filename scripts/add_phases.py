
import django
django.setup()

from status.models import *
import csv
import argparse

parser = argparse.ArgumentParser(
    description='Add phases')
parser.add_argument('csv_file', metavar='csv',
                    help='a CSV formatted file')
args = parser.parse_args()
with open(args.csv_file,encoding='utf-8-sig') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter='\t')
    for row in csvreader:
        if row['taxon_id']:
            if row['phase'] and len(row['phase'])>0:
                print(row)
                p, created = Phase.objects.get_or_create(
                    name=row['phase']
                )
                seq_record = Sequencing.objects.get(species__taxon_id=row['taxon_id'])
                print(seq_record.species.scientific_name)
                seq_record.phase = p
                seq_record.save()
print("Finished OK")
