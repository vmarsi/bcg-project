import numpy as np
import pandas as pd

from src.data_handling.data_interface import DataInterface
from src.data_handling.dataloader import DataLoader


class DataHandler:
    def __init__(self, dl: DataLoader):
        self.dl = dl

        self.data_if = DataInterface()

    def run(self) -> None:
        countries_inter = self.get_countries_intersection()
        self.dl.meta_data = self.dl.meta_data.loc[countries_inter]
        self.dl.time_series_data = self.dl.time_series_data[
            self.dl.time_series_data['Country'].isin(countries_inter)
        ]

        data = {
            'cases_df': self.get_df(countries_inter=countries_inter, data_type='cases',
                                    period=7),
            'deaths_df': self.get_df(countries_inter=countries_inter, data_type='deaths',
                                     period=7)
        }

        self.data_if = DataInterface(data=data)

    def get_countries_intersection(self) -> list:
        countries = set(self.dl.time_series_data['Country'].values)
        countries_2 = set(self.dl.meta_data.index)

        return list(countries.intersection(countries_2))

    def get_df(self, countries_inter: list, data_type: str, period: int) -> pd.DataFrame:
        date_range = pd.date_range(start='2020-01-04', end='2025-01-12', freq=f'{period}D')

        all_values = []
        for country in countries_inter:
            country_df = self.dl.time_series_data[self.dl.time_series_data['Country'] == country]

            pop = float(
                str(
                    self.dl.meta_data.loc[country]['Population']
                ).replace(',', '')
            )

            values = np.array(
                country_df[f'Cumulative_{data_type}'].values.tolist()[::period]
            ) / pop * 1000000

            all_values.append(values)

        df = pd.DataFrame(np.array(all_values).T, index=date_range, columns=countries_inter)

        return df
