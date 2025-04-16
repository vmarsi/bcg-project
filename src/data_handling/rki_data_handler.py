import numpy as np
import pandas as pd

from src.data_handling.data_interface import DataInterface
from src.data_handling.dataloader import DataLoader


class RKIDataHandler:
    """
    Class for processing data from the Robert Koch Institute.
    """
    def __init__(self, dl: DataLoader):
        """
        Constructor.
        :param DataLoader dl: a DataLoader instance
        """
        self.dl = dl

        self.data_if = DataInterface()

    def run(self) -> None:
        """
        Run function. Gets the processed dataframe.
        """
        data = {
            'deaths_df': self.get_df()
        }

        self.data_if = DataInterface(data=data)

    def get_df(self) -> pd.DataFrame:
        """
        Creates the processed dataframe. Indices are weeks, columns are german states, values are
        deaths per million.
        :return pd.DataFrame: the processed dataframe
        """
        df_indices = sorted(set(list(self.dl.time_series_data.index)))
        state_names = list(self.dl.meta_data.index)[:-1]

        all_values = []
        for state in state_names:
            state_df = self.dl.time_series_data[self.dl.time_series_data['State'] == state]

            pop = self.dl.meta_data.loc[state]['Population']

            values = np.array(
                state_df['Deaths_total'].values.tolist()
            ) / pop * 1000000

            all_values.append(list(values))

        return pd.DataFrame(np.array(all_values).T, index=df_indices, columns=state_names)
