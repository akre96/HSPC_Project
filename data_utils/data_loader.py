from .step7_to_long_format import step7_out_to_long_format
import pandas as pd
import numpy as np
import json
from pathlib import Path
from tqdm import tqdm


class HSPC_data_loader():
    def __init__(self, config_path):
        self.config = load_config(config_path)
        print('Finding data files from:', self.config['step7'])
        self.data_files = list(
            Path(self.config['step7']).glob(self.config['user'] + '*.txt')
        )
        print('\tFound', len(self.data_files), 'files')
        self.validated: bool = False

        print('Loading and transforming to long format')
        self.data: pd.DataFrame = self.load_format_data(self.data_files)

        print('Marking parent cells by library ID')
        self.mark_lib_codes()

        print('Validating data')
        self.metadata: pd.DataFrame = self.load_metadata(self.config['metadata'])
        self.validated = self.validate()

    def validate(self):
        melted = self.metadata.melt(
            id_vars=['mouse_id', 'day', 'condition', 'generation'],
            value_vars=['gr', 'b', 'mo', 't'],
            var_name='cell_type',
            value_name='exists'
        )
        should_exist = melted[melted.exists == 1]
        merged = self.data.merge(should_exist, how='right')
        if self.data.shape[0] != merged.shape[0]:
            outer = self.data.merge(should_exist, how='outer')
            na = outer[outer.isna().any(axis=1)]
            print('Validation/Data mismatch')
            print('Pre-validation shape:', self.data.shape, 'Post validation shape:', merged.shape)
            print(na)
        else:
            print('Data Validation Passed')
        self.data = merged
        return True

    def mark_lib_codes(self):
        lib_codes = pd.read_csv(
            self.config['lib_codes'],
            sep='\t',
            header=None,
            names=['lib_id', 'lib_code', 'lib_code_reverse']
        )
        lib_ids = pd.read_excel(
            self.config['lib_ids'],
            names=['mouse_id', 'condition', 'hsc_lib_id', 'mpp_lib_id']
        )
        for (m_id, hsc_id, mpp_id), _ in lib_ids.groupby(['mouse_id', 'hsc_lib_id', 'mpp_lib_id']):
            hsc_code = lib_codes[lib_codes.lib_id == hsc_id].lib_code.tolist()[0]
            mpp_code = lib_codes[lib_codes.lib_id == mpp_id].lib_code.tolist()[0]
            hsc_query = (
                self.data.code.str.startswith(hsc_code) &
                (self.data.mouse_id == m_id)
            )
            self.data.loc[hsc_query, 'parent_cell_type'] = 'hsc'
            mpp_query = (
                self.data.code.str.startswith(mpp_code) &
                (self.data.mouse_id == m_id)
            )
            self.data.loc[mpp_query, 'parent_cell_type'] = 'mpp'




    @staticmethod
    def load_format_data(data_files):
        formatted = []

        for file_path in data_files:
            formatted.append(step7_out_to_long_format(file_path))
        return pd.concat(formatted)
    
    @staticmethod
    def load_metadata(path):
        metadata = pd.read_excel(path)
        cols = list(metadata.columns)
        cols = [c.lower() for c in cols]
        metadata.columns = cols
        return metadata


def load_config(path):
    return json.load(Path(path).open('r'))
