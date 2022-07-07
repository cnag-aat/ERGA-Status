
# Load initial Resistom data from excel into the database
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
        if row['taxon_id'] or None:
            print(row)
            print(row['taxon_id'] or None)

            #if row['with_data'] != '1':
            #    print('with_data:' + row['with_data'])
            #    print("Skipped")
            #    continue

            t_kingdom = None
            if row['kingdom']:
                t_kingdom, _ = TaxonKingdom.objects.get_or_create(
                    name=row['kingdom'],
                )

            t_phylum = None
            if row['phylum']:
                t_phylum, _ = TaxonPhylum.objects.get_or_create(
                    name=row['phylum'],
                    taxon_kingdom=t_kingdom
                )

            t_class = None
            if row['class']:
                t_class, _ = TaxonClass.objects.get_or_create(
                    name=row['class'],
                    taxon_kingdom=t_kingdom,
                    taxon_phylum=t_phylum,
                )

            t_order = None
            if row['order']:
                t_phylum, _ = TaxonOrder.objects.get_or_create(
                    name=row['order'],
                    taxon_kingdom=t_kingdom,
                    taxon_phylum=t_phylum,
                    taxon_class=t_class,
                )

            t_family = None
            if row['family']:
                t_family, _ = TaxonFamily.objects.get_or_create(
                    name=row['family'],
                    taxon_kingdom=t_kingdom,
                    taxon_phylum=t_phylum,
                    taxon_class=t_class,
                    taxon_order=t_order,
                )

            t_genus = None
            if row['genus']:
                t_genus, _ = TaxonGenus.objects.get_or_create(
                    name=row['genus'],
                    taxon_kingdom=t_kingdom,
                    taxon_phylum=t_phylum,
                    taxon_class=t_class,
                    taxon_order=t_order,
                    taxon_family=t_family,
                )

            # t_species = None
            # if row['species']:
            #     t_species, _ = TaxonSpecies.objects.get_or_create(
            #         name=row['species'],
            #         taxon_kingdom=t_kingdom
            #         taxon_phylum=t_phylum,
            #         taxon_class=t_class,
            #         taxon_order=t_order,
            #         taxon_family=t_family,
            #         taxon_genus=t_genus,
            #     )


            try:
                targetspecies = TargetSpecies.objects.get(taxon_id=row['taxon_id'])
            except TargetSpecies.DoesNotExist:
                targetspecies, _ = TargetSpecies.objects.get_or_create(
                    taxon_id=row['taxon_id'])

            for syn in row['synonym'].split(','):
                try:
                    species_synonyms = Synonyms.objects.get(name=syn)
                except Synonyms.DoesNotExist:
                    species_synonyms, _ = Synonyms.objects.get_or_create(name=syn)

                species_synonyms.species = targetspecies

            for com_name in row['common_name'].split(','):
                try:
                    species_comnames = CommonNames.objects.get(name=com_name)
                except Synonyms.DoesNotExist:
                    species_comnames, _ = CommonNames.objects.get_or_create(name=com_name)

                species_comnames.species = targetspecies

            targetspecies.scientific_name = row['scientific_name'] or None
            targetspecies.tolid_prefix = row['tolid_prefix'] or None
            targetspecies.chromosome_number = row['chromosome_number'] or None
            targetspecies.haploid_number = row['haploid_number'] or None
            targetspecies.ploidy = row['ploidy'] or None
            targetspecies.c_value = row['c_value'] or None
            targetspecies.genome_size = row['genome_size'] or None
            targetspecies.taxon_kingdom = t_kingdom or None
            targetspecies.taxon_phylum = t_phylum or None
            targetspecies.taxon_class = t_class or None
            targetspecies.taxon_order = t_order or None
            targetspecies.taxon_family = t_family or None
            targetspecies.taxon_genus = t_genus or None
            targetspecies.save()

print("Finished OK")
