#import joblib
import numpy as np
import pandas as pd
import pickle
from scipy.sparse import csr_matrix, csc_matrix

class FAERS():
    def __init__(self):
        self.DRUG = None
        self.REAC = None
        self.ATC = None
        self.MedDRA = None
        self.drug_list = None
        self.reac_list = None
        
    
    def load(self, path):
        with open(path, 'rb') as f:
            data = pickle.load(f)
        #data = joblib.load(self.cache_path)
        self.DRUG = data['DRUG']
        self.REAC = data['REAC']
        self.ATC = data['ATC']
        self.MedDRA = data['MedDRA']
        self.drug_list = data['drug_list']
        self.reac_list = data['reac_list']
        
    
    def sort_df(self, df, sort:dict):
        keys = [key for key in sort]
        asc = [sort[key] == 'asc' for key in sort]
        return df.sort_values(keys, ascending=asc)    

    
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

        
    def RORbyReac(self, reac_term, sort=None):
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
        
        DRUG, drug_labels, ids = self.to_sparseMatrix(self.DRUG, 'primaryid', 'prod_ai')
        REAC, reac_labels, ids = self.to_sparseMatrix(self.REAC, 'primaryid', 'pt')

        reac_idx = self.getIdxFromArr(reac_labels, reac_term)
        pids = np.where(REAC[:,reac_idx].sum(axis=1) > 0)[0]

        n = DRUG.shape[0]
        d1 = DRUG.sum(axis=0).A1
        r1 = len(pids)
        d1r1 = DRUG[pids].sum(axis=0).A1

        return self._calc_ROR(n, d1, r1, d1r1, index=drug_labels, sort=sort)
    
    
    def RORbyDrugAndReac(self, drug, reac_term, sort=None):
        ids = self.DRUG['primaryid'][self.DRUG['prod_ai'] == drug].unique()
        DRUG, drug_labels, ids = self.to_sparseMatrix(self.DRUG[self.DRUG['primaryid'].isin(ids)], 'primaryid', 'prod_ai')
        REAC, reac_labels, ids = self.to_sparseMatrix(self.REAC[self.REAC['primaryid'].isin(ids)], 'primaryid', 'pt')

        reac_idx = self.getIdxFromArr(reac_labels, reac_term)
        pids = np.where(REAC[:,reac_idx].sum(axis=1) > 0)[0]

        n = DRUG.shape[0]
        d1 = DRUG.sum(axis=0).A1
        r1 = len(pids)
        d1r1 = DRUG[pids].sum(axis=0).A1

        return self._calc_ROR(n, d1, r1, d1r1, index=drug_labels, sort=sort)
            

    def getIdxFromArr(self, array, target):
        if type(target) == str: target = [target]
        if len(target) > 1:
            return np.where(np.isin(array, target))[0]
        else:
            return np.where(array == target)[0]

        
    def _calc_ROR(self, n, d1, r1, d1r1, index=None, sort=None):
        d1r0 = d1 - d1r1
        d0r1 = r1 - d1r1
        d0r0 = n - r1- d1r0
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

        if index is not None: df.index = index
        if sort: df = self.sort_df(df, sort)

        return df
