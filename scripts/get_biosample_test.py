#!/usr/bin/env python3
import requests
import logging
import argparse

COPO_URL = "https://copo-project.org/api"
CBP_URL = "https://dades.biogenoma.cat/api/biosamples?taxid__in={taxid}"
ENA_BIOSAMPLES_URL = "https://www.ebi.ac.uk/biosamples/samples"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Flatten characteristics with pipe-separated text handling ---
def flatten_characteristics(characteristics):
    flat_chars = {}
    for key, values in characteristics.items():
        if isinstance(values, list):
            texts = [v.get("text") for v in values if "text" in v]
            if not texts:
                flat_chars[key] = None
            elif len(texts) == 1:
                if "|" in texts[0]:
                    flat_chars[key] = [t.strip() for t in texts[0].split("|")]
                else:
                    flat_chars[key] = texts[0]
            else:
                all_values = []
                for t in texts:
                    if "|" in t:
                        all_values.extend([x.strip() for x in t.split("|")])
                    else:
                        all_values.append(t)
                flat_chars[key] = all_values
        else:
            flat_chars[key] = values
    return flat_chars

# --- ENA fetch ---
def fetch_biosample_metadata(accession):
    if not accession:
        return None
    url = f"{ENA_BIOSAMPLES_URL}/{accession}?format=json"
    logger.info(f"Retrieving ENA BioSamples metadata for {accession}")
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        characteristics = flatten_characteristics(data.get("characteristics", {}))
        return {
            "accession": data.get("accession"),
            "name": data.get("name"),
            "organism": characteristics.get("organism") or data.get("organism"),
            "tax_id": data.get("taxId"),
            "collection_date": characteristics.get("collection date") or data.get("submitted"),
            "country": characteristics.get("geographic location (country and/or sea)"),
            "characteristics": characteristics
        }
    except Exception as e:
        logger.warning(f"ENA BioSamples query failed for {accession}: {e}")
        return None

# --- COPO ---
def get_copo_samples_by_taxid(taxid):
    url = f"{COPO_URL}/sample/taxon_id/{taxid}"
    logger.info(f"Querying COPO for taxid {taxid}")
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
    except Exception as e:
        logger.error(f"COPO query failed: {e}")
        return []

    resp = r.json()
    biosamples = []
    for record in resp.get("data", []):
        purpose = record.get("PURPOSE_OF_SPECIMEN", "")
        if "BARCODING" in purpose or "RESEQUENCING" in purpose:
            continue
        accession = record.get("SAMPLE_ACCESSION") or record.get("biosampleAccession")
        if accession:
            biosamples.append({"accession": accession, "status": "accepted"})
    return biosamples

# --- CBP ---
def get_cbp_samples_by_taxid(taxid):
    url = CBP_URL.format(taxid=taxid)
    logger.info(f"Querying CBP portal for taxid {taxid}")
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
    except Exception as e:
        logger.error(f"CBP query failed: {e}")
        return []

    resp = r.json()
    biosamples = []
    for record in resp.get("data", []):
        accession = record.get("metadata", {}).get("External Id") or record.get("accession")
        if accession:
            biosamples.append({"accession": accession, "status": "accepted"})
    return biosamples

# --- Main ---
def main():
    parser = argparse.ArgumentParser(description="Fetch ENA metadata for a given taxid/project")
    parser.add_argument("--taxid", type=int, required=True, help="NCBI TaxID to query")
    parser.add_argument("--project", choices=["ERGA", "CBP"], required=True, help="Project: ERGA or CBP")
    args = parser.parse_args()

    if args.project == "ERGA":
        samples = get_copo_samples_by_taxid(args.taxid)
    else:
        samples = get_cbp_samples_by_taxid(args.taxid)

    if not samples:
        logger.warning(f"No samples found for taxid {args.taxid} in project {args.project}")
        return

    logger.info(f"Found {len(samples)} samples for project {args.project}")
    for s in samples:
        meta = fetch_biosample_metadata(s["accession"])
        if meta:
            logger.info(f"ENA Metadata for {s['accession']}: {meta}")
        else:
            logger.warning(f"No metadata returned for {s['accession']}")

if __name__ == "__main__":
    main()