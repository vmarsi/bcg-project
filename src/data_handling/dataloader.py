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

        self.meta_data = None
        self.time_series_data = None
        self.load_data()

    def load_data(self) -> None:
        """
        Reads downloaded data from the data folder and saves them in member variables.
        """
        populations_name = 'populations.csv'
        cases_and_deaths_data_name = 'cases_and_deaths_data.csv'

        self.meta_data = pd.read_csv(
            os.path.join(self.data_folder_path, populations_name)
        )

        self.time_series_data = pd.read_csv(
            os.path.join(self.data_folder_path, cases_and_deaths_data_name)
        )
