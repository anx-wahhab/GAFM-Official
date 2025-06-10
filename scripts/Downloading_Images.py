import os
import pandas as pd
from tqdm.notebook import tqdm
from Scraper import GoogleEarthScraper

BASE_DIR = '..'
DISTRICT_DIR = os.path.join(BASE_DIR, 'data', 'images')


def download_images(df):

    districts = df['district'].unique()

    for district in districts:
        dist_imgs_path = os.path.join(os.path.join(DISTRICT_DIR, district))
        os.makedirs(dist_imgs_path, exist_ok=True)
        # drops what is already downloaded
        already_downloaded = os.listdir(dist_imgs_path)

        already_downloaded = list(set(already_downloaded).intersection(set(df['cluster_name'])))
        print('Already downloaded ', (len(already_downloaded)))
        df = df.set_index('cluster_name').drop(already_downloaded).reset_index()
        print('Need to download ' + str(len(df)))

        scraper = GoogleEarthScraper()
        scraper.initiate_browser()

        for _, r in tqdm(df.iterrows(), total=df.shape[0]):
            lat = r.cluster_lat
            lon = r.cluster_long

            image_save_path = os.path.join(DISTRICT_DIR, district, r.cluster_name)
            scraper.scrape([lat, lon], img_path=image_save_path)

        scraper.quit_browser()


if __name__ == '__main__':
    df_path = os.path.join('..', 'data', 'processed', 'finalized_df.csv')
    df_ = pd.read_csv(df_path)
    download_images(df_)
