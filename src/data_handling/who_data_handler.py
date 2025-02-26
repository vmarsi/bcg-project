import numpy as np
import pandas as pd

from src.data_handling.data_interface import DataInterface
from src.data_handling.dataloader import DataLoader


class WHODataHandler:
    """
    Class for preprocessing the WHO data.
    """
    def __init__(self, dl: DataLoader):
        """
        Constructor.
        :param DataLoader dl: a DataLoader instance
        """
        self.dl = dl

        self.data_if = DataInterface()
        self.bcg_index_dict = {}
        self.bcg_index_similar_dict = {}

    def run(self) -> None:
        """
        Run function. Selects countries for which we have all necessary information, gets two
        dataframes, one containing cases data, the other containing deaths data.
        """
        countries_inter = self.get_common_countries()

        self.filter_data(countries_inter=countries_inter)

        self.create_bcg_index_dicts()

        data = {
            'cases_df': self.get_df(countries_inter=countries_inter, data_type='cases'),
            'deaths_df': self.get_df(countries_inter=countries_inter, data_type='deaths'),
            'bcg_index_dict': self.bcg_index_dict,
            'bcg_index_similar_dict': self.bcg_index_similar_dict
        }

        self.data_if = DataInterface(data=data)

    def get_common_countries(self) -> list:
        """
        Gets countries for which we have all necessary data.
        :return list: list of countries we can work with
        """
        countries = set(self.dl.time_series_data['Country'].values)
        countries_2 = set(self.dl.meta_data.index)

        return list(countries.intersection(countries_2))

    def filter_data(self, countries_inter: list) -> None:
        """
        Filters all data for common countries.
        :param list countries_inter: common countries
        """
        self.dl.meta_data = self.dl.meta_data.loc[countries_inter]
        self.dl.meta_data['Population'] = self.dl.meta_data['Population'].apply(
            lambda x: float(str(x).replace(',', ''))
        )
        self.dl.time_series_data = self.dl.time_series_data[
            self.dl.time_series_data['Country'].isin(countries_inter)
        ]

    def get_df(self, countries_inter: list, data_type: str) -> pd.DataFrame:
        """
        Gets the normalized dataframe. Indices are dates and columns are countries.
        :param list countries_inter: countries for which we have all necessary data
        :param str data_type: either 'cases' or 'deaths'
        :return pd.DataFrame: the desired dataframe
        """
        date_range = pd.date_range(start='2020-01-04', end='2025-01-12', freq='1D')

        all_values = []
        for country in countries_inter:
            country_df = self.dl.time_series_data[self.dl.time_series_data['Country'] == country]

            pop = self.dl.meta_data.loc[country]['Population']

            values = np.array(
                country_df[f'Cumulative_{data_type}'].values.tolist()
            ) / pop * 1000000

            all_values.append(values)

        df = pd.DataFrame(np.array(all_values).T, index=date_range, columns=countries_inter)

        return df

    def create_bcg_index_dicts(self) -> None:
        """
        Creates two dictionaries, one containing the BCG indices of all countries,
        the other only containing the BCG indices of similar countries.
        """
        self.bcg_index_dict = self.dl.bcg_index['BCG Index.  0 to 1'][:-1].to_dict()
        self.bcg_index_dict.pop('Turkey')
        self.bcg_index_dict.pop('Russian Federation')
        self.bcg_index_dict.pop('Uzbekistan')

        self.bcg_index_similar_dict = (
            self.dl.bcg_index_similar_countries['Corrected BCG Index'][:-1].to_dict())
