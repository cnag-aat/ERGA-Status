
# Load initial Resistom data from excel into the database
import django
django.setup()

from status.models import *
import csv
import argparse

parser = argparse.ArgumentParser(
    description='Add BUSCO dbs')
parser.add_argument('csv_file', metavar='csv',
                    help='a CSV formatted file')
args = parser.parse_args()
with open(args.csv_file) as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter='\t')

    for row in csvreader:
        if row['db'] or None:
            print(row)
            print(row['db'] or None)

            if row['db']:
                bdb, _ = BUSCOdb.objects.get_or_create(
                    db=row['db']
                )

print("Finished OK")
