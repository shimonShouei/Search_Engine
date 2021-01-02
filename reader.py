import os
import pandas as pd

"""
~~~~~~~~~~~~~~~~~~~~~~~~  Module Description ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    This Module Contains read class , its part is to read parquet files and store them in list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

class ReadFile:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path
        self.files_names = {}
        for root, dirs, files in os.walk(self.corpus_path):
            for file in files:
                if file.endswith(".parquet"):
                    self.files_names[file] = os.path.join(root, file)

    """
        Description : required function for assignment system
    """

    def read_file(self, file_name):
        for root, dirs, files in os.walk(self.corpus_path):
            for file in files:
                if file.endswith(".parquet"):
                    if file_name.__contains__(file):
                        df = pd.read_parquet(os.path.join(root, file), engine="pyarrow")
                        return df.values.tolist()

    """
        Description : read one parquet file
    """

    def read_one_file(self, file_name):
        """
        This function is reading a parquet file contains several tweets
        The file location is given as a string as an input to this function.
        :param file_name: string - indicates the path to the file we wish to read.
        :return: a dataframe contains tweets.
        """
        full_path = self.files_names[file_name]
        df = pd.read_parquet(full_path, engine="pyarrow")
        return df.values.tolist()

