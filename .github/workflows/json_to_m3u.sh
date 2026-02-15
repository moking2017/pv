#!/bin/bash
# Convert channels JSON to M3U playlist grouped by country

JSON_URL="https://raw.githubusercontent.com/tutw/platinsport-m3u-updater/ee93a8c9fa81a2b6e6d3d6261a6fbd1affeac67d/channels_final.json"
OUTPUT_FILE="playlist.m3u"

echo "📡 Fetching JSON data..."
JSON_DATA=$(curl -s "$JSON_URL")

if [ -z "$JSON_DATA" ]; then
    echo "❌ Failed to fetch JSON data"
    exit 1
fi

echo "✅ JSON data fetched successfully"
echo "📝 Generating M3U playlist..."

# Start M3U file
echo "#EXTM3U" > "$OUTPUT_FILE"

# Declare country names
declare -A COUNTRY_NAMES=(
    ["US"]="United States"
    ["GB"]="United Kingdom"
    ["ES"]="Spain"
    ["FR"]="France"
    ["DE"]="Germany"
    ["IT"]="Italy"
    ["PT"]="Portugal"
    ["BR"]="Brazil"
    ["AR"]="Argentina"
    ["MX"]="Mexico"
    ["CA"]="Canada"
    ["AU"]="Australia"
    ["NL"]="Netherlands"
    ["BE"]="Belgium"
    ["CH"]="Switzerland"
    ["AT"]="Austria"
    ["SE"]="Sweden"
    ["NO"]="Norway"
    ["DK"]="Denmark"
    ["FI"]="Finland"
    ["PL"]="Poland"
    ["CZ"]="Czech Republic"
    ["GR"]="Greece"
    ["TR"]="Turkey"
    ["RU"]="Russia"
    ["IN"]="India"
    ["CN"]="China"
    ["JP"]="Japan"
    ["KR"]="South Korea"
    ["SA"]="Saudi Arabia"
    ["AE"]="UAE"
    ["ZA"]="South Africa"
    ["EG"]="Egypt"
)

# Extract and group channels
echo "$JSON_DATA" | jq -r '.[] | @json' | while IFS= read -r channel; do
    name=$(echo "$channel" | jq -r '.name')
    logo=$(echo "$channel" | jq -r '.logo')
    category=$(echo "$channel" | jq -r '.category')
    stream_url=$(echo "$channel" | jq -r '.stream_url')
    
    # Get country name or use code if not found
    if [ -n "${COUNTRY_NAMES[$category]}" ]; then
        country="${COUNTRY_NAMES[$category]}"
    else
        country="$category"
    fi
    
    # Write M3U entry
    echo "#EXTINF:-1 tvg-logo=\"$logo\" group-title=\"$country\",$name" >> "$OUTPUT_FILE"
    echo "$stream_url" >> "$OUTPUT_FILE"
done

echo "✅ M3U playlist generated: $OUTPUT_FILE"

# Show statistics
echo ""
echo "📈 Statistics:"
echo "$JSON_DATA" | jq -r '.[].category' | sort | uniq -c | while read -r count code; do
    if [ -n "${COUNTRY_NAMES[$code]}" ]; then
        country="${COUNTRY_NAMES[$code]}"
    else
        country="$code"
    fi
    echo "  $country ($code): $count channels"
done
