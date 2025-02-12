import random
from datetime import datetime, timedelta
from typing import Tuple

import numpy as np
import pandas as pd

from src.data_handling.data_handler import DataHandler


class GroupCoordinateCreator:
    def __init__(self, data_handler: DataHandler, date: str):
        self.dl = data_handler.dl
        self.data_if = data_handler.data_if
        self.date = date

        self.x_coordinates = []
        self.y_coordinates = []

    def run(self):
        df_over_one_mil = self.filter_over_one_million()

        self.x_coordinates, self.y_coordinates = self.get_coordinates(
            df_over_one_mil=df_over_one_mil
        )

    def filter_over_one_million(self) -> pd.DataFrame:
        df_over_one_mil = self.dl.meta_data[self.dl.meta_data['Population'] >= 1000000]

        return df_over_one_mil

    def get_coordinates(self, df_over_one_mil: pd.DataFrame) -> Tuple[list, list]:
        group1, group2, group3 = self.get_groups(df_over_one_mil=df_over_one_mil)

        grouped_countries = list(group1.index) + list(group2.index) + list(group3.index)

        x_coordinates = self.get_x_coordinates(group1=group1, group2=group2, group3=group3)
        y_coordinates = self.get_y_coordinates(grouped_countries=grouped_countries)

        return x_coordinates, y_coordinates

    def get_y_coordinates(self, grouped_countries: list) -> list:
        date_obj = datetime.strptime(self.date, '%Y-%m-%d')
        final_date = date_obj + timedelta(days=6)
        y_coordinates = []
        for country in grouped_countries:
            y = self.data_if.deaths_df[country][self.date:final_date].values[0]
            y_coordinates.append(y)

        return y_coordinates

    @staticmethod
    def get_groups(df_over_one_mil: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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

        return group1, group2, group3

    @staticmethod
    def get_x_coordinates(group1: pd.DataFrame, group2: pd.DataFrame, group3: pd.DataFrame) -> list:
        x_range = np.linspace(0, 12, 1201)

        group1_coordinates = random.choices(x_range[150:351], k=len(group1))
        group2_coordinates = random.choices(x_range[500:701], k=len(group2))
        group3_coordinates = random.choices(x_range[850:1051], k=len(group3))

        x_coordinates = group1_coordinates + group2_coordinates + group3_coordinates

        return x_coordinates
