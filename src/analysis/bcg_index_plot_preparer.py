import numpy as np
import pandas as pd
from scipy.stats import linregress

from src.data_handling.data_interface import DataInterface


class BCGIndexPlotPreparer:
    def __init__(self, data_if: DataInterface, countries_type: str,
                 weeks_after_alignment: int, prepare_for_log_plot: bool):
        self.deaths_df = data_if.deaths_df
        if countries_type == 'all':
            self.bcg_index = data_if.bcg_index_dict
        elif countries_type == 'similar':
            self.bcg_index = data_if.bcg_index_similar_dict
        else:
            raise Exception('Incorrect type of countries (all/similar).')

        self.weeks_after_alignment = weeks_after_alignment
        self.prepare_for_log_plot = prepare_for_log_plot

        self.x_coordinates = np.array([])
        self.y_coordinates = np.array([])
        self.x_fit = np.array([])
        self.y_fit = np.array([])
        self.slope = float()
        self.intercept = float()

    def run(self) -> None:
        deaths_df_filtered = self.filter_data()

        aligned_data = self.align_data(data=deaths_df_filtered)

        self.x_coordinates = np.array(list(self.bcg_index.values()))
        self.y_coordinates = self.get_y_coordinates(aligned_data=aligned_data)

        self.do_linear_regression()

    def filter_data(self) -> pd.DataFrame:
        countries_with_bcg_index = list(self.bcg_index.keys())

        return self.deaths_df[countries_with_bcg_index]

    def get_y_coordinates(self, aligned_data: pd.DataFrame) -> np.ndarray:
        y_coordinates = []
        for country in aligned_data.columns:
            y = aligned_data[country][self.weeks_after_alignment]
            y_coordinates.append(y)

        return np.array(y_coordinates)

    def do_linear_regression(self) -> None:
        if self.prepare_for_log_plot:
            y = np.log(self.y_coordinates)
        else:
            y = self.y_coordinates

        self.slope, self.intercept, r_value, p_value, std_err = linregress(
            self.x_coordinates, y
        )

        self.x_fit = np.linspace(self.x_coordinates.min(), self.x_coordinates.max(), 100)
        if self.prepare_for_log_plot:
            self.y_fit = np.exp(self.slope * self.x_fit + self.intercept)
        else:
            self.y_fit = self.slope * self.x_fit + self.intercept

    @staticmethod
    def align_data(data: pd.DataFrame) -> pd.DataFrame:
        max_len = len(data)
        new_dict = {}

        for col in data.columns:
            nonzero_idx = data[col].ne(0).idxmax()
            pos_idx = data.index.get_loc(nonzero_idx)
            shifted = data[col].iloc[pos_idx:].reset_index(drop=True)
            new_dict[col] = shifted.reindex(range(max_len), fill_value=np.nan)

        return pd.DataFrame(new_dict)
