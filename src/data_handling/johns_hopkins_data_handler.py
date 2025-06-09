import numpy as np
import pandas as pd

from src.data_handling.data_interface import DataInterface
from src.data_handling.dataloader import DataLoader
from src.data_handling.stringency_index_creator import StringencyIndexCreator


class JohnsHopkinsDataHandler:
    """
    Class for preprocessing the Johns Hopkins data.
    """
    def __init__(self, dl: DataLoader,
                 take_log_of_vodka: bool = False, stringency_date: str = None):
        """
        Constructor.
        :param DataLoader dl: a DataLoader instance
        :param bool take_log_of_vodka: whether to take the logarithm of the vodka indices or not
        :param str stringency_date: stringency indices are extracted from this date
        """
        self.dl = dl
        self.take_log_of_vodka = take_log_of_vodka
        self.stringency_date = stringency_date

        self.deaths_df = pd.DataFrame()

        self.countries_inter = list()
        self.data_if = DataInterface()
        self.index_all_countries_dict = {}
        self.index_similar_countries_dict = {}

    def run(self) -> None:
        """
        Run function. Selects countries for which we have all necessary information, gets two
        dataframes, one containing cases data, the other containing deaths data.
        """
        self.preprocess_df()

        self.get_common_countries()

        self.filter_data(countries_inter=self.countries_inter)

        self.create_index_dicts()

        data = {
            'cases_df': self.get_df(countries_inter=self.countries_inter, data_type='cases'),
            'deaths_df': self.get_df(countries_inter=self.countries_inter, data_type='deaths'),
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

    def get_common_countries(self):
        """
        Gets countries for which we have all necessary data.
        """
        countries = set(self.dl.time_series_data['deaths'].columns)
        countries_2 = set(self.dl.meta_data.index)

        self.countries_inter = list(countries.intersection(countries_2))

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

    def create_index_dicts(self) -> None:
        """
        If the index type is BCG, then this function creates two dictionaries. One containing
        BCG indices for all countries, the other containing BCG indices for similar countries.
        If the index type is vodka, then this function creates one dictionary containing
        vodka consumption indices for similar countries.
        """
        if self.dl.index_type == 'BCG':
            self.create_bcg_indices()
        elif self.dl.index_type == 'vodka':
            self.create_vodka_indices()
        elif self.dl.index_type == 'stringency':
            self.create_stringency_indices()
        else:
            return

    def create_bcg_indices(self) -> None:
        """
        Load BCG indices for both all and similar countries from bcg_index_article_data.xlsx
        and normalize them by dividing with the maximum (the minimum is 0).
        """
        # Remove Uzbekistan, Latvia and Romania with the [:-4]
        bcg_index_df = self.dl.index_all_countries['Corrected BCG Index'][:-4]
        normalized_bcg_index_df = bcg_index_df / max(bcg_index_df)
        self.index_all_countries_dict = normalized_bcg_index_df.to_dict()

        similar_bcg_index = self.dl.index_similar_countries['Corrected BCG Index'][:-1]
        normalized_similar_bcg_index_df = similar_bcg_index / max(similar_bcg_index)
        self.index_similar_countries_dict = normalized_similar_bcg_index_df.to_dict()

    def create_vodka_indices(self) -> None:
        """
        Create vodka indices by loading data from vodka_consumption.csv and normalizing
        the values.
        """
        df = self.dl.index_similar_countries
        if self.take_log_of_vodka:
            df['vodka_consumption'] = np.log2(df['vodka_consumption'])
        df_normalized = (df - df.min()) / (df.max() - df.min())
        self.index_similar_countries_dict = list(df_normalized.to_dict().values())[0]

    def create_stringency_indices(self) -> None:
        """
        Create stringency indices by loading data from OxCGRT_stringency.csv
        """
        df = self.dl.index_all_countries
        index_creator = StringencyIndexCreator(
            deaths_data=self.dl.time_series_data['deaths'],
            stringency_data=df,
            meta_data=self.dl.meta_data
        )
        index_creator.run()

        values = list(index_creator.final_indices.values())
        min_val = min(values)
        max_val = max(values)

        self.index_all_countries_dict = \
            {k: (v - min_val) / (max_val - min_val) for k, v in index_creator.final_indices.items()}
