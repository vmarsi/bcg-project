import os

import numpy as np
import pandas as pd


class DataAligner:

    @staticmethod
    def align_data(data: pd.DataFrame) -> pd.DataFrame:
        """
        Aligns data in the given dataframe. The first elements of the new columns are the first
        nonzero elements of the old columns.
        :param pd.DataFrame data: the given dataframe
        :return pd.DataFrame: the aligned dataframe
        """
        max_len = len(data)
        new_dict = {}

        for col in data.columns:
            nonzero_idx = data[col].ne(0).idxmax()
            pos_idx = data.index.get_loc(nonzero_idx)
            shifted = data[col].iloc[pos_idx:].reset_index(drop=True)
            new_dict[col] = shifted.reindex(range(max_len), fill_value=np.nan)

        return pd.DataFrame(new_dict)

    @staticmethod
    def save_aligned(aligned_data: pd.DataFrame, data_folder_path: str) -> None:
        """
        Saves the transposed of aligned_data (columns are country names, indices are days after
        alignment)
        :param pd.DataFrame aligned_data: the aligned dataframe
        :param str data_folder_path: path of the data folder
        """
        if not os.path.exists(os.path.join(data_folder_path, 'generated')):
            os.makedirs(os.path.join(data_folder_path, 'generated'))

        transposed_df = aligned_data.T.round(2)

        transposed_df.to_csv(data_folder_path + '/generated/' + 'aligned_values.csv')
