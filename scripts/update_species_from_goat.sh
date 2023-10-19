#!/bin/bash
export t=`date +%s`
cd /home/www/resistome.cnag.cat/erga/scripts/inputs;
/home/www/resistome.cnag.cat/erga-dev/scripts/fetch_BGE_species.pl > goat.$t.tsv
python3 /home/www/resistome.cnag.cat/erga-dev/scripts/import_target_species_no_team.py goat.$t.tsv
