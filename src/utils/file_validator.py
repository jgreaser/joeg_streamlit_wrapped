# utils/file_validator.py
import zipfile
import json
import pandas as pd
from io import BytesIO

def process_spotify_zip(uploaded_zip):
    """
    Process a Spotify data zip file and extract all audio streaming history.
    
    Args:
        uploaded_zip: StreamlitUploadedFile containing the zip file
    
    Returns:
        dict containing:
            'is_valid': bool
            'error': str (if any)
            'df': pandas DataFrame (if successful)
    """
    try:
        # Read the zip file
        zip_bytes = BytesIO(uploaded_zip.read())
        
        # List to store all audio streaming records
        all_streams = []
        
        with zipfile.ZipFile(zip_bytes) as z:
            # Find all JSON files containing audio history
            audio_files = [f for f in z.namelist() if '_Audio_' in f and f.endswith('.json')]
            
            if not audio_files:
                return {
                    'is_valid': False,
                    'error': 'No audio streaming history files found in zip'
                }
            
            # Process each audio history file
            for file_name in audio_files:
                with z.open(file_name) as f:
                    json_data = json.load(f)
                    all_streams.extend(json_data)
        
        if not all_streams:
            return {
                'is_valid': False,
                'error': 'No streaming data found in files'
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(all_streams)
        
        # Basic validation of required columns
        required_columns = [
            'ts', 'master_metadata_track_name', 
            'master_metadata_album_artist_name', 'ms_played'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return {
                'is_valid': False,
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }
        
        # Convert timestamp to datetime
        df['ts'] = pd.to_datetime(df['ts'])
        
        # Sort by timestamp
        df = df.sort_values('ts')
        
        return {
            'is_valid': True,
            'df': df
        }
        
    except zipfile.BadZipFile:
        return {
            'is_valid': False,
            'error': 'Invalid zip file format'
        }
    except json.JSONDecodeError:
        return {
            'is_valid': False,
            'error': 'Invalid JSON format in streaming history files'
        }
    except Exception as e:
        return {
            'is_valid': False,
            'error': f'Error processing file: {str(e)}'
        }