import os

import pandas as pd


class DataLoader:
    """
    Class for loading downloaded data.
    """
    def __init__(self, data_folder_path: str,
                 dataset_origin: str, index_type: str = None):
        """
        Constructor.
        :param str data_folder_path: path of the data folder
        :param str dataset_origin: origin of the mortality data,
        can be 'who', 'johns_hopkins', 'euromomo' or 'rki'
        :param str index_type: 'BCG', 'vodka' or 'stringency'
        """
        self.data_folder_path = data_folder_path
        self.dataset_origin = dataset_origin
        self.index_type = index_type

        self.meta_data = pd.DataFrame()
        self.time_series_data = pd.DataFrame()
        self.index_all_countries = pd.DataFrame()
        self.index_similar_countries = pd.DataFrame()
        self.load_data()

    def load_data(self) -> None:
        """
        Reads downloaded data from the data folder and saves them in member variables.
        """
        meta_name = 'meta.csv'
        who_cases_and_deaths_name = 'who_cases_and_deaths.csv'
        johns_hopkins_cases_name = 'johns_hopkins_cases.csv'
        johns_hopkins_deaths_name = 'johns_hopkins_deaths.csv'
        bcg_index_name = 'bcg_index_article_data.xlsx'
        vodka_consumption_name = 'vodka_consumption.csv'
        vodka_consumption_all_name = 'vodka_consumption_all.csv'
        excess_deaths_name = 'excess_deaths.csv'
        germany_data_name = 'deaths_by_german_states.csv'
        stringency_name = 'OxCGRT_stringency.csv'

        if self.dataset_origin == 'who':
            self.time_series_data = pd.read_csv(
                os.path.join(self.data_folder_path, who_cases_and_deaths_name),
                index_col=[0]
            )
            self.meta_data = pd.read_csv(
                os.path.join(self.data_folder_path, meta_name),
                index_col=[0]
            )
        elif self.dataset_origin == 'johns_hopkins':
            self.time_series_data = {
                'cases': pd.read_csv(os.path.join(self.data_folder_path, johns_hopkins_cases_name),
                                     index_col=[1]),
                'deaths': pd.read_csv(os.path.join(self.data_folder_path, johns_hopkins_deaths_name),
                                      index_col=[1])
            }
            self.index_all_countries = pd.read_excel(
                os.path.join(self.data_folder_path, bcg_index_name),
                sheet_name='Coarse',
                index_col=[1]
            )
            population_meta = self.index_all_countries[['population_2018']]
            self.meta_data = population_meta[~population_meta.index.duplicated(keep='first')]
            self.meta_data.columns = ['Population']
        elif self.dataset_origin == 'euromomo':
            self.time_series_data = pd.read_csv(
                os.path.join(self.data_folder_path, excess_deaths_name),
                sep=';'
            )
        elif self.dataset_origin == 'rki':
            meta = pd.read_excel(
                os.path.join(self.data_folder_path, bcg_index_name),
                sheet_name='Germany',
                index_col=[0]
            )
            self.meta_data = meta[['East-West', 'Population']]
            self.time_series_data = pd.read_csv(
                os.path.join(self.data_folder_path, germany_data_name),
                index_col=[0]
            )
        else:
            raise Exception('Dataset origin is not valid.')

        if self.index_type == 'BCG':
            self.index_all_countries = pd.read_excel(
                os.path.join(self.data_folder_path, bcg_index_name),
                sheet_name='BCG Index',
                index_col=[0]
            )
            self.index_similar_countries = pd.read_excel(
                os.path.join(self.data_folder_path, bcg_index_name),
                sheet_name='BCG Index Similar Countries',
                index_col=[0]
            )
        elif self.index_type == 'vodka':
            self.index_similar_countries = pd.read_csv(
                os.path.join(self.data_folder_path, vodka_consumption_name),
                index_col=[0]
            )
            self.index_all_countries = pd.read_csv(
                os.path.join(self.data_folder_path, vodka_consumption_all_name),
                index_col=[0]
            )
        elif self.index_type == 'stringency':
            self.index_all_countries = pd.read_csv(
                os.path.join(self.data_folder_path, stringency_name),
                index_col=[1]
            )
        elif self.index_type is None:
            pass
        else:
            raise Exception('Type of index can only be BCG, vodka or stringency.')
