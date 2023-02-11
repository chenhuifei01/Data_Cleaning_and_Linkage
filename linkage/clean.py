import re
import pathlib
from .datatypes import CleanedData
import pandas as pd

def clean_ppp_data():
    """
    This function should load the data from data/il-ppp.csv
    and return a list of CleanedData tuples.
    * For PPP data you should use the ID, BorrowerName, BorrowerCity, and BorrowerZip
    * All data should be converted to lowercase & stripped of leading and trailing whitespace.
    * All zip codes should be 5 digits long.
    Returns:
        A list of CleanedData tuples
    """
    filename = pathlib.Path(__file__).parent / "data/il-ppp.csv"
    # TODO: Implement this function
    data = pd.read_csv(filename)
    data = data[['ID', 'BorrowerName', 'BorrowerCity', 'BorrowerZip']]
    data['ID'] = data['ID'].astype('str')
    data['BorrowerZip'] = data['BorrowerZip'].str[:5]
    data = data.apply(lambda x: x.str.strip())
    data = data.apply(lambda x: x.str.lower())
    data['ID'] = data['ID'].astype('int64')

    data = data.set_axis(['id','org_name','city','zip'],axis = 1)
    answer = list(data.itertuples(index = False))

    return answer

def clean_opensecrets_data():
    """
    This function should load the data from data/il_opensecrets.csv
    and return a list of CleanedData tuples.
    * Drop any rows where the Orgname is "Self Employed" with or without a hyphen.
    * All data should be converted to lowercase & stripped of leading and trailing whitespace.
    * All zip codes should be 5 digits long.
    Returns:
        A list of CleanedData tuples
    """
    filename = pathlib.Path(__file__).parent / "data/il_opensecrets_orgs.csv"
    data = pd.read_csv(filename)
    data['ID'] = data['ID'].astype('str')
    data['Zip'] = data['Zip'].str[:5]
    data = data.apply(lambda x: x.str.strip())
    data = data.apply(lambda x: x.str.lower())
    data = data[~data['Orgname'].str.match('.*self-?employed.*')]
    data['ID'] = data['ID'].astype('int64')

    data = data.set_axis(['id','org_name','city','zip'],axis = 1)
    answer = list(data.itertuples(index = False))


    return answer