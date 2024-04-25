
import django
django.setup()

from status.models import *
import csv
import argparse

parser = argparse.ArgumentParser(
    description='Add records to ERGA target species table.')
parser.add_argument('csv_file', metavar='csv',
                    help='a CSV formatted file')
args = parser.parse_args()
with open(args.csv_file) as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter='\t')

    for row in csvreader:  
        if row['country']:
            print(row)
            country, _ = Country.objects.get_or_create(
                    name=row['country'],
                )
        else:
            print("no country\n")
            print(row)

print("Finished")
