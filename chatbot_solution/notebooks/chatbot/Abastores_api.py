import pandas as pd
import requests
import logging

class Abastores:
    def __init__(self, base_url="https://api.abastores.com/api/v2/marketdata/"):
        self.base_url = base_url
        logging.basicConfig(level=logging.INFO)
        
    def normalize(self, data):
        """Normalize JSON data into a pandas DataFrame.""" 
        return pd.json_normalize(data['results'])

    def dataprice(self, page_size=1000, max_pages=37)  -> pd.DataFrame:
        """
        Retrieve price data from the API, handling pagination.
        
        Parameters:
        page_size (int): The number of records per page.
        max_pages (int): The maximum number of pages to retrieve.
        
        Returns:
        pd.DataFrame: The concatenated DataFrame of all retrieved data.
        """
        all_data = []
        for page_number in range(1, max_pages + 1):
            url = f"{self.base_url}dataprice-rag/?page={page_number}&page_size=1000"
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                normalized_data = self.normalize(data)
                all_data.append(normalized_data)
                logging.info(f"Successfully retrieved data for page {page_number}")
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to retrieve data for page {page_number}. Error: {e}")
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        else:
            return pd.DataFrame()
            