#!/usr/bin/env python3
"""
Convert channels JSON to M3U playlist grouped by country
"""
import json
import requests
from collections import defaultdict

# Country code to country name mapping
COUNTRY_NAMES = {
        'us': 'United States', 'gb': 'United Kingdom', 'es': 'Spain', 
        'de': 'Germany', 'fr': 'France', 'it': 'Italy', 'br': 'Brazil', 
        'ar': 'Argentina', 'mx': 'Mexico', 'ca': 'Canada', 'au': 'Australia', 
        'za': 'South Africa', 'in': 'India', 'pk': 'Pakistan', 'bd': 'Bangladesh', 
        'ae': 'UAE', 'sa': 'Saudi Arabia', 'eg': 'Egypt', 'tr': 'Turkey', 
        'ru': 'Russia', 'pl': 'Poland', 'nl': 'Netherlands', 'be': 'Belgium', 
        'se': 'Sweden', 'no': 'Norway', 'dk': 'Denmark', 'fi': 'Finland', 
        'gr': 'Greece', 'pt': 'Portugal', 'ro': 'Romania', 'hr': 'Croatia', 
        'rs': 'Serbia', 'bg': 'Bulgaria', 'ua': 'Ukraine', 'cz': 'Czech Republic',
        'sk': 'Slovakia', 'hu': 'Hungary', 'at': 'Austria', 'ch': 'Switzerland',
        'ie': 'Ireland', 'il': 'Israel', 'jp': 'Japan', 'kr': 'South Korea',
        'cn': 'China', 'th': 'Thailand', 've': 'Venezuela', 'cl': 'Chile',
        'co': 'Colombia', 'pe': 'Peru', 'ec': 'Ecuador', 'uy': 'Uruguay',
        'bo': 'Bolivia', 'py': 'Paraguay', 'cr': 'Costa Rica', 'pa': 'Panama',
        'do': 'Dominican Republic', 'pr': 'Puerto Rico', 'cu': 'Cuba',
        'jm': 'Jamaica', 'tt': 'Trinidad and Tobago', 'ke': 'Kenya',
        'ng': 'Nigeria', 'gh': 'Ghana', 'tz': 'Tanzania', 'ug': 'Uganda',
        'et': 'Ethiopia', 'ma': 'Morocco', 'dz': 'Algeria', 'tn': 'Tunisia',
        'ly': 'Libya', 'sd': 'Sudan', 'iq': 'Iraq', 'sy': 'Syria',
        'jo': 'Jordan', 'lb': 'Lebanon', 'kw': 'Kuwait', 'qa': 'Qatar',
        'bh': 'Bahrain', 'om': 'Oman', 'ye': 'Yemen', 'ir': 'Iran',
        'af': 'Afghanistan', 'uz': 'Uzbekistan', 'kz': 'Kazakhstan',
        'nz': 'New Zealand', 'ph': 'Philippines', 'vn': 'Vietnam',
        'id': 'Indonesia', 'my': 'Malaysia', 'sg': 'Singapore'
}

def fetch_json(url):
    """Fetch JSON data from URL"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def group_channels_by_country(channels):
    """Group channels by country code"""
    grouped = defaultdict(list)
    for channel in channels:
        category = channel.get('category', 'Unknown')
        grouped[category].append(channel)
    return grouped

def generate_m3u(grouped_channels, output_file='playlist.m3u'):
    """Generate M3U playlist file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        
        # Sort countries alphabetically
        for country_code in sorted(grouped_channels.keys()):
            channels = grouped_channels[country_code]
            country_name = COUNTRY_NAMES.get(country_code, country_code)
            
            # Sort channels by name within each country
            channels.sort(key=lambda x: x.get('name', ''))
            
            for channel in channels:
                name = channel.get('name', 'Unknown')
                logo = channel.get('logo', '')
                stream_url = channel.get('stream_url', '')
                
                # Write M3U entry
                f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{country_name}",{name}\n')
                f.write(f'{stream_url}\n')
    
    print(f'✅ M3U playlist generated: {output_file}')

def main():
    """Main function"""
    json_url = 'https://raw.githubusercontent.com/tutw/platinsport-m3u-updater/ee93a8c9fa81a2b6e6d3d6261a6fbd1affeac67d/channels_final.json'
    
    print('📡 Fetching JSON data...')
    channels = fetch_json(json_url)
    print(f'✅ Fetched {len(channels)} channels')
    
    print('📊 Grouping channels by country...')
    grouped = group_channels_by_country(channels)
    print(f'✅ Grouped into {len(grouped)} countries')
    
    print('📝 Generating M3U playlist...')
    generate_m3u(grouped, 'playlist.m3u')
    
    # Print statistics
    print('\n📈 Statistics:')
    for country_code in sorted(grouped.keys()):
        country_name = COUNTRY_NAMES.get(country_code, country_code)
        count = len(grouped[country_code])
        print(f'  {country_name} ({country_code}): {count} channels')

if __name__ == '__main__':
    main()
