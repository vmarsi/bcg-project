import numpy as np
import pandas as pd
from scipy.stats import linregress

from src.analysis.data_aligner import DataAligner
from src.data_handling.data_interface import DataInterface


class LinearRegressionPlotPreparer:
    """
    This class prepares everything for the BCG or vodka index - deaths/million linear regression plot.
    """
    def __init__(self, data_if: DataInterface, countries_type: str,
                 do_align_data: bool, prepare_for_log_plot: bool,
                 save_aligned: bool = False, data_folder_path: str = None):
        """
        Constructor.
        :param DataInterface data_if: a DataInterface instance
        :param bool do_align_data: whether to align data or not
        :param str countries_type: either 'all' or 'similar'
        :param bool prepare_for_log_plot: True if we wish to create a plot with logarithmic y-axis,
        False if not
        """
        self.deaths_df = data_if.deaths_df
        self.do_align_data = do_align_data
        if countries_type == 'all':
            self.index = data_if.index_all_countries_dict
        elif countries_type == 'similar':
            self.index = data_if.index_similar_countries_dict
        else:
            raise Exception('Incorrect type of countries (all/similar).')

        self.prepare_for_log_plot = prepare_for_log_plot
        self.save_aligned = save_aligned
        self.data_folder_path = data_folder_path

        self.x_coordinates = np.array([])
        self.y_coordinates = np.array([])
        self.country_names = []
        self.x_fit = np.array([])
        self.y_fit = np.array([])
        self.slope = float()
        self.intercept = float()
        self.r_squared = float()
        self.p_value = float()

    def run(self, days_after_alignment: int = None,
            date: str = None) -> None:
        """
        Filters and aligns data for the given countries, gets x and y coordinates, gets the linear
        regression line and the linear regression parameters.
        :param int days_after_alignment: deaths/million data will be collected this many days
        after the alignment
        :param str date: the date for which we want to extract the deaths from the NON-aligned df
        """
        deaths_df_filtered = self.filter_data()
        self.x_coordinates = np.array(list(self.index.values()))

        if self.do_align_data:
            aligned_data = self.align_data(data=deaths_df_filtered)
            self.y_coordinates = self.get_y_coordinates(
                data=aligned_data,
                days_after_alignment=days_after_alignment
            )
        else:
            data = deaths_df_filtered
            self.y_coordinates = self.get_y_coordinates(
                data=data, date=date
            )

        self.country_names = list(self.index.keys())

        self.do_linear_regression()

        self.get_r_squared()

    def align_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        :param pd.DataFrame data: filtered deaths dataframe
        Filters countries and aligns data in the given dataframe. The first elements of
        the new columns are the first nonzero elements of the old columns.
        :return pd.DataFrame aligned data
        """
        aligned_data = DataAligner.align_data(data=data)

        if self.save_aligned:
            DataAligner.save_aligned(
                aligned_data=aligned_data,
                data_folder_path=self.data_folder_path
            )

        return aligned_data

    def filter_data(self) -> pd.DataFrame:
        """
        Filters the indices and the dataframe containing the time series for only common countries.
        :return pd.DataFrame: the filtered dataframe
        """
        countries_with_mortality_data = set(self.deaths_df.columns)

        countries_with_index = set(self.index.keys())

        common = countries_with_mortality_data.intersection(countries_with_index)

        self.index = {c: self.index[c] for c in common if c in self.index}

        return self.deaths_df[common]

    def get_y_coordinates(self, data: pd.DataFrame,
                          days_after_alignment: int = None,
                          date: str = None) -> np.ndarray:
        """
        Gets deaths/million data for all countries for the given date.
        :param pd.DataFrame data: the dataframe (aligned or not aligned)
        :param int days_after_alignment: deaths/million data will be collected this many days
        after the alignment (alignment means each country's data start from the first nonzero element)
        :param str date: the date for which we want to extract the deaths from the NON-aligned df
        :return np.ndarray: deaths/million data in order
        """
        y_coordinates = []
        for country in data.columns:
            if self.do_align_data:
                y = data[country][days_after_alignment]
            else:
                y = data[country].loc[date]
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

        self.slope, self.intercept, r_value, self.p_value, std_err = linregress(
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
