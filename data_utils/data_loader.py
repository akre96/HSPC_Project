from .step7_to_long_format import step7_out_to_long_format
import pandas as pd
import json
from pathlib import Path
from tqdm import tqdm


class HSPC_data_loader():
    def __init__(self, config_path):
        config = load_config(config_path)
        print('Finding data files from:', config['step7'])
        self.data_files = list(
            Path(config['step7']).glob(config['user'] + '*.txt')
        )
        print('\tFound', len(self.data_files), 'files')
        self.validated: bool = False

        self.data: pd.DataFrame = self.load_format_data(self.data_files)

        self.metadata: pd.DataFrame = self.load_metadata(config['metadata'])
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
        self.data = merged
        return True

    @staticmethod
    def load_format_data(data_files):
        formatted = []
        for file_path in tqdm(data_files, desc='Loading and transforming to long format'):
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
