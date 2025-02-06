import pandas as pd


class DataInterface:
    def __init__(self, data: dict = None):
        self.cases_df = pd.DataFrame()
        self.deaths_df = pd.DataFrame()

        if data is not None:
            for key, value in data.items():
                setattr(self, key, value)
