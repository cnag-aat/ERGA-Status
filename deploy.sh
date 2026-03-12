#!/bin/bash

source /home/talioto/setup_cbp.sh
# cp /home/www/resistome.cnag.cat/erga-dev/erga/urls.py /home/www/resistome.cnag.cat/erga/erga/ 
# cp /home/www/resistome.cnag.cat/erga-dev/erga/templates/base.html /home/www/resistome.cnag.cat/erga/erga/templates/base.html
# cp /home/www/resistome.cnag.cat/erga-dev/static/*.css /home/www/resistome.cnag.cat/incredible/deployment/static/css/           
# cp /home/www/resistome.cnag.cat/erga-dev/static/species_example.csv /home/www/resistome.cnag.cat/incredible/deployment/static/examples/           
# cp /home/www/resistome.cnag.cat/erga-dev/status/*py /home/www/resistome.cnag.cat/erga/status/
# cp /home/www/resistome.cnag.cat/erga-dev/status/templates/*html /home/www/resistome.cnag.cat/erga/status/templates/
# cp /home/www/resistome.cnag.cat/erga-dev/status/templates/status/*html /home/www/resistome.cnag.cat/erga/status/templates/status/
python3 manage.py makemigrations
python3 manage.py migrate
sudo /usr/bin/systemctl restart httpd
