import os

import gdown

from src import PROJECT_PATH


class DataDownloader:
    """
    Class for downloading all necessary data.
    """
    def __init__(self,
                 folder_link: str = '',
                 data_folder_path: str = None):
        """
        Constructor.
        :param str folder_link: The link of the folder containing all necessary data
        :param str data_folder_path: where to create the data folder
        """
        self.folder_link = folder_link
        self.data_folder_path = data_folder_path

        if self.data_folder_path is None:
            self.data_folder_path = os.path.join(PROJECT_PATH, 'data')

        if not self.do_all_files_exist():
            self.download_data()

    def download_data(self) -> None:
        """
        Downloads all data from Google Drive.
        """
        gdown.download_folder(url=self.folder_link, output=self.data_folder_path)

    @staticmethod
    def do_all_files_exist() -> bool:
        """
        This function checks whether all the files we wish to download already exist
        :return bool: True if all of them exist, False if at least one is missing
        """
        files = ['who_cases_and_deaths.csv', 'johns_hopkins_cases.csv', 'johns_hopkins_deaths.csv',
                 'meta.csv', 'bcg_index_article_data.xlsx', 'vodka_consumption.csv',
                 'excess_deaths.csv', 'deaths_by_german_states.csv']

        for file in files:
            if not os.path.exists(os.path.join(PROJECT_PATH, 'data', file)):
                return False

        return True
