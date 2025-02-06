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

        self.download_data()

    def download_data(self) -> None:
        """
        Downloads all data from Google Drive.
        """
        gdown.download_folder(url=self.folder_link, output=self.data_folder_path)
