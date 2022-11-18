#from datetime import datetime
import os
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


# def load_FAERS(path):
#     f.load_cache(path)
#     return f.data, f.labels


@app.route('/')
def main():
    levels = {'DRUG': 'prod_ai', 'REAC': 'pt'}
    f._load_pickles(levels, pkl_dir)
    sammary = {
        'year': '2015-19',
        'n_cases': f.DRUG.shape[0],
        'n_drugs': f.DRUG.shape[1],
        'n_reacs': f.REAC.shape[1],
        }

    return render_template('main_test.html', sammary=sammary, 
                           levels=levels, drug_list=f.drug_labels, reac_list=f.reac_labels)


@app.route('/levels', methods=['POST'])
def switch_levels():
    drug_level = request.form['drug']
    reac_level = request.form['reac']
    levels = {'DRUG': drug_level, 'REAC': reac_level}
    f._load_pickles(levles, pkl_dir)
    return_json = {
            'drug_list': f.drug_labels,
            'reac_list': f.reac_lavels,
            }
    #return jsonify
    

@app.route('/level', methods=['get'])
def change_level():
    drug_level = request.args.get('drug')
    reac_level = request.args.get('reac')
    levels = {'DRUG': drug_level, 'REAC': reac_level}
    f._load_pickles(levels, pkl_dir)
    sammary = {
        'year': '2015-19',
        'n_cases': f.DRUG.shape[0],
        'n_drugs': f.DRUG.shape[1],
        'n_reacs': f.REAC.shape[1],
        }
    return render_template('main_test.html', sammary=sammary, 
                           levels=levels, drug_list=f.drug_labels, reac_list=f.reac_labels)

@app.route('/result', methods=['get'])
def result():
#     message = f.drug_labels
    drug = request.args.get('drug')
    reac = request.args.get('reac')
    ftype = request.args.get('ftype')
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
    fname = 'out/' + drug[:50] + '_' + reac
    
    if ftype == 'xlsx':
        fname = fname + '.xlsx'
        result.to_excel(fname) 
        return send_file(fname, as_attachment=True, mimetype=XLSX_MIMETYPE)
    else:
        fname = fname + '.csv'
        result.to_csv(fname)
        return send_file(fname, as_attachment=True, mimetype='text/csv')
    
#     os.remove(fname)


if __name__ == '__main__':
    pkl_dir = 'data/'
    f = FAERS(pkl_dir)
#     data, labels = load_FAERS(FAERS_path)
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)
