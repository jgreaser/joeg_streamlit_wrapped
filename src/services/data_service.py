import pandas as pd

class DataService:
    """Service class for handling data operations."""
    
    @staticmethod
    def load_data(file_path: str) -> pd.DataFrame:
        """Load data from a file."""
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    @staticmethod
    def process_data(df: pd.DataFrame) -> pd.DataFrame:
        """Process the dataframe."""
        # Add your data processing logic here
        return df