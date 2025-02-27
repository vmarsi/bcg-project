import numpy as np
import pandas as pd

from src.data_handling.data_interface import DataInterface
from src.data_handling.dataloader import DataLoader


class JohnsHopkinsDataHandler:
    """
    Class for preprocessing the Johns Hopkins data.
    """
    def __init__(self, dl: DataLoader):
        """
        Constructor.
        :param DataLoader dl: a DataLoader instance
        """
        self.dl = dl

        self.data_if = DataInterface()
        self.index_all_countries_dict = {}
        self.index_similar_countries_dict = {}

    def run(self) -> None:
        """
        Run function. Selects countries for which we have all necessary information, gets two
        dataframes, one containing cases data, the other containing deaths data.
        """
        self.preprocess_df()

        countries_inter = self.get_common_countries()

        self.filter_data(countries_inter=countries_inter)

        self.create_bcg_index_dicts()

        data = {
            'cases_df': self.get_df(countries_inter=countries_inter, data_type='cases'),
            'deaths_df': self.get_df(countries_inter=countries_inter, data_type='deaths'),
            'index_all_countries_dict': self.index_all_countries_dict,
            'index_similar_countries_dict': self.index_similar_countries_dict
        }

        self.data_if = DataInterface(data=data)

    def preprocess_df(self) -> None:
        """
        Creates two dataframes, one containing cases, the other containing deaths data.
        Indices are dates, columns are countries.
        """
        for data_type in ['cases', 'deaths']:
            df = self.dl.time_series_data[data_type].drop(['Province/State', 'Lat', 'Long'], axis=1)
            df_summed = df.groupby(df.index).sum()
            df_transposed = df_summed.T

            df_transposed.index = pd.to_datetime(
                df_transposed.index, format='%m/%d/%y'
            ).strftime('%y-%m-%d')

            self.dl.time_series_data[data_type] = df_transposed

    def get_common_countries(self) -> list:
        """
        Gets countries for which we have all necessary data.
        :return list: list of countries we can work with
        """
        countries = set(self.dl.time_series_data['cases'].columns)
        countries_2 = set(self.dl.meta_data.index)

        countries_inter = list(countries.intersection(countries_2))

        return countries_inter

    def filter_data(self, countries_inter: list) -> None:
        """
        Filters all data for common countries.
        :param list countries_inter: common countries
        """
        self.dl.meta_data = self.dl.meta_data.loc[countries_inter]
        self.dl.meta_data['Population'] = self.dl.meta_data['Population'].apply(
            lambda x: float(str(x).replace(',', ''))
        )

        self.dl.time_series_data['cases'] = self.dl.time_series_data['cases'][countries_inter]
        self.dl.time_series_data['deaths'] = self.dl.time_series_data['deaths'][countries_inter]

    def get_df(self, countries_inter: list, data_type: str) -> pd.DataFrame:
        """
        Gets the normalized dataframe. Indices are dates and columns are countries.
        :param list countries_inter: countries for which we have all necessary data
        :param str data_type: either 'cases' or 'deaths'
        :return pd.DataFrame: the desired dataframe
        """
        date_range = pd.date_range(start='2020-01-22', end='2023-03-09', freq='1D')

        all_values = []
        for country in countries_inter:
            country_df = self.dl.time_series_data[data_type][country]

            pop = self.dl.meta_data.loc[country]['Population']

            values = np.array(
                country_df.values.tolist()
            ) / pop * 1000000

            all_values.append(values)

        df = pd.DataFrame(np.array(all_values).T, index=date_range, columns=countries_inter)

        return df

    def create_bcg_index_dicts(self) -> None:
        """
        If the index type is BCG, then this function creates two dictionaries. One containing
        BCG indices for all countries, the other containing BCG indices for similar countries.
        If the index type is vodka, then this function creates one dictionary containing
        vodka consumption indices for similar countries.
        """
        if self.dl.index_type == 'BCG':
            self.index_all_countries_dict = self.dl.index_all_countries['BCG Index.  0 to 1'][:-1].to_dict()
            self.index_all_countries_dict.pop('Uzbekistan')

            self.index_similar_countries_dict = (
                self.dl.index_similar_countries['Corrected BCG Index'][:-1].to_dict())
        else:
            df = self.dl.index_similar_countries
            self.index_similar_countries_dict = (df-df.min())/(df.max()-df.min()).squeeze().to_dict()
