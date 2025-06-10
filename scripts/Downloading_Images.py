import os
import pandas as pd
import requests
from tqdm import tqdm

BASE_DIR = '..'
DISTRICT_DIR = os.path.join(BASE_DIR, 'data', 'images')

# Write your API key
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
if not API_KEY:
    raise ValueError("Please set the GOOGLE_MAPS_API_KEY environment variable.")


def download_image(url, save_path):
    """Download an image from a URL and save it to the specified path."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
        else:
            print(f"Failed to download image: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error downloading image: {e}")


def download_images(df):
    """Process each district and download missing satellite images using Google Maps Static API."""
    districts = df['district'].unique()

    for district in districts:
        dist_imgs_path = os.path.join(DISTRICT_DIR, district)
        os.makedirs(dist_imgs_path, exist_ok=True)

        # Get list of already downloaded images (remove .png extension)
        already_downloaded = [f for f in os.listdir(dist_imgs_path) if f.endswith('.png')]
        already_downloaded = [f[:-4] for f in already_downloaded]
        already_downloaded = list(set(already_downloaded).intersection(set(df['cluster_name'])))
        print(f'Already downloaded for {district}: {len(already_downloaded)}')

        # Filter out clusters that are already downloaded
        df_district = df[df['district'] == district]
        df_to_download = df_district[~df_district['cluster_name'].isin(already_downloaded)]
        print(f'Need to download for {district}: {len(df_to_download)}')

        # Download images for remaining clusters
        for _, r in tqdm(df_to_download.iterrows(), total=len(df_to_download)):
            lat = r.cluster_lat
            lon = r.cluster_long
            cluster_name = r.cluster_name

            # Construct Google Maps Static API URL
            url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=17&size=640x640&maptype=satellite&format=png&key={API_KEY}"
            image_save_path = os.path.join(dist_imgs_path, f"{cluster_name}.png")
            download_image(url, image_save_path)


if __name__ == '__main__':
    df_path = os.path.join('..', 'data', 'processed', 'finalized_df.csv')
    df_ = pd.read_csv(df_path)
    download_images(df_)