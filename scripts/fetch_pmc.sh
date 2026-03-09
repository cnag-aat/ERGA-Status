#!/usr/bin/env bash

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 \"PMC search query\" [retmax]" >&2
    exit 1
fi

QUERY_RAW="$1"
RETMAX="${2:-10000}"
EMAIL="erga-gtc@gmail.com"

QUERY_FULL="${QUERY_RAW} AND (open_access[filter] OR author_manuscript[filter])"

# URL encode safely
QUERY_ENC=$(python3 - <<EOF
import urllib.parse
print(urllib.parse.quote_plus("""$QUERY_FULL"""))
EOF
)

echo "Searching PMC for: $QUERY_RAW" >&2

# -------------------------
# eSearch
# -------------------------
SEARCH_JSON=$(curl -sL \
  -H "User-Agent: pmc-fetch-script/1.0 (${EMAIL})" \
  "https://eutils.ncbi.nlm.nih.gov/eutils/esearch.fcgi?db=pmc&retmax=${RETMAX}&term=${QUERY_ENC}&format=json")

IDLIST=$(echo "$SEARCH_JSON" | jq -r '.esearchresult.idlist[]?')

if [ -z "$IDLIST" ]; then
    echo "No PMC IDs found." >&2
    exit 0
fi

echo "Found $(echo "$IDLIST" | wc -l) PMC IDs." >&2

# -------------------------
# eSummary → TSV to STDOUT
# -------------------------

IDS_COMMA=$(echo "$IDLIST" | paste -sd "," -)

SUMMARY_JSON=$(curl -sL \
  -H "User-Agent: pmc-fetch-script/1.0 (${EMAIL})" \
  "https://eutils.ncbi.nlm.nih.gov/eutils/esummary.fcgi?db=pmc&id=${IDS_COMMA}&format=json")

# TSV header
echo -e "PMCID\tDOI\tTitle\tJournal\tPublicationDate"

echo "$SUMMARY_JSON" | jq -r '
  .result
  | to_entries[]
  | select(.key != "uids")
  | .value as $v
  | [
      ($v.articleids[]? | select(.idtype=="pmcid") | .value),
      ($v.articleids[]? | select(.idtype=="doi") | .value) // "",
      ($v.title // ""),
      ($v.fulljournalname // ""),
      ($v.pubdate // "")
    ]
  | @tsv
'

# -------------------------
# Download latest version only
# -------------------------

for ID in $IDLIST; do
    PMCID="PMC${ID}"
    echo "Checking versions for ${PMCID}..." >&2

    VERSION_JSON=$(aws s3api list-objects-v2 \
        --no-sign-request \
        --bucket pmc-oa-opendata \
        --prefix "${PMCID}." \
        --delimiter "/" \
        --query "CommonPrefixes[].Prefix" \
        --output json)

    # Extract valid version strings safely
    VERSIONS=$(echo "$VERSION_JSON" | jq -r '
        .[]
        | select(test("^PMC[0-9]+\\.[0-9]+/$"))
        | rtrimstr("/")
    ')

    if [ -z "$VERSIONS" ]; then
        echo "  No downloadable versions found." >&2
        continue
    fi

    # Select highest numeric version
    LATEST=$(echo "$VERSIONS" \
        | sort -t'.' -k2,2n \
        | tail -n1)

    # Safety check
    if [[ ! "$LATEST" =~ ^PMC[0-9]+\.[0-9]+$ ]]; then
        echo "  Skipping malformed prefix: $LATEST" >&2
        continue
    fi

    echo "  Downloading latest version: ${LATEST}" >&2

    # Clean partial directory if exists
    if [ -d "$LATEST" ]; then
        echo "  Removing existing directory $LATEST to avoid corruption." >&2
        rm -rf "$LATEST"
    fi

    mkdir -p "$LATEST"

    if ! aws s3 cp --recursive \
        --no-sign-request \
        "s3://pmc-oa-opendata/${LATEST}/" \
        "${LATEST}/" >&2; then
        echo "  Download failed. Cleaning up $LATEST." >&2
        rm -rf "$LATEST"
    fi
done

echo "Done." >&2