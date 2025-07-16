import numpy as np
import pandas as pd


class StringencyIndexCreator:
    """
    Class for creating the indices based on stringency.
    """
    def __init__(self, deaths_data: pd.DataFrame, stringency_data: pd.DataFrame,
                 meta_data: pd.DataFrame, similar_only: bool, remove_italy: bool = False):
        """
        Constructor.
        :param pd.DataFrame deaths_data: dataframe containing mortality data
        :param pd.DataFrame stringency_data: dataframe containing stringency data
        :param pd.DataFrame meta_data: dataframe containing metadata
        :param bool similar_only: True if only similar countries should be considered
        while creating stringency indices, False otherwise
        :param bool remove_italy: Italy is an outlier. We wish to disregard it in some
        cases
        """
        self.deaths_data = self.preprocess_deaths_data(deaths_data=deaths_data)
        self.stringency_data = self.preprocess_stringency_dataframe(stringency_data=stringency_data)
        self.meta_data = meta_data
        self.similar_only = similar_only
        self.remove_italy = remove_italy

        self.final_indices = dict()

    def run(self) -> None:
        """
        Run function. Filters the dataframes for the common (or "similar") countries, then gets
        the indices.
        """
        countries_inter = self.filter_countries()

        self.deaths_data = self.deaths_data[countries_inter]
        self.stringency_data = self.stringency_data[countries_inter]

        self.get_date_differences()

    @staticmethod
    def preprocess_deaths_data(deaths_data: pd.DataFrame) -> pd.DataFrame:
        """
        Replaces the indices of deaths_data for dates in 'YYYY-MM-DD' format.
        :param pd.DataFrame deaths_data: dataframe containing mortality data
        :return pd.DataFrame: dataframe with new indices
        """
        deaths_data.index = (
            pd.date_range('2020-01-22', periods=len(deaths_data), freq='D'))

        return deaths_data

    @staticmethod
    def preprocess_stringency_dataframe(stringency_data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocesses the stringency dataframe. Columns represent countries and rows are dates
        in 'YYYY-MM-DD' format.
        :param pd.DataFrame stringency_data: dataframe containing stringency data
        :return pd.DataFrame: preprocessed stringency dataframe
        """
        df = stringency_data.T[6:-59]
        df = df.loc[:, ~df.columns.duplicated(keep=False)]
        df.index = (
            pd.date_range('2020-01-01', periods=len(df), freq='D'))
        df = df.apply(pd.to_numeric, errors='coerce')

        return df

    def filter_countries(self) -> list:
        """
        Either gets common countries in the two dataframes or returns list of similar
        countries.
        :return list: the desired list described above
        """
        if not self.similar_only:
            countries = set(self.deaths_data.columns)
            countries_2 = set(self.stringency_data.columns)
            countries_3 = set(self.meta_data.index)
            countries_3.remove('Eritrea')

            countries_inter_1 = countries.intersection(countries_2)
            countries_inter = list(countries_inter_1.intersection(countries_3))
        else:
            countries_inter = [
                'Italy', 'Netherlands', 'Switzerland', 'Sweden', 'Germany',
                'Portugal', 'Denmark', 'Poland', 'Norway', 'Hungary' ,'Bulgaria',
                'Finland', 'Ukraine', 'Lithuania'
            ]
            if self.remove_italy:
                countries_inter.remove('Italy')

        return countries_inter

    def get_date_differences(self) -> None:
        """
        Gets the indices. For each country c, let dm(c) be the first date when c's mortality
        reached at least 10, and ds(c) be the first date when c's stringency reached at least 50.
        Then, the index of c is ds(c) - dm(c).
        """
        for country in self.stringency_data.columns:
            country_stringency = self.stringency_data[country]
            stringency_threshold_date = country_stringency[country_stringency >= 50].index.min()

            country_deaths = self.deaths_data[country]
            deaths_threshold_date = country_deaths[country_deaths >= 10].index.min()

            day_diff = (
                (pd.to_datetime(stringency_threshold_date) - pd.to_datetime(deaths_threshold_date)).days
            )

            if day_diff is np.nan:
                continue

            self.final_indices[country] = day_diff
