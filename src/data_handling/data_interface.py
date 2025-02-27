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
        - 'index_all_countries_dict'
        - 'index_similar_countries_dict'
        """
        self.cases_df = pd.DataFrame()
        self.deaths_df = pd.DataFrame()
        self.index_all_countries_dict = {}
        self.index_similar_countries_dict = {}

        if data is not None:
            for key, value in data.items():
                setattr(self, key, value)
