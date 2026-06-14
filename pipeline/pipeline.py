import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_loader import load_config
from extract import extract_stock_data
from transform import transform_stock_data
from load import load_to_database, read_from_database

class StockPipeline:
    def __init__(self, config_path: str = None):
        self.config  = load_config(config_path)
        self.tickers = self.config['tickers']
        self.period  = self.config['data']['period']
        self.df      = None
        self.logger = logging.getLogger(__name__)

    def extract(self):
        self.logger.info("Starting Extract...")
        self.df = extract_stock_data(self.tickers, self.period)
        self.logger.info(f"Extracted {len(self.df)} rows")
        return self

    def transform(self):
        self.logger.info("Starting Transform...")
        self.df = transform_stock_data(self.df)
        self.logger.info(f"Transformed {len(self.df)} rows")
        return self

    def load(self):
        self.logger.info("Starting Load...")
        load_to_database(self.df)
        self.logger.info("Load complete")
        return self

    def run(self):
        """รัน ETL pipeline ทั้งหมดในคำสั่งเดียว"""
        self.logger.info("Pipeline started")
        self.extract().transform().load()
        self.logger.info("Pipeline complete!")
        return self

    def summary(self):
        """สรุปข้อมูลใน database"""
        df = read_from_database(
            "SELECT ticker, COUNT(*) as rows, MIN(date) as start, MAX(date) as end FROM stock_prices GROUP BY ticker"
        )
        print("\nDatabase Summary:")
        print(df.to_string(index=False))

if __name__ == "__main__":
    pipeline = StockPipeline()
    pipeline.run()
    pipeline.summary()