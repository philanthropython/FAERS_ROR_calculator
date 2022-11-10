import os
import urllib.request
import requests
import shutil
import sys
import settings
from tqdm import tqdm
from requests.exceptions import RequestException
import logging
import zipfile

faers_url = settings.FAERS_URL
years = settings.YEARS
quarters = settings.quarters
download_dir = settings.DOWNLOAD_DIR
unpack_dir = settings.UNPACK_DIR

logger = logging.getLogger(__name__)

def progress( block_count, block_size, total_size ):
    ''' コールバック関数 '''
    percentage = 100.0 * block_count * block_size / total_size
    # 改行したくないので print 文は使わない
    sys.stdout.write( "%.2f %% ( %d KB )\r"
            % ( percentage, total_size / 1024 ) )

def _progress(cnt, chunk, total):
  now = cnt * chunk
  if(now > total): now = total
  sys.stdout.write('\rdownloading {} {} / {} ({:.1%})'.format(filename, now, total, now/total))
  sys.stdout.flush()

if not os.path.exists(download_dir):
    os.mkdir(download_dir)

for y in years:
    for q in quarters:
        filename = 'faers_ascii_' + y + q + '.zip'
        url = os.path.join(faers_url, filename)
        filepath = os.path.join(download_dir, filename)
        if not os.path.exists(filepath):
            #print(url)
            #urllib.request.urlretrieve(url, filepath, _progress)
            r = requests.get(url, stream=True)
            try:
                r.raise_for_status()
            except RequestException as e:
                logger.exception("request failed. error=(%s)", e.response.text)
                continue
            #print(r.status_code())
            total_size = int(r.headers.get('content-length', 0));
            chunk_size = 32 * 1024
            downloaded = 0

            pbar = tqdm(total=total_size, unit='B', unit_scale=True)
            with open(filepath, 'wb') as f:
                    for data in r.iter_content(chunk_size):
                        f.write(data)
                        downloaded+=len(data)
                        pbar.update(chunk_size)

            if total_size != 0 and downloaded != total_size:
                print("ERROR, download failed")

        out_dir = os.path.join(unpack_dir, y+q)
        if not os.path.exists(out_dir):
            #shutil.unpack_archive(filepath, os.path.join(unpack_dir, y+qy))
            print('extracting files from {}'.format(filepath))
            with zipfile.ZipFile(filepath) as zf:
                files = zf.namelist()
                DEMO = [file for file in files if 'DEMO' in file and file.endswith('.txt')]
                DRUG = [file for file in files if 'DRUG' in file and file.endswith('.txt')] 
                REAC = [file for file in files if 'REAC' in file and file.endswith('.txt')]
                zf.extractall(path=unpack_dir ,members=DEMO+DRUG+REAC)
                txt_dir_upper = os.path.join(unpack_dir, 'ASCII')
                txt_dir_lower = os.path.join(unpack_dir, 'ascii')
                if os.path.exists(txt_dir_upper):
                    os.rename(txt_dir_upper, out_dir)
                else:
                    os.rename(txt_dir_lower, out_dir)


