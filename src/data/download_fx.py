import yfinance as yf
import pandas as pd
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)

def download_yf_monthly(ticker, out_name):
    logging.info(f"Downloading {ticker} from yfinance")
    df = yf.download(ticker, start="2004-01-01", end="2026-01-01", interval="1mo")
    if df.empty:
        logging.error(f"Failed to download {ticker}")
        return
    
    # We only need Close
    df = df[['Close']].reset_index()
    # yfinance multi-index columns fix if needed
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['date', 'fx_rate']
    else:
        df.columns = ['date', 'fx_rate']
        
    df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
    # Ensure end of month or start of month? 
    # Usually we just merge on year-month
    df['date'] = df['date'].dt.to_period('M').dt.to_timestamp()
    
    df['fx_rate'] = df['fx_rate'].ffill()
    
    out_path = config.RAW_DIR / out_name
    df.to_csv(out_path, index=False)
    logging.info(f"Saved {out_name} to {out_path}")

if __name__ == "__main__":
    download_yf_monthly('JPY=X', 'fx_japan.csv')
    download_yf_monthly('KRW=X', 'fx_korea.csv')
