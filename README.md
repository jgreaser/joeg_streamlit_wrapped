# JoeG Streamlit Wrapped

A multi-page Streamlit application for wrapped-style analytics visualization.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/joeg_streamlit_wrapped.git
   cd joeg_streamlit_wrapped
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # for development
   ```

4. Create a `.env` file:
   ```
   DEBUG=True
   API_KEY=your_api_key_here
   ```

5. Run the application:
   ```bash
   streamlit run src/app.py
   ```