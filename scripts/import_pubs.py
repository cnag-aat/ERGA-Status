import django
import os
import subprocess
import re
from datetime import datetime

django.setup()

os.environ["PATH"] = os.path.expanduser("/home/www/resistome.cnag.cat/erga/scripts") + ":" + os.environ.get("PATH", "")

FETCH_SCRIPT = "/home/www/resistome.cnag.cat/erga/scripts/fetch_pmc.sh"

from status.models import TargetSpecies, Publication

species_qs = TargetSpecies.objects.filter(goat_sequencing_status='insdc_open')

for spe in species_qs:
    species_name = spe.scientific_name
    print(f"Fetching PMC articles for species: {species_name}", file=os.sys.stderr)

    query = f'ERGA-BGE[Title] AND "{species_name}"'

    try:
        result = subprocess.run(
            [FETCH_SCRIPT, query],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")

        if not stdout.strip():
            print(f"No TSV output for {species_name}", file=os.sys.stderr)
            continue

        lines = stdout.strip().splitlines()
        header, *rows = lines
        print(f"TSV header: {header}", file=os.sys.stderr)

        latest_pub = None
        latest_year = 0

        for row in rows:
            try:
                pmcid, doi, title, journal, pubdate = row.split("\t")
                # Extract year
                year_match = re.search(r"\d{4}", pubdate)
                year = int(year_match.group(0)) if year_match else datetime.now().year

                # Keep track of the newest publication
                if year > latest_year:
                    latest_year = year
                    latest_pub = {
                        "pmcid": pmcid,
                        "doi": doi,
                        "title": title,
                        "journal": journal,
                        "date": year
                    }

            except ValueError:
                print(f"Skipping malformed row: {row}", file=os.sys.stderr)

        # Insert/update only the newest publication
        if latest_pub:
            pub, created = Publication.objects.update_or_create(
                species=spe,
                defaults=latest_pub
            )
            action = "Created" if created else "Updated"
            print(f"{action} latest publication for {species_name}: {latest_pub['doi']}", file=os.sys.stderr)

        # Print fetch_pmc.sh logs
        if stderr.strip():
            print(stderr, file=os.sys.stderr)

    except subprocess.CalledProcessError as e:
        print(f"Error fetching PMC for {species_name}:", file=os.sys.stderr)
        print("stdout:", e.stdout.decode("utf-8", errors="replace"), file=os.sys.stderr)
        print("stderr:", e.stderr.decode("utf-8", errors="replace"), file=os.sys.stderr)