import numpy as np
import pandas as pd

from src.data_handling.data_interface import DataInterface
from src.data_handling.dataloader import DataLoader


class JohnsHopkinsDataHandler:
    def __init__(self, dl: DataLoader):
        self.dl = dl

        self.data_if = DataInterface()
        self.bcg_index_dict = {}
        self.bcg_index_similar_dict = {}

    def run(self):
        self.preprocess_df()

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

    def preprocess_df(self):
        for data_type in ['cases', 'deaths']:
            df = self.dl.time_series_data[data_type].drop(['Province/State', 'Lat', 'Long'], axis=1)
            df_summed = df.groupby(df.index).sum()
            df_transposed = df_summed.T

            df_transposed.index = pd.to_datetime(
                df_transposed.index, format='%m/%d/%y'
            ).strftime('%y-%m-%d')

            self.dl.time_series_data[data_type] = df_transposed

    def get_common_countries(self):
        countries = set(self.dl.time_series_data['cases'].columns)
        countries_2 = set(self.dl.meta_data.index)

        countries_inter = list(countries.intersection(countries_2))

        return countries_inter

    def filter_data(self, countries_inter: list):
        self.dl.meta_data = self.dl.meta_data.loc[countries_inter]
        self.dl.meta_data['Population'] = self.dl.meta_data['Population'].apply(
            lambda x: float(str(x).replace(',', ''))
        )

        self.dl.time_series_data['cases'] = self.dl.time_series_data['cases'][countries_inter]
        self.dl.time_series_data['deaths'] = self.dl.time_series_data['deaths'][countries_inter]

    def get_df(self, countries_inter: list, data_type: str) -> pd.DataFrame:
        """
        Gets the desired dataframe. Indices are dates and columns are countries.
        :param list countries_inter: countries for which we have all necessary data
        :param str data_type: either 'cases' or 'deaths'
        :return pd.DataFrame: the desired dataframe
        """
        date_range = pd.date_range(start='2020-01-22', end='2023-03-09', freq='7D')

        all_values = []
        for country in countries_inter:
            country_df = self.dl.time_series_data[data_type][country]

            pop = self.dl.meta_data.loc[country]['Population']

            values = np.array(
                country_df.values.tolist()[::7]
            ) / pop * 1000000

            all_values.append(values)

        df = pd.DataFrame(np.array(all_values).T, index=date_range, columns=countries_inter)

        return df

    def create_bcg_index_dicts(self):
        self.bcg_index_dict = self.dl.bcg_index['BCG Index.  0 to 1'][:-1].to_dict()
        self.bcg_index_dict.pop('Russian Federation')
        self.bcg_index_dict.pop('Uzbekistan')

        self.bcg_index_similar_dict = (
            self.dl.bcg_index_similar_countries['Corrected BCG Index'][:-1].to_dict())
