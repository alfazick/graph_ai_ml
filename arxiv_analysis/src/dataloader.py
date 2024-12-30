

import pandas as pd

class DataLoader:
    def __init__(self):
        pass

    def load_data(self,path,format,columns) -> pd.DataFrame:
        if format == "tsv":
            df = pd.read_csv(path, sep="\t", header=None)
            df.columns = columns
            return df
        else:
            raise ValueError("Unsupported file format")


