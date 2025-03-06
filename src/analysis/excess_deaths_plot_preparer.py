import json
import os
import random
from typing import Tuple

import numpy as np

from src.data_handling.euromomo_data_handler import EUROMOMODataHandler


class ExcessDeathsPlotPreparer:
    """
    This is a helper class for plotting the excess deaths.
    """
    def __init__(self, data_handler: EUROMOMODataHandler,
                 year: str, week: int, data_folder_path: str):
        """
        Constructor.
        :param EUROMOMODataHandler data_handler: a EUROMOMODataHandler instance
        :param str year: year as a string
        :param int week: week of the year
        :param str data_folder_path: path of the data folder
        """
        self.data = data_handler.data_if.deaths_df
        week_str = str(week) if week >= 10 else f'0{week}'
        self.week_date = year + '-' + week_str
        self.data_folder_path = data_folder_path

        self.x_coordinates = np.array([])
        self.y_coordinates = np.array([])
        self.y_medians = []

    def run(self) -> None:
        """
        Run function. Gets the x and y coordinates of the data points representing the countries on the
        plot, gets the median y values in each group.
        """
        self.x_coordinates, self.y_coordinates = self.get_coordinates()

        self.get_y_medians()

    def get_coordinates(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Function for getting the x and y coordinates.
        :return Tuple[np.ndarray, np.ndarray]: x and y coordinates in a tuple
        """
        group1 = ['Greece', 'Estonia', 'Ireland', 'Portugal', 'Hungary']
        group2 = ['Belgium', 'Italy', 'Netherlands']

        grouped_countries = group1 + group2

        x_coordinates = self.get_x_coordinates(group1=group1, group2=group2)
        y_coordinates = self.get_y_coordinates(grouped_countries=grouped_countries)

        return np.array(x_coordinates), np.array(y_coordinates)

    def get_x_coordinates(self, group1: list, group2: list) -> list:
        """
        Gets or reads the random x coordinates.
        :param list group1: countries with universal BCG policy
        :param list group2: countries without universal BCG policy
        :return list: x coordinates
        """
        if os.path.exists(os.path.join(self.data_folder_path, 'x_coordinates_excess.json')):
            with open(os.path.join(self.data_folder_path, 'x_coordinates_excess.json'), 'r') as f:
                x_coordinates_dict = json.load(f)
                x_coordinates = x_coordinates_dict['coordinates']

        else:
            x_range = np.linspace(0, 10, 1001)

            group1_coordinates = random.choices(x_range[200:400], k=len(group1))
            group2_coordinates = random.choices(x_range[600:800], k=len(group2))

            x_coordinates = group1_coordinates + group2_coordinates

            x_coordinates_dict = {'coordinates': x_coordinates}

            with open(os.path.join(self.data_folder_path, 'x_coordinates_excess.json'), 'w') as f:
                json.dump(x_coordinates_dict, f)

        return x_coordinates

    def get_y_coordinates(self, grouped_countries: list) -> list:
        """
        Gets the y coordinates (excess deaths).
        :param list grouped_countries: all country names in a list in a specific order
        (countries in the same group are next to each other)
        :return list: y coordinates in the same order as grouped_countries
        """
        y_coordinates = []
        for country in grouped_countries:
            y = self.data[country][self.week_date]
            y_coordinates.append(y)

        return y_coordinates

    def get_y_medians(self) -> None:
        """
        Gets the medians of the y values in each group.
        """
        cutting_points = [0, 5, 10]

        y_medians = []
        for i, j in zip(cutting_points[:-1], cutting_points[1:]):
            y_cut = self.y_coordinates[(i < self.x_coordinates) & (self.x_coordinates <= j)]

            y_medians.append(np.median(y_cut))

        self.y_medians = y_medians
