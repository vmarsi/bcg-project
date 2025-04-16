import json
import os
import random
from typing import Tuple

import numpy as np

from src.data_handling.data_interface import DataInterface


class GermanyStatesPlotPreparer:
    """
    This is a helper class for plotting the deaths data in different German states.
    """
    def __init__(self, data_if: DataInterface, year: str, week: int,
                 data_folder_path: str):
        """
        Constructor.
        :param DataInterface data_if: a DataInterface instance
        :param str year: year as a string
        :param int week: week of the year
        :param str data_folder_path: path of the data folder
        """
        self.data = data_if.deaths_df
        week_str = str(week) if week >= 10 else f'0{week}'
        self.week_date = year + '-W' + week_str
        self.data_folder_path = data_folder_path

        self.x_coordinates = np.array([])
        self.y_coordinates = np.array([])
        self.y_means = []
        self.state_names = []

    def run(self) -> None:
        """
        Run function. Gets the x and y coordinates of the data points representing the states on the
        plot, gets the mean y values in each group.
        """
        self.x_coordinates, self.y_coordinates = self.get_coordinates()

        self.get_y_means()

    def get_coordinates(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Function for getting the x and y coordinates.
        :return Tuple[np.ndarray, np.ndarray]: x and y coordinates in a tuple
        """
        west = ['Bayern', 'Nordrhein-Westfalen', 'Baden-Württemberg', 'Niedersachsen', 'Hessen', 'Rheinland-Pfalz',
                'Saarland', 'Schleswig-Holstein']
        east = ['Brandenburg', 'Thüringen', 'Sachsen-Anhalt', 'Mecklenburg-Vorpommern', 'Sachsen']

        self.state_names = west + east

        x_coordinates = self.get_x_coordinates(group1=west, group2=east)
        y_coordinates = self.get_y_coordinates()

        return np.array(x_coordinates), np.array(y_coordinates)

    def get_x_coordinates(self, group1: list, group2: list) -> list:
        """
        Gets or reads the random x coordinates.
        :param list group1: west german states
        :param list group2: east german states
        :return list: x coordinates
        """
        if os.path.exists(os.path.join(self.data_folder_path, 'x_coordinates_germany_states.json')):
            with open(os.path.join(self.data_folder_path, 'x_coordinates_germany_states.json'), 'r') as f:
                x_coordinates_dict = json.load(f)
                x_coordinates = x_coordinates_dict['coordinates']

        else:
            x_range = np.linspace(0, 6, 601)

            group1_coordinates = random.choices(x_range[50:250], k=len(group1))
            group2_coordinates = random.choices(x_range[350:550], k=len(group2))

            x_coordinates = group1_coordinates + group2_coordinates

            x_coordinates_dict = {'coordinates': x_coordinates}

            with open(os.path.join(self.data_folder_path, 'x_coordinates_germany_states.json'), 'w') as f:
                json.dump(x_coordinates_dict, f)

        return x_coordinates

    def get_y_coordinates(self) -> list:
        """
        Gets the y coordinates (deaths/million).
        :return list: y coordinates in the same order as self.state_names
        """
        y_coordinates = []
        for country in self.state_names:
            y = self.data[country][self.week_date]
            y_coordinates.append(y)

        return y_coordinates

    def get_y_means(self) -> None:
        """
        Gets the mean of the y values in each group.
        """
        cutting_points = [0, 3, 6]

        y_means = []
        for i, j in zip(cutting_points[:-1], cutting_points[1:]):
            y_cut = self.y_coordinates[(i < self.x_coordinates) & (self.x_coordinates <= j)]

            y_means.append(np.mean(y_cut))

        self.y_means = y_means
