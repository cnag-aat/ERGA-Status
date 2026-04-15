import django
django.setup()

from status.models import *
import csv
import argparse
import requests
import logging
import re
from unicodedata import normalize
from unidecode import unidecode
import json
import yaml
import urllib
from urllib import request

logging.getLogger("requests").setLevel(logging.WARNING)
urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.CRITICAL)

def parse_tree(tree):
    files = []
    directories = []
    
    for item in tree:
        if item['type'] == 'blob':  # It's a file
            files.append(item['path'])
        elif item['type'] == 'tree':  # It's a directory
            directories.append(item['path'])
    
    return files, directories

def fetch_repo_tree(owner, repo, branch='main'):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    headers = {'Accept': 'application/vnd.github+json', 'Authorization':'Bearer '+ settings.GITHUB_TOKEN}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

owner = "ERGA-consortium"
repo = "EARs"
branch = "main"

data = fetch_repo_tree(owner, repo, branch)
yaml_files = []
if data and "tree" in data:
    files, directories = parse_tree(data['tree'])
    # print("Files:")
    # print("\n".join(files))
    # print("\nDirectories:")
    # print("\n".join(directories))
    # example: Assembly_Reports/Valencia_hispanica/fValHis1/fValHis1_EAR.yaml
    for f in files:
        if re.search("^Assembly_Reports.*yaml$", f):
            yaml_files.append(f)
else:
    print("No tree data found.")

# json_data = json.loads(r.text)
# print(json_data)
#print(yaml_files)
regular_url_prefix = 'https://github.com/ERGA-consortium/EARs/blob/main/'
raw_url_prefix = 'https://raw.githubusercontent.com/ERGA-consortium/EARs/refs/heads/main/'
for yf in yaml_files:
    print(yf)
"""     
    pdf = re.sub(r'yaml$','pdf',yf)
    x = request.urlopen(raw_url_prefix + yf)
    ear_yaml = yaml.safe_load(x)
    print(ear_yaml)
    EAR_pdf = regular_url_prefix + pdf
    print(ear_yaml['Species'])
    assembly_project= AssemblyProject.objects.all().filter(species__scientific_name=ear_yaml['Species']).first()
    if assembly_project:
        print(assembly_project)
        assembly_object = Assembly.objects.filter(project=assembly_project).first()
        if assembly_object is None:
            assembly_object = Assembly.objects.create(project=assembly_project)
        print('assmebly object: ' + str(assembly_object.project))
        for m in ear_yaml['Metrics']:
            print(m)
            if re.match(r'^Pre-curation',m):
                continue
            if m == 'Curated hap1':
                assembly_object.type = 'Hap1'
            elif m == 'Curated pr':
                assembly_object.type = 'Primary'
            elif m == 'Curated collapsed':
                assembly_object.type = 'Primary'
            if ear_yaml['Metrics'][m].get('Total bp'):
                assembly_object.span = re.sub(r',','',ear_yaml['Metrics'][m]['Total bp'])
            if ear_yaml['Metrics'][m].get('Scaffold N50'):
                assembly_object.scaffold_n50 = re.sub(r',','',ear_yaml['Metrics'][m]['Scaffold N50'])
            if ear_yaml['Metrics'][m].get('Contig N50'):
                assembly_object.contig_n50 = re.sub(r',','',ear_yaml['Metrics'][m]['Contig N50'])
            if ear_yaml['Metrics'][m].get('QV'):
                assembly_object.qv = ear_yaml['Metrics'][m]['QV']
            if ear_yaml['BUSCO'].get('ver') is not None and re.search(r'^\d',ear_yaml['BUSCO']['ver']):
                busco_version = ear_yaml['BUSCO']['ver']
                bv, created = BUSCOversion.objects.get_or_create(version=busco_version)
                assembly_object.busco_version = bv
            if ear_yaml['BUSCO'].get('lineage') is not None and re.search(r'odb',ear_yaml['BUSCO']['lineage']):
                busco_db = ear_yaml['BUSCO']['lineage']
                bdb, created = BUSCOdb.objects.get_or_create(db=busco_db)
                assembly_object.busco_db = bdb
            if (ear_yaml['Metrics'][m].get('BUSCO sing.')):
                print('making busco string')
                busco_s = re.sub(r'%','',ear_yaml['Metrics'][m]['BUSCO sing.'])
                busco_d = re.sub(r'%','',ear_yaml['Metrics'][m]['BUSCO dupl.'])
                busco_f = re.sub(r'%','',ear_yaml['Metrics'][m]['BUSCO frag.'])
                busco_m = re.sub(r'%','',ear_yaml['Metrics'][m]['BUSCO miss.'])
                assembly_object.busco  = 'C:{complete:.1f}%[S:{single:.1f}%,D:{duplicate:.1f}%],F:{fragmented:.1f}%,M:{missing:.1f}%'.format(complete = float(busco_s)+float(busco_d), single = float(busco_s), duplicate = float(busco_d), fragmented = float(busco_f), missing = float(busco_m))
        assembly_object.save()
 """


        #'Curated collapsed'
    #print(assembly_object)

    # description = models.CharField(null=True, blank=True, max_length=100)
    # pipeline = models.ForeignKey(AssemblyPipeline, on_delete=models.SET_NULL, null=True, verbose_name="Assembly pipeline", blank=True )
    # options = models.TextField(max_length=1000,blank=True, null=True, verbose_name="Main options if not default")
    # type = models.CharField(max_length=20, help_text='Type of assembly', choices=ASSEMBLY_TYPE_CHOICES, default='Primary')
    # span = models.BigIntegerField(null=True, blank=True, verbose_name="Assembly span")
    # contig_n50 = models.BigIntegerField(null=True, blank=True, verbose_name="Contig N50")
    # scaffold_n50 = models.BigIntegerField(null=True, blank=True, verbose_name="Scaffold N50")
    # chromosome_level =  models.NullBooleanField(blank=True, null=True, verbose_name="Chr level")
    # percent_placed = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Pct. placed")
    # busco = models.CharField(null=True, blank=True, max_length=60, verbose_name="BUSCO")
    # busco_db = models.ForeignKey(BUSCOdb, on_delete=models.SET_NULL, null=True, verbose_name="BUSCO db", blank=True)
    # busco_version = models.ForeignKey(BUSCOversion, on_delete=models.SET_NULL, null=True, verbose_name="BUSCO version", blank=True)
    # qv = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="QV")
    # report = models.URLField(max_length = 400, null=True, blank=True)
    # accession = models.CharField(max_length=12,null=True, blank=True, verbose_name="Project Accession")
    # gca = models.CharField(max_length=20,null=True, blank=True, verbose_name="GCA")
    # last_updated = models.DateField(null=True, blank=True)
    # version = models.IntegerField(default=1)