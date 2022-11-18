import os
import numpy as np
import pandas as pd
import pickle
from scipy.sparse import csr_matrix, csc_matrix

class FAERS():
    def __init__(self, pkl_dir):
        self.pkl_dir = pkl_dir
        
    
    def load_cache(self, path):
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.DRUG = data['DRUG']
        self.REAC = data['REAC']
        self.data = data['matrices']
        self.labels = data['labels']
        
            
    
    def load_files(self, params, out_dir=None):
        """
        ファイル読み込み -> キャッシュ作成
        """
        print('1: loading files...')
        
        self.data_dir = params['data_dir']
        self.quarters = params['quarters']
        self.keep = params['keep']
        ATC_path = params['ATC_path']
        MedDRA_path = params['MedDRA_path']
        if not out_dir: out_dir = self.pkl_dir
        
        self.DEMO = self._load_FAERS('DEMO', cols={'primaryid':'int32', 'caseid':'category', 'caseversion':'category'})
        self.DRUG = self._load_FAERS('DRUG', cols={'primaryid':'int32', 'prod_ai':'category'}, 
                                    sort={'primaryid':'asc', 'prod_ai':'asc'})
        self.REAC = self._load_FAERS('REAC', cols={'primaryid':'int32', 'pt':'category'}, 
                                    sort={'primaryid':'asc', 'pt':'asc'})

        self._add_ATC(ATC_path)
        self._add_MedDRA(MedDRA_path)
        
        print('2: formatting data...')
        self._format_data()
        os.makedirs(out_dir, exist_ok=True)
        self._dump_tables(out_dir)
#         self._save_cache(cache_path)
        print('3: saved caches under ' + out_dir)
        
    
    def _load_FAERS(self, tblname:str, cols:dict, sort:dict=None):
        df = pd.DataFrame()
        usecols = cols.keys()
        for q in self.quarters:
            path = os.path.join(self.data_dir, q, tblname + q.upper()[2:] + '.txt')
            print('loading "{}"'.format(path))
            # pandas version>1.2から DRUG19Q3.txt のみ Shift-JIS を指定しないと decoding error で読み込めない。とりあえず encoding_errors='ignore' でエラーを無視。
            tmp = pd.read_csv(path, delimiter='$', usecols=usecols, dtype=cols, encoding_errors='ignore')
            # The frame.append method is deprecated and will be removed from pandas in a future version.
            # df = df.append(tmp) 
            df = pd.concat([df, tmp], ignore_index=True)
            
        if sort: 
            return self.sort_df(df, sort)
        else: 
            return df
        
    
    def _add_ATC(self, ATC_path):
        ATC = pd.read_csv(ATC_path, dtype='category')
        ATC = ATC[['drug_name', 'lvl5_name', 'lvl4_name', 'lvl3_name', 'lvl2_name', 'lvl1_name']] \
             .drop_duplicates('drug_name')
        ATC.columns = ['prod_ai', 'lvl5', 'lvl4', 'lvl3', 'lvl2', 'lvl1']
        
        self.DRUG = self.DRUG.merge(ATC, on='prod_ai', how='left')
        self.DRUG['prod_ai'] = self.DRUG['prod_ai'].astype('category')


    def _add_MedDRA(self, MedDRA_path):
        MedDRA = pd.read_csv(MedDRA_path, dtype='category').rename(columns={'PT_en':'pt'})
        MedDRA = MedDRA[MedDRA['primary'] == '1'] \
             .drop(columns=['SOC_cd', 'HLGT_cd', 'HLT_cd', 'PT_cd', 'seq', 'primary'])
        
        self.REAC = self.REAC.merge(MedDRA, on='pt', how='left')
        self.REAC['pt'] = self.REAC['pt'].astype('category')

        
    def sort_df(self, df, sort:dict):
        keys = [key for key in sort]
        asc = [sort[key] == 'asc' for key in sort]
        return df.sort_values(keys, ascending=asc)    
    
    
    def _format_data(self):
        self.DRUG = self.DRUG.dropna(subset=['prod_ai'])
        
        if self.keep == 'first':
            ids_demo = self.DEMO['primaryid'][self.DEMO['caseversion'] == '1'].values
        elif self.keep == 'last':
            ids_demo = self.DEMO.sort_values(['caseid', 'caseversion']).drop_duplicates(['caseid'], keep='last')['primaryid']
        else: raise
        
        # DRUG と REAC に共通するIDだけに限定
        ids_drug = self.DRUG['primaryid'].unique()
        ids_drug = ids_drug[np.isin(ids_drug, ids_demo)]
        ids_reac = self.REAC['primaryid'].unique()
        ids_reac = ids_reac[np.isin(ids_reac, ids_demo)]
        ids_common = ids_drug[np.isin(ids_drug, ids_reac)]

        del self.DEMO
        self.DRUG = self.DRUG[self.DRUG['primaryid'].isin(ids_common)] \
                                                    .drop_duplicates(['primaryid', 'prod_ai']) \
                                                    .reset_index(drop=True)
        self.REAC = self.REAC[self.REAC['primaryid'].isin(ids_common)] \
                                                    .drop_duplicates(['primaryid', 'pt']) \
                                                    .reset_index(drop=True)
        
        # カテゴリーの修正
        # self.DRUG.iloc[:,1:] = self.DRUG.iloc[:,1:] \
        # .apply(lambda x: x.cat.remove_unused_categories().cat.add_categories('_undefined')) #FutureWarning
        self.DRUG[self.DRUG.columns[1:]] = self.DRUG[self.DRUG.columns[1:]] \
        .apply(lambda x: x.cat.remove_unused_categories().cat.add_categories('_undefined'))
        # self.REAC.iloc[:,1:] = self.REAC.iloc[:,1:] \
        # .apply(lambda x: x.cat.remove_unused_categories().cat.add_categories('_undefined')) #FutureWarning
        self.REAC[self.REAC.columns[1:]] = self.REAC[self.REAC.columns[1:]] \
        .apply(lambda x: x.cat.remove_unused_categories().cat.add_categories('_undefined'))
        
    
    def _dump_tables(self, out_dir):
        data = {}
        for col in self.DRUG.columns[1:]:
            df = self.DRUG[['primaryid', col]] \
                                 .fillna('_undefined') \
                                 .drop_duplicates() \
                                 .reset_index(drop=True)
            tmp = self.to_sparseMatrix(df, 'primaryid', col)[:2]
            self._pickle_dump(tmp, os.path.join(out_dir, col + '.pkl'))
            self._pickle_dump(tmp[1], os.path.join(out_dir, col+'_labels.pkl'))
        
        for col in self.REAC.columns[1:]:
            df = self.REAC[['primaryid', col]] \
                                 .fillna('_undefined') \
                                 .drop_duplicates() \
                                 .reset_index(drop=True)
            tmp = self.to_sparseMatrix(df, 'primaryid', col)[:2]
            self._pickle_dump(tmp, os.path.join(out_dir, col+'.pkl'))
            self._pickle_dump(tmp[1], os.path.join(out_dir, col+'_labels.pkl'))
            
    
    def _pickle_dump(self, obj, fname):
#         data = {
#             'DRUG': self.DRUG,
#             'REAC': self.REAC,
#             'matrices': self.data,
#             'labels': self.labels
#         }
        
        with open(fname, 'wb') as f:
            pickle.dump(obj, f)
    
    def _pickle_load(self, fname):
        with open(fname, 'rb') as f:
            return pickle.load(f)
    
    
    def to_sparseMatrix(self, df, row, col, data=None):
        row, row_labels = pd.factorize(df[row], sort=True)
        col, col_labels = pd.factorize(df[col], sort=True)
        if data:
            data = df[data].values
        else:
            data = np.repeat(1, len(df))
#         mat = csr_matrix((data, (row, col)), shape=(len(row_labels), len(col_labels)))
        mat = csc_matrix((data, (row, col)), shape=(len(row_labels), len(col_labels)))
        return mat, col_labels.values, row_labels.values

        
    def RORbyReac(self, reac_term:str, levels:dict=None, sort:dict=None):
        self._load_pickles(levels)
        return self._RORbyReac(reac_term, sort)

        
    def _RORbyReac(self, reac_term:str, sort:dict=None):
        """
        +-----+-----+-----+-----+
        |     |+reac|-reac| sum |
        +-----+-----+-----+-----+
        |+drug|d1r1 |d1r0 | d1  |
        |-drug|d0r1 |d0r0 | d0  |
        +-----+-----+-----+-----+
        | sum | r1  | r0  |  n  |
        +-----+-----+-----+-----+
        """
        reac_idx = self.getIdxFromArr(self.reac_labels, reac_term)
        pids = np.where(self.REAC[:,reac_idx].sum(axis=1) > 0)[0]

        n = self.DRUG.shape[0]
        d1 = self.DRUG.sum(axis=0).A1
        r1 = len(pids)
        d1r1 = self.DRUG[pids].sum(axis=0).A1

        return self._calc_ROR(n, d1, r1, d1r1, index=self.drug_labels, sort=sort)
    
    
    def RORbyDrug(self, drug_term:str, levels:dict=None, sort:dict=None):
        self._load_pickles(levels)
        return self._RORbyDrug(drug_term, sort)
        
        
    def _RORbyDrug(self, drug_term:str, sort:dict=None):
        drug_idx = self.getIdxFromArr(self.drug_labels, drug_term)
        pids = np.where(self.DRUG[:,drug_idx].sum(axis=1) > 0)[0]

        n = self.REAC.shape[0]
        d1 = len(pids)
        r1 = self.REAC.sum(axis=0).A1
        d1r1 = self.REAC[pids].sum(axis=0).A1

        return self._calc_ROR(n, d1, r1, d1r1, index=self.reac_labels, sort=sort)
    
    
    def RORbyDrugAndReac(self, drug:str, reac_term:str, levels:dict=None, sort:dict=None):
        self._load_pickles(levels)
        return self._RORbyDrugAndReac(drug, reac_term, sort)
        
        
    def _RORbyDrugAndReac(self, drug:str, reac_term:str, sort:dict=None):
        drug_idx = self.getIdxFromArr(self.drug_labels, drug)
        pidx = np.where(self.DRUG[:,drug_idx].sum(axis=1) > 0)[0]
        DRUG, REAC = self.DRUG[pidx], self.REAC[pidx]

        reac_idx = self.getIdxFromArr(self.reac_labels, reac_term)
        pids = np.where(REAC[:,reac_idx].sum(axis=1) > 0)[0]

        n = DRUG.shape[0]
        d1 = DRUG.sum(axis=0).A1
        r1 = len(pids)
        d1r1 = DRUG[pids].sum(axis=0).A1

        return self._calc_ROR(n, d1, r1, d1r1, index=self.drug_labels, sort=sort)
            

    def getIdxFromArr(self, array, target):
        if type(target) == str: target = [target]
        return np.where(np.isin(array, target))[0]
        
    
    def _load_pickles(self, levels:dict=None, pkl_dir=None):
        if not pkl_dir: pkl_dir = self.pkl_dir
            
        if levels == None: levels = {'DRUG':'prod_ai', 'REAC':'pt'}
        if not 'DRUG' in levels.keys(): levels['DRUG'] = 'prod_ai'
        if not 'REAC' in levels.keys(): levels['REAC'] = 'pt'
        
#         DRUG = self.data[levels['DRUG']]
#         REAC = self.data[levels['REAC']]
#         drug_labels = self.labels[levels['DRUG']]
#         reac_labels = self.labels[levels['REAC']]
        self.DRUG, self.drug_labels = self._pickle_load(os.path.join(pkl_dir, levels['DRUG'] + '.pkl'))
        self.REAC, self.reac_labels = self._pickle_load(os.path.join(pkl_dir, levels['REAC'] + '.pkl'))
        
#         return DRUG, REAC, drug_labels, reac_labels

        
    def _calc_ROR(self, n, d1, r1, d1r1, index=None, sort=None):
        d1r0 = d1 - d1r1
        d0r1 = r1 - d1r1
        d0r0 = n - r1- d1r0
        with np.errstate(divide='ignore', invalid='ignore'):
            ROR = d1r1 * d0r0 / (d1r0 * d0r1)
            SE = np.sqrt(1/d1r1 + 1/d1r0 + 1/d0r1 + 1/d0r0)
            CI95min = np.exp(np.log(ROR) - 1.96 * SE)
            CI95max = np.exp(np.log(ROR) + 1.96 * SE)

        df = pd.DataFrame({'d1r1': d1r1,
                           'd1r0': d1r0,
                           'd0r1': d0r1,
                           'd0r0': d0r0,
                           'ROR': ROR,
                           'SE': SE,
                           'CI95min': CI95min,
                           'CI95max': CI95max})
        df.iloc[:,-4:] = df.iloc[:,-4:].replace([0, np.inf], np.nan)

        if index is not None: df.index = index
        if sort: df = self.sort_df(df, sort)

        return df