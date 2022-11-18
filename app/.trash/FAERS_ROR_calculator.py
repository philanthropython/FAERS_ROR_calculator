#from datetime import datetime
import argparse, os
from flask import Flask, request, render_template, send_file, json, jsonify
import pandas as pd
import openpyxl
from faerstools2 import FAERS
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

TIME_FORMAT = '%Y%m%d_%H%M%S'

# 2007 Office system ファイル形式の MIME タイプをサーバーで登録する
# https://technet.microsoft.com/ja-jp/library/ee309278(v=office.12).aspx
XLSX_MIMETYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

levels = {'DRUG': 'prod_ai', 'REAC': 'pt'}
sammary = {}
params = {}

# def load_FAERS(path):
#     f.load_cache(path)
#     return f.data, f.labels


@app.route('/')
def main():
#     getFormValues()
    #変数を初期化する
    f._load_pickles(levels, pkl_dir)
    sammary['year'] = pkl_dir[pkl_dir.find('/')+1:pkl_dir.rfind('/')]
    sammary['n_cases'] = f.DRUG.shape[0]
    sammary['n_drugs'] = f.DRUG.shape[1]
    sammary['n_reacs'] = f.REAC.shape[1]
    params = {}

#     sammary = {
#         'year': pkl_dir[pkl_dir.find('/')+1:pkl_dir.rfind('/')],
#         'n_cases': f.DRUG.shape[0],
#         'n_drugs': f.DRUG.shape[1],
#         'n_reacs': f.REAC.shape[1],
#         }
#     sammary['n_drugs'] = f.DRUG.shape[1]
#     sammary['n_reacs'] = f.REAC.shape[1]
    
    return render_template('main.html', sammary=sammary, params=params,
                           levels=levels, drug_list=f.drug_labels, reac_list=f.reac_labels)


@app.route('/d', methods=['POST'])
def change_drug_level():
    getFormValues()
    drug_level = params['drug_level']
    params['drug_name'] = ''
    
    fname = pkl_dir + drug_level + '_labels.pkl'
    f.drug_labels = f._pickle_load(fname)
    sammary['n_drugs'] = len(f.drug_labels)
    message = sammary
    
    return render_template('main.html', sammary=sammary, params=params,
                           levels=levels, drug_list=f.drug_labels, reac_list=f.reac_labels)


@app.route('/r', methods=['POST'])
def change_reac_level():
    getFormValues()
    reac_level = params['reac_level']
    params['reac_name'] = ''

    fname = pkl_dir + reac_level + '_labels.pkl'
    f.reac_labels = f._pickle_load(fname)
    sammary['n_reacs'] = len(f.reac_labels)
    
    return render_template('main.html', sammary=sammary, params=params,
                           levels=levels, drug_list=f.drug_labels, reac_list=f.reac_labels)


@app.route('/t', methods=['POST'])
def keep_text():
    getFormValues()
    return render_template('main.html', sammary=sammary, params=params,
                           levels=levels, drug_list=f.drug_labels, reac_list=f.reac_labels)


@app.route('/result', methods=['POST'])
def result():
    getFormValues()
    levels['DRUG'] = params['drug_level']
    levels['REAC'] = params['reac_level']
    drug = params['drug_name']
    reac = params['reac_name']
    ftype = params['ftype']
    
    f._load_pickles(levels, pkl_dir)
    
    message = drug + reac
    
#     return render_template('main_test.html', sammary=None, drug_list=f.drug_labels, reac_list=f.reac_labels, message=message)

    if drug and reac:
        result = f._RORbyDrugAndReac(drug, reac, sort={'CI95max':'asc'})
    elif drug:
        result = f._RORbyDrug(drug, sort={'CI95min':'desc'})
    elif reac:
        result = f._RORbyReac(reac, sort={'CI95min':'desc'})
    else: return None
     
#     time = datetime.now().strftime(TIME_FORMAT)
    #fname = 'out/' + drug + '_' + reac + '_' + time
    fname = 'out/' + drug[:50] +'(' + levels['DRUG'] + ')' + '_' + reac + '(' + levels['REAC'] + ')'
     
    if ftype == 'xlsx':
        fname = fname + '.xlsx'
        result.to_excel(fname) 
        return send_file(fname, as_attachment=True, mimetype=XLSX_MIMETYPE)
    else:
        fname = fname + '.csv'
        result.to_csv(fname)
        return send_file(fname, as_attachment=True, mimetype='text/csv')
    
#     os.remove(fname)

def getFormValues():
    #POST通信でフォームの入力値を取得
    params['drug_level'] = request.form['drug_level']
    params['drug_name'] = request.form['drug_name']
    params['reac_level'] = request.form['reac_level']
    params['reac_name'] = request.form['reac_name']
    params['ftype'] = request.form['ftype']
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-D', '--data_dir', default='data/2015-2020', type=str, help='designate the directory which holds FAERS pickled data')
    parser.add_argument('-p', '--port', default=5000, type=int)
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()
    
    pkl_dir = args.data_dir
    if not pkl_dir[-1] == '/': pkl_dir = pkl_dir + '/'
        
    f = FAERS(pkl_dir)
#     f._load_pickles(levels, pkl_dir)
    
#     sammary['year'] = pkl_dir[pkl_dir.find('/')+1:pkl_dir.rfind('/')]
#     sammary['n_cases'] = f.DRUG.shape[0]
#     sammary['n_drugs'] = f.DRUG.shape[1]
#     sammary['n_reacs'] = f.REAC.shape[1]
    
#     data, labels = load_FAERS(FAERS_path)
    app.run(debug=args.debug, host='0.0.0.0', port=args.port, threaded=True)
