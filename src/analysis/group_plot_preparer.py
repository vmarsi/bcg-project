import json
import os.path
import random
from typing import Tuple

import numpy as np
import pandas as pd

from src.data_handling.who_data_handler import WHODataHandler


class GroupPlotPreparer:
    """
    This is a helper class for plotting cases or deaths data grouped by some factors.
    """
    def __init__(self, data_handler: WHODataHandler, date: str, data_type: str,
                 data_folder_path: str):
        """
        Constructor.
        :param WHODataHandler data_handler: a DataHandler instance
        :param str date: we only consider data on this day
        :param str data_type: either 'cases' or 'deaths'
        :param str data_folder_path: path of the data folder
        """
        self.dl = data_handler.dl
        self.date = date
        self.data_type = data_type
        self.data_folder_path = data_folder_path
        if self.data_type == 'cases':
            self.data = data_handler.data_if.cases_df
        elif self.data_type == 'deaths':
            self.data = data_handler.data_if.deaths_df
        else:
            raise Exception('data_type can only be cases or deaths')

        self.x_coordinates = np.array([])
        self.y_coordinates = np.array([])
        self.y_medians = []

    def run(self) -> None:
        """
        Run function. Gets all countries with more than one million inhabitants,
        gets the x and y coordinates of the data points representing the countries on the
        plot, gets the median y values in each group.
        """
        df_over_one_mil = self.filter_over_one_million()

        self.x_coordinates, self.y_coordinates = self.get_coordinates(
            df_over_one_mil=df_over_one_mil
        )

        self.get_y_medians()

    def filter_over_one_million(self) -> pd.DataFrame:
        """
        Function for filtering data for countries with more than one million inhabitants
        :return pd.DataFrame: filtered dataframe
        """
        df_over_one_mil = self.dl.meta_data[self.dl.meta_data['Population'] >= 1000000]

        return df_over_one_mil

    def get_coordinates(self, df_over_one_mil: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Function for getting the x and y coordinates.
        :param pd.DataFrame df_over_one_mil: dataframe containing data only for countries with
        more than one million inhabitants
        :return Tuple[np.ndarray, np.ndarray]: x and y coordinates in a tuple
        """
        group1, group2, group3 = self.get_groups(df_over_one_mil=df_over_one_mil)

        grouped_countries = group1 + group2 + group3

        x_coordinates = self.get_x_coordinates(group1=group1, group2=group2, group3=group3)
        y_coordinates = self.get_y_coordinates(grouped_countries=grouped_countries)

        return np.array(x_coordinates), np.array(y_coordinates)

    def get_y_coordinates(self, grouped_countries: list) -> list:
        """
        Gets the y coordinates (cases or deaths per million inhabitants).
        :param list grouped_countries: all country names in a list in a specific order
        (countries in the same group are next to each other)
        :return list: y coordinates in the same order as grouped_countries
        """
        y_coordinates = []
        for country in grouped_countries:
            y = self.data[country][self.date]
            y_coordinates.append(y)

        return y_coordinates

    def get_y_medians(self) -> None:
        """
        Gets the medians of the y values in each group.
        """
        cutting_points = [0, 4, 8, 12]

        y_medians = []
        for i, j in zip(cutting_points[:-1], cutting_points[1:]):
            y_cut = self.y_coordinates[(i < self.x_coordinates) & (self.x_coordinates <= j)]

            y_medians.append(np.median(y_cut))

        self.y_medians = y_medians

    def get_x_coordinates(self, group1: list, group2: list, group3: list) -> list:
        """
        Generates or reads random x coordinates inside the groups.
        :param list group1: group 1 described in the docstring of get_groups()
        :param list group2: group 2 described in the docstring of get_groups()
        :param list group3: group 3 described in the docstring of get_groups()
        :return list: x coordinates
        """
        if os.path.exists(os.path.join(self.data_folder_path, 'x_coordinates.json')):
            with open(os.path.join(self.data_folder_path, 'x_coordinates.json'), 'r') as f:
                x_coordinates_dict = json.load(f)
                x_coordinates = x_coordinates_dict['coordinates']

        else:
            x_range = np.linspace(0, 12, 1201)

            group1_coordinates = random.choices(x_range[150:351], k=len(group1))
            group2_coordinates = random.choices(x_range[500:701], k=len(group2))
            group3_coordinates = random.choices(x_range[850:1051], k=len(group3))

            x_coordinates = group1_coordinates + group2_coordinates + group3_coordinates

            x_coordinates_dict = {'coordinates': x_coordinates}

            with open(os.path.join(self.data_folder_path, 'x_coordinates.json'), 'w') as f:
                json.dump(x_coordinates_dict, f)

        return x_coordinates

    @staticmethod
    def get_groups(df_over_one_mil: pd.DataFrame) -> Tuple[list, list, list]:
        """
        Groups countries based on their income level and BCG policy.
        - group 1: lower middle income countries with universal BCG policy
        - group 2: upper middle income and high income countries with universal BCG policy
        - group 3: upper middle income and high income countries that never had universal
        BCG policy
        :param pd.DataFrame df_over_one_mil: dataframe containing data only for countries with
        more than one million inhabitants
        :return Tuple[list, list, list]: lists of country names in different groups
        """
        group1 = df_over_one_mil[
            (df_over_one_mil['income'] == 2) & (
                    df_over_one_mil['bcg_policy'].astype('int') == 1)
            ]

        group2 = df_over_one_mil[
            ((df_over_one_mil['income'] == 3) | (df_over_one_mil['income'] == 4)) & (
                    df_over_one_mil['bcg_policy'].astype('int') == 1)
            ]

        group3 = df_over_one_mil[
            ((df_over_one_mil['income'] == 3) | (df_over_one_mil['income'] == 4)) & (
                    df_over_one_mil['bcg_policy'].astype('int') == 3)
            ]

        return list(group1.index), list(group2.index), list(group3.index)
