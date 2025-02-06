import numpy as np
import pandas as pd

from src.data_handling.data_interface import DataInterface
from src.data_handling.dataloader import DataLoader


class DataHandler:
    def __init__(self, dl: DataLoader):
        self.dl = dl

        self.data_if = DataInterface()

    def run(self):
        countries_inter = self.get_countries_intersection()

        data = {
            'cases_df': self.get_df(countries_inter=countries_inter, data_type='cases'),
            'deaths_df': self.get_df(countries_inter=countries_inter, data_type='deaths')
        }

        self.data_if = DataInterface(data=data)

    def get_countries_intersection(self):
        countries = list(set(self.dl.time_series_data['Country'].values))
        countries_2 = list(set(self.dl.meta_data['Country'].values))

        return list(set(countries).intersection(set(countries_2)))

    def get_df(self, countries_inter: list, data_type: str):
        date_range = pd.date_range(start='2020-01-04', end='2025-01-12', freq='7D')

        df = pd.DataFrame(index=date_range)
        for country in countries_inter:
            df = self.dl.time_series_data[self.dl.time_series_data['Country'] == country]
            pop = float(
                str(
                    self.dl.meta_data[self.dl.meta_data['Country'] == country].values[0][2]
                ).replace(',', '')
            )
            values = np.array(df[f'Cumulative_{data_type}'].values.to_list()[::7]) / pop * 1000000
            df[country] = values

        return df
