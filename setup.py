import glob
import os
import logging
import requests
from requests.exceptions import RequestException
import zipfile
from tqdm import tqdm

import config
from faerstools2 import FAERS

logger = logging.getLogger(__name__)

def check_dir(dir:str):
    if not os.path.isdir(dir):
        os.makedirs(dir)
        
def check_request(url):
    r = requests.get(url, stream=True)
    try:
        r.raise_for_status()
        return True
    except RequestException as e:
        logger.exception("request failed. error=(%s)", e.response.text)
        return False

def download(url:str, filepath:str):
    r = requests.get(url, stream=True)
    
    total_size = int(r.headers.get('content-length', 0));
    chunk_size = 32 * 1024
    downloaded = 0

    print('Download: ' + url)
    pbar = tqdm(total=total_size, unit='B', unit_scale=True)
    with open(filepath, 'wb') as f:
            for data in r.iter_content(chunk_size):
                f.write(data)
                downloaded+=len(data)
                pbar.update(chunk_size)

    if total_size != 0 and downloaded != total_size:
        print("ERROR, download failed")
        
def unzip(filepath:str, out_dir:str):
    print('extracting files from {}'.format(filepath))
    with zipfile.ZipFile(filepath) as zf:
        files = zf.namelist()
        DEMO = [file for file in files if 'DEMO' in file and file.endswith('.txt')]
        DRUG = [file for file in files if 'DRUG' in file and file.endswith('.txt')] 
        REAC = [file for file in files if 'REAC' in file and file.endswith('.txt')]
        zf.extractall(path=out_dir ,members=DEMO+DRUG+REAC)

def rename_dir(dir:str, newname:str):
    dirname_upper = os.path.join(dir, 'ASCII')
    dirname_lower = os.path.join(dir, 'ascii')
    new_dirname = os.path.join(dir, newname)
    if os.path.isdir(dirname_upper):
        os.rename(dirname_upper, new_dirname)
    else:
        os.rename(dirname_lower, new_dirname)
    if os.path.exists(os.path.join(new_dirname, 'DEMO18Q1_new.txt')):
        os.rename(os.path.join(new_dirname, 'DEMO18Q1_new.txt'), os.path.join(new_dirname, 'DEMO18Q1.txt'))

def rename_files(dir:str):
    '''
    DEMO18Q1_new.txtのように"_new"が付いたファイルがあるので、"_new"を削除する
    '''
    files = glob.glob(os.path.join(dir, '**/*_new.txt'), recursive=True)
    for file in files:
        os.rename(file, file.replace('_new', ''))

def setup_FAERS():
    FAERS(out_path).load_files(params)
        
if __name__ == '__main__':
    
    faers_url = config.FAERS_URL
    # years = config.YEARS
    quarters = config.QUARTERS
    download_dir = config.DOWNLOAD_DIR
    unpack_dir = config.UNPACK_DIR
    cache_dir = config.CACHE_DIR
    params = config.setup_params

    check_dir(download_dir)
    check_dir(unpack_dir)
    
    # for y in years:
    for q in quarters:
        filename = 'faers_ascii_' + q + '.zip'
        url = os.path.join(faers_url, filename)
        filepath = os.path.join(download_dir, filename)
        out_path = os.path.join(unpack_dir, q)
        if os.path.exists(out_path):
            print('"{}" already esists. Skip downloading.'.format(out_path))
        elif not os.path.exists(out_path) and check_request(url):
            download(url, filepath)
            unzip(filepath, unpack_dir)
            rename_dir(unpack_dir, q)

    rename_files(unpack_dir)
    print('Downloading completed:)')
    
    # FAERS setup
    pkl_dir = os.path.join(cache_dir, quarters[0] + '-' + quarters[-1])
    FAERS(pkl_dir).load_files(params)