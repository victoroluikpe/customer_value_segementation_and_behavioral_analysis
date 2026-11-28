import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from src.data.data_ingestion import DataIngestion
from src.data.data_validation import DataValidation

pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 200)
pd.set_option("display.float", lambda x: f"{x:,.2f}")
from src.logger import configure_logger
from src.Exception import MyException
from src.config.constant import asset_to_currency, currency_to_asset
import sys

logging = configure_logger()

def DataCleaning(customer_transaction_data):
    try:
        mask = customer_transaction_data["TransactionCurrency"].isna() & customer_transaction_data["AssetType"].isin(asset_to_currency)
        customer_transaction_data.loc[mask, "TransactionCurrency"] = customer_transaction_data.loc[mask, "AssetType"].map(asset_to_currency)
        logging.info(f"Rule 1 filled: {mask.sum():,}")



        # Rule 2 - wallet - only movements default to GBP
        mask = customer_transaction_data["TransactionCurrency"].isna() & (customer_transaction_data["WalletActivity"] == 1)
        customer_transaction_data.loc[mask, "TransactionCurrency"] = "GBP"
        logging.info(f"Rule 2 filled: {mask.sum():,}")



        # Rule 3 - Everything else-> GBP (home currency)
        mask = customer_transaction_data["TransactionCurrency"].isna()
        customer_transaction_data.loc[mask, "TransactionCurrency"] = "GBP"
        logging.info(f"Rule 3 filled: {mask.sum():,}")

        logging.info(f"\nRemaining TransactionCurrency nulls: {customer_transaction_data["TransactionCurrency"].isna().sum()}")
        mask = customer_transaction_data["AssetType"].isna()
        customer_transaction_data.loc[mask, "AssetType"] = customer_transaction_data.loc[mask, "TransactionCurrency"].map(currency_to_asset)

        logging.info(f"AssetType filled from currency: {mask.sum():,}")
        logging.info(f"remaining AssetType nulls: {customer_transaction_data["AssetType"].isna().sum()}")

        # safety net  anything still null (shouldnt be) --Traditional
        customer_transaction_data["AssetType"] = customer_transaction_data["AssetType"].fillna("Traditional")
        mode_per_customer = customer_transaction_data.groupby("CustomerID")["CustLocation"].transform(
            lambda s: s.dropna().mode().iloc[0] if s.notna().any() else np.nan
        )

        customer_transaction_data["CustLocation"] = customer_transaction_data["CustLocation"].fillna(mode_per_customer).fillna("unknown")

        logging.info(f"Remaining CustLocation nulls: {customer_transaction_data["CustLocation"].isna().sum()}")

        return customer_transaction_data

    except Exception as e:
        logging.error(f"Error occured during data cleaning: {e}")
        raise MyException(e, sys)

#customer_transaction_data = DataIngestion()
#customer_transaction_data = DataValidation(customer_transaction_data)
#cleaned_customer_transaction_data = DataCleaning(customer_transaction_data)