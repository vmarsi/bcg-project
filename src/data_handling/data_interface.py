import pandas as pd


class DataInterface:
    """
    Class for storing data created in DataHandler.
    """
    def __init__(self, data: dict = None):
        """
        Constructor.
        :param dict data: dictionary with the following keys:
        - 'cases_df'
        - 'deaths_df'
        """
        self.cases_df = pd.DataFrame()
        self.deaths_df = pd.DataFrame()

        if data is not None:
            for key, value in data.items():
                setattr(self, key, value)
