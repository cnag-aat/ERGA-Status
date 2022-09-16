#! /usr/bin/env python3

import argparse
import unicodedata
import json
import urllib.request
import os
import pandas as pd
import collections as c

def arg_parse():
    opt = argparse.ArgumentParser('Get LIMS info')
    opt.add_argument(
        '-s',
        help='subproject/s',
        dest='subproject',
        nargs='+'
    )
    opt.add_argument(
        "--link",
        "-l",
        help="Create SymLink under ./SEX/",
        action='store_true',
        dest="link"
    )
    opt.add_argument(
        "--barcode",
        "-b",
        help="barcode",
        dest="barcode",
        nargs="+",
        default="ALL"
    )
    opt.add_argument(
        '-f',
        help="Force links.",
        dest="force",
        action="store_true"
    )
    opt.add_argument(
            "--sc",
            help="Specifies it will be used in a single cell project",
            action="store_true",
            dest="sc",
            default=False
            )

    return opt.parse_args()

HEADERS = {
    'Authorization':'ApiKey talioto:c20c7de364c4e00ae2fd9df3717b0a98365bc916',
    'Content-Type': 'application/json'
}

URLS={
    'ip':'http://172.16.10.22/',
    "root":"lims/api/seq",
    'subproject':"subproject/?format=json&limit=0"\
        "&subproject_name={subproject}",
    "sample":"sample/?format=json&limit=0&"\
            "subprojects__subproject_name={subproject}",
    "library":"library/?format=json&sample__barcode={barcode}"\
                "&subprojects__subproject_name={subproject}",
    "LaneFlowcell":"lane/?format=json&limit=0&loadedwiths__library__name={library}"\
                    "&__sample__barcode={barcode}",
    "SOP":"sop?format=json&limit=0&name={sop}",
    'uri':'{uri}/?format=json&limit=0',
    'uri_raw': '{uri}',
    'fli':'flowcell_lane_index/?format=json&limit=0&library__subprojects__subproject_name={subproject}'
    }

info = []
sampleNum = {}

class entry_sample:
    def __init__(self):
        self.barcode = ''
        self.sample = ''
        self.lib = ''
        self.fc = ''
        self.lane = ''
        self.idx = ''
        self.sex = ''
        self.type = ''
        self.organism = ''
        self.passfail = ''
        self.sop = ''
        self.data_sent = ''
        self.sampleNum = ''


    def link(self, sc=False):
        pair = ['1']
        source1 = '/project/production/fastq/{fc}/{lane}/fastq/{fc}_{lane}_{idx}_{pair}.fastq.gz'
        source2 = '/scratch/project/production/fastq/{fc}/{lane}/fastq/{fc}_{lane}_{idx}_{pair}.fastq.gz'
        sourceI2 = '/scratch/project/production/fastq/{fc}/{lane}/fastq/{fc}_{lane}_{idx}_UMI2.fastq.gz'

        destI2 = False
        if sc:
            dest = '{sex}/{barcode}_S'+str(self.sampleNum)+'_L00{lane}_R{pair}_001.fastq.gz'
            destI2 = '{sex}/{barcode}_S'+str(self.sampleNum)+'_L00{lane}_I2_001.fastq.gz'
        else:
            dest = '{sex}/{barcode}_{lib}_{flowcell}_{lane}_{idx}_{pair}.fastq.gz'

        if os.path.exists(source1.format(fc=self.fc, lane=self.lane,
                                          idx=self.idx, pair=1)
                          ):
            source = source1
        else:
            source = source2

        if os.path.exists(source.format(fc=self.fc, lane=self.lane,
                                        idx=self.idx, pair=2)
                          ):
            pair = ['1', '2']
        for i in pair:
            if not os.path.isdir(self.sex):
                os.mkdir(self.sex)
            if not os.path.exists(
                    dest.format(
                    flowcell=self.fc,
                    sex=self.sex,
                    barcode=self.barcode,
                    lib=self.lib,
                    lane=self.lane,
                    idx=self.idx,
                    pair=i)
            ):
                os.symlink(source.format(fc=self.fc, lane=self.lane,
                                        idx=self.idx, pair=i),
                        dest.format(flowcell=self.fc, sex=self.sex,
                                    barcode=self.barcode, lib=self.lib,
                                    lane=self.lane, idx=self.idx,
                                    pair=i)
                        )
        if destI2:
            if not os.path.exists(
                    destI2.format(
                    flowcell=self.fc,
                    sex=self.sex,
                    barcode=self.barcode,
                    lib=self.lib,
                    lane=self.lane,
                    idx=self.idx)
            ):
                os.symlink(sourceI2.format(fc=self.fc, lane=self.lane,
                                        idx=self.idx),
                        destI2.format(flowcell=self.fc, sex=self.sex,
                                    barcode=self.barcode, lib=self.lib,
                                    lane=self.lane, idx=self.idx,
                                    )
                        )

    def __str__(self):
        #sex_str = {"0":'Unknown',"1":'Male',"2":'Female'}
        return '\t'.join(map(str, [self.barcode, self.sample, self.lib,
                                   self.fc, self.lane, self.idx, self.sex,
                                   self.type, self.organism, self.sop,
                                   self.passfail]))

    def get_dict(self):
        d = c.OrderedDict()
        d["barcode"] = self.barcode
        d["sample"] = self.sample
        d["library"] = self.lib
        d["flowcell"] = self.fc
        d["lane"] = self.lane
        d["index"] = self.idx
        d["sex"] = self.sex
        d["type"] = self.type
        d["organism"] = self.organism
        d["status"] = self.passfail
        d["sop"] = self.sop
        d["data_sent"] = self.data_sent
        return d

def get_json(key,**kwargs):
    if not 'uri' in key:
        url=URLS['ip']+"/"+URLS['root']+"/"+URLS[key].format(**kwargs)
    else:
        url=URLS['ip']+"/"+URLS[key].format(**kwargs)
    req = urllib.request.Request(url, headers=HEADERS)
    reponse=urllib.request.urlopen(req)
    return json.loads(reponse.read().decode('utf-8'))

def get_fli(subproject):
    """
Get full output from FLI
    """
    tmp = get_json('fli', subproject=subproject)
    fli = []
    while not tmp['meta']['next'] is None:
        fli.extend(tmp['objects'])
        tmp = get_json('uri_raw', uri=tmp['meta']['next'])
    fli.extend(tmp['objects'])

    return fli

def get_sample_info(subproject, barcode='ALL'):
    global info
    global sampleNum

    info = []
    sb = get_json('subproject', subproject=subproject)['objects'][0]
    app = get_json('uri', uri=sb['application']).get('name',' NA')
    fli = get_fli(subproject=subproject)
    for f in fli:
        object = entry_sample()
        object.type = app
#        object.idx = f['index_name']
#        if f['index_name_2']:
#            if object.idx != f['index_name_2']:
#                object.idx = object.idx+"-"+f['index_name_2']
        object.fc = f['flowcell_name']
        object.lane = f['lane_number']
        object.passfail = get_json('uri', uri=f['passfail'])['status']
        libj = get_json('uri', uri=f['library'])
        object.lib = libj['name']
        object.idx = libj["multiplex_index_compact_name"]
        try:
            object.sop = libj['sop']['description']
        except:
            object.sop='NA'
        samplej = get_json('uri', uri=libj['sample'])
        object.sex = samplej['sex']
        object.barcode = samplej['barcode']
        object.sample = samplej['name']
        object.organism = samplej['organism']['name']
        object.data_sent = f['data_sent']
        if object.barcode in sampleNum:
            sampleNum[object.barcode]+=1
        else:
             sampleNum[object.barcode]=1
        object.sampleNum = sampleNum[object.barcode]

        if (barcode=='ALL') or (object.barcode in barcode):
            info.append(object)
    return info


if __name__ == '__main__':
    args = arg_parse()
    table = []
    for s in args.subproject:
        table.extend(get_sample_info(s, args.barcode))
    print(pd.DataFrame([i.get_dict() for i in table]).to_string())
    if args.link:
        if args.force:
            [i.link(sc=args.sc) for i in table ]
        else:
            [i.link(sc=args.sc) for i in table if (i.get_dict()['status']=="pass" and i.get_dict()['data_sent']) ]
