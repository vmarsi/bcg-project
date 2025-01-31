import os

import pandas as pd

from src.data_downloader import DataDownloader


class DataLoader:
    """
    Class for loading downloaded data.
    """
    def __init__(self,
                 do_download: bool = False,
                 folder_link: str = '',
                 put_data_folder_inside_project_folder: bool = True):
        """
        Constructor.
        :param bool do_download: True if we wish to download data, False if we don't
        :param str folder_link: The link of the folder containing all necessary data
        :param bool put_data_folder_inside_project_folder: if True, the generated data folder will
        be inside the project folder, otherwise it will be the in the folder containing the
        project folder
        """
        self.ddl = DataDownloader(
            do_download=do_download,
            folder_link=folder_link,
            put_data_folder_inside_project_folder=put_data_folder_inside_project_folder
        )

        self.dataset_name = 'time_series_data'

        self.populations = None
        self.cases_and_deaths_data = None
        self.load_data()

    def load_data(self) -> None:
        """
        Reads downloaded data from the data folder and saves them in member variables.
        """
        populations_name = 'populations.csv'
        cases_and_deaths_data_name = 'cases_and_deaths_data.csv'

        self.populations = pd.read_csv(
            os.path.join(self.ddl.data_folder_path, populations_name)
        )

        self.cases_and_deaths_data = pd.read_csv(
            os.path.join(self.ddl.data_folder_path, cases_and_deaths_data_name)
        )
