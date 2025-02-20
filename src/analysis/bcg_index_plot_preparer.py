import numpy as np
import pandas as pd
from scipy.stats import linregress

from src.data_handling.data_interface import DataInterface


class BCGIndexPlotPreparer:
    """
    This class prepares everything for the BCG index - deaths/million correlation plot.
    """
    def __init__(self, data_if: DataInterface, countries_type: str,
                 weeks_after_alignment: int, prepare_for_log_plot: bool):
        """
        Constructor.
        :param DataInterface data_if: a DataInterface instance
        :param str countries_type: either 'all' or 'similar'
        :param int weeks_after_alignment: deaths/million data will be collected this many weeks
        after the alignment (alignment means each country's data start from the first nonzero element)
        :param bool prepare_for_log_plot: True if we wish to create a plot with logarithmic y-axis,
        False if not
        """
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
        """
        Filters and aligns data for the given countries, gets x and y coordinates, gets the linear
        regression line and the linear regression parameters.
        """
        deaths_df_filtered = self.filter_data()

        aligned_data = self.align_data(data=deaths_df_filtered)

        self.x_coordinates = np.array(list(self.bcg_index.values()))
        self.y_coordinates = self.get_y_coordinates(aligned_data=aligned_data)

        self.do_linear_regression()

    def filter_data(self) -> pd.DataFrame:
        """
        Filters the dataframe containing the time series for only those countries that
        are in the list of keys of self.bcg_index.
        :return pd.DataFrame: the filtered dataframe
        """
        countries_with_bcg_index = list(self.bcg_index.keys())

        return self.deaths_df[countries_with_bcg_index]

    def get_y_coordinates(self, aligned_data: pd.DataFrame) -> np.ndarray:
        """
        Gets deaths/million data for all countries for the given date.
        :param pd.DataFrame aligned_data: the aligned dataframe
        :return np.ndarray: deaths/million data in order
        """
        y_coordinates = []
        for country in aligned_data.columns:
            y = aligned_data[country][self.weeks_after_alignment]
            y_coordinates.append(y)

        return np.array(y_coordinates)

    def do_linear_regression(self) -> None:
        """
        Does linear regression on the given data, saves fit values and parameters in member
        variables.
        """
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
        """
        Aligns data in the given dataframe. The first elements of the new columns are the first
        nonzero elements of the old columns.
        :param pd.DataFrame data: the given dataframe
        :return pd.DataFrame: the aligned dataframe
        """
        max_len = len(data)
        new_dict = {}

        for col in data.columns:
            nonzero_idx = data[col].ne(0).idxmax()
            pos_idx = data.index.get_loc(nonzero_idx)
            shifted = data[col].iloc[pos_idx:].reset_index(drop=True)
            new_dict[col] = shifted.reindex(range(max_len), fill_value=np.nan)

        return pd.DataFrame(new_dict)
