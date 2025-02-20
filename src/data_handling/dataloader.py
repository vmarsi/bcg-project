import os

import pandas as pd


class DataLoader:
    """
    Class for loading downloaded data.
    """
    def __init__(self, data_folder_path: str):
        """
        Constructor.
        :param str data_folder_path: path of the data folder
        """
        self.data_folder_path = data_folder_path

        self.meta_data = pd.DataFrame()
        self.time_series_data = pd.DataFrame()
        self.bcg_index = pd.DataFrame()
        self.bcg_index_similar_countries = pd.DataFrame()
        self.load_data()

    def load_data(self) -> None:
        """
        Reads downloaded data from the data folder and saves them in member variables.
        """
        meta_name = 'meta.csv'
        cases_and_deaths_data_name = 'cases_and_deaths_data.csv'
        bcg_index_file_name = 'bcg_index_article_data.xlsx'

        self.meta_data = pd.read_csv(
            os.path.join(self.data_folder_path, meta_name),
            index_col=[0]
        )

        self.time_series_data = pd.read_csv(
            os.path.join(self.data_folder_path, cases_and_deaths_data_name),
            index_col=[0]
        )

        self.bcg_index = pd.read_excel(
            os.path.join(self.data_folder_path, bcg_index_file_name),
            sheet_name='BCG Index',
            index_col=[0]
        )

        self.bcg_index_similar_countries = pd.read_excel(
            os.path.join(self.data_folder_path, bcg_index_file_name),
            sheet_name='BCG Index Similar Countries',
            index_col=[0]
        )
