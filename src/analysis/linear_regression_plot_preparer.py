import numpy as np
import pandas as pd
from scipy.stats import linregress

from src.data_handling.data_interface import DataInterface


class LinearRegressionPlotPreparer:
    """
    This class prepares everything for the BCG or vodka index - deaths/million linear regression plot.
    """
    def __init__(self, data_if: DataInterface, countries_type: str,
                 days_after_alignment: int, prepare_for_log_plot: bool):
        """
        Constructor.
        :param DataInterface data_if: a DataInterface instance
        :param str countries_type: either 'all' or 'similar'
        :param int days_after_alignment: deaths/million data will be collected this many days
        after the alignment (alignment means each country's data start from the first nonzero element)
        :param bool prepare_for_log_plot: True if we wish to create a plot with logarithmic y-axis,
        False if not
        """
        self.deaths_df = data_if.deaths_df
        if countries_type == 'all':
            self.index = data_if.index_all_countries_dict
        elif countries_type == 'similar':
            self.index = data_if.index_similar_countries_dict
        else:
            raise Exception('Incorrect type of countries (all/similar).')

        self.days_after_alignment = days_after_alignment
        self.prepare_for_log_plot = prepare_for_log_plot

        self.x_coordinates = np.array([])
        self.y_coordinates = np.array([])
        self.country_names = []
        self.x_fit = np.array([])
        self.y_fit = np.array([])
        self.slope = float()
        self.intercept = float()
        self.r_squared = float()

    def run(self) -> None:
        """
        Filters and aligns data for the given countries, gets x and y coordinates, gets the linear
        regression line and the linear regression parameters.
        """
        deaths_df_filtered = self.filter_data()

        aligned_data = self.align_data(data=deaths_df_filtered)

        self.x_coordinates = np.array(list(self.index.values())) ** 0.5
        self.y_coordinates = self.get_y_coordinates(aligned_data=aligned_data)

        self.country_names = list(self.index.keys())

        self.do_linear_regression()

        self.get_r_squared()

    def filter_data(self) -> pd.DataFrame:
        """
        Filters the dataframe containing the time series for only those countries that
        are in the list of keys of self.index.
        :return pd.DataFrame: the filtered dataframe
        """
        countries_with_index = list(self.index.keys())

        return self.deaths_df[countries_with_index]

    def get_y_coordinates(self, aligned_data: pd.DataFrame) -> np.ndarray:
        """
        Gets deaths/million data for all countries for the given date.
        :param pd.DataFrame aligned_data: the aligned dataframe
        :return np.ndarray: deaths/million data in order
        """
        y_coordinates = []
        for country in aligned_data.columns:
            y = aligned_data[country][self.days_after_alignment]
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

    def get_r_squared(self) -> None:
        """
        Gets R^2 of the regression line.
        """
        fit_values = []
        for x in self.x_coordinates:
            if self.prepare_for_log_plot:
                fit_values.append(np.exp(self.slope * x + self.intercept))
            else:
                fit_values.append(self.slope * x + self.intercept)

        numerator = np.sum((self.y_coordinates - fit_values) ** 2)
        denominator = np.sum((self.y_coordinates - np.mean(self.y_coordinates)) ** 2)

        self.r_squared = 1 - numerator / denominator

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
