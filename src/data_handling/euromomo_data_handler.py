import numpy as np
import pandas as pd

from src.data_handling.data_interface import DataInterface
from src.data_handling.dataloader import DataLoader


class EUROMOMODataHandler:
    """
    Class for preprocessing EUROMOMO data (excess deaths).
    """
    def __init__(self, dl: DataLoader):
        """
        Constructor.
        :param DataLoader dl: a DataLoader instance
        """
        self.dl = dl

        self.data_if = DataInterface()

    def run(self) -> None:
        """
        Gets excess deaths dataframe.
        """
        studied_countries = self.get_studied_countries()

        self.data_if.deaths_df = self.get_excess_deaths_df(studied_countries=studied_countries)

    @staticmethod
    def get_studied_countries() -> list:
        """
        Only the following countries' excess deaths are studied.
        :return list: studied countries
        """
        return ['Greece', 'Estonia', 'Ireland', 'Portugal', 'Hungary',
                'Belgium', 'Italy', 'Netherlands']

    def get_excess_deaths_df(self, studied_countries: list) -> pd.DataFrame:
        """
        Gets the excess deaths dataframe. Indices are weeks and columns are countries.
        Indices are in the form YYYY-WW, which represents the WW-th week of YYYY. For example
        2020-05 is the fifth week of 2020.
        :param list studied_countries: list of studied countries
        :return pd.DataFrame: excess deaths dataframe
        """
        indices = self.dl.time_series_data[
            self.dl.time_series_data['country'] == 'Austria'
        ][['week']].values.tolist()
        indices = [idx[0] for idx in indices]

        all_values = []
        for country in studied_countries:
            country_df = self.dl.time_series_data[self.dl.time_series_data['country'] == country]

            values = np.array(country_df['zscore'].values.tolist())

            all_values.append(values)

        df = pd.DataFrame(np.array(all_values).T, index=indices, columns=studied_countries)

        return df
