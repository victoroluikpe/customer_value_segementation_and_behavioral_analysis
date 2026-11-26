import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.join(__file__))))

DB_PATH = os.path.join(BASE_DIR, "customer_data", "vault_chain_flow.db")
TABLE = "customer_Transactions"