import os

import gdown
import pandas as pd

from src import PROJECT_PATH


class DataLoader:
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
        self.do_download = do_download
        self.folder_link = folder_link
        self.put_data_folder_inside_project_folder = put_data_folder_inside_project_folder

        self.dataset_name = 'time_series_data'

        if self.put_data_folder_inside_project_folder:
            self.data_folder_path = os.path.join(PROJECT_PATH, 'data')
        else:
            self.data_folder_path = '../data'

        if self.do_download:
            self.download_data()

        self.populations = None
        self.cases_and_deaths_data = None
        self.read_data()

    def download_data(self) -> None:
        """
        Downloads all data from Google Drive.
        """
        gdown.download_folder(url=self.folder_link, output=self.data_folder_path)

    def read_data(self) -> None:
        """
        Reads downloaded data from the data folder and saves them in member variables.
        """
        populations_name = 'populations.csv'
        cases_and_deaths_data_name = 'cases_and_deaths_data.csv'

        self.populations = pd.read_csv(
            os.path.join(self.data_folder_path, populations_name),
            sep=';'
        )

        self.cases_and_deaths_data = pd.read_csv(
            os.path.join(self.data_folder_path, cases_and_deaths_data_name)
        )
