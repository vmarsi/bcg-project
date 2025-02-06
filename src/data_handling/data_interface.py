import pandas as pd


class DataInterface:
    def __init__(self, data: dict = None):
        cases_df = pd.DataFrame()
        deaths_df = pd.DataFrame()

        if data is not None:
            for key, value in data.items():
                setattr(self, key, value)
