import os, sys
sys.path.append(os.path.join(os.path.dirname('__file__'), '../FAERS_ROR_calculator/'))

import numpy as np
import pandas as pd
from faerstools2 import FAERS

params = {
    'FAERS_path': '../data/',
    'quarters': [
        '2015q1', '2015q2', '2015q3', '2015q4',
        '2016q1', '2016q2', '2016q3', '2016q4',
        '2017q1', '2017q2', '2017q3', '2017q4',
        '2018q1', '2018q2', '2018q3', '2018q4',
        '2019q1', '2019q2', '2019q3', '2019q4',
        '2020q1', '2020q2', '2020q3', '2020q4',
        '2021q1', '2021q2',
    ],
    'keep': 'last', # 'first' or 'last'
    'ATC_path': '../ATC/ATC2019.csv',
    'MedDRA_path': '../MedDRA_v21.1j.csv',
    'pkl_dir': 'data/2015-2019/'
}

f = FAERS(params['pkl_dir'])


