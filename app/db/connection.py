import os
import requests
from typing import List, Dict, Any, Optional
from app.constants import (CLOUDFLARE_ACCOUNT_ID,
                           CLOUDFLARE_DATABASE_ID,
                           CLOUDFLARE_API_TOEKN,
                           CLOUDFLARE_BASE_URL)
from app.core.logging import Logger
from app.core.logging import Logger
logger = Logger(__name__)

logging = Logger()


class D1Connection:
    def __init__(self):
        logger.info(f"Entered __init__ of D1Connection")
        self.account_id = CLOUDFLARE_ACCOUNT_ID
        self.database_id = CLOUDFLARE_DATABASE_ID
        self.api_token = CLOUDFLARE_API_TOEKN

        if not all([self.account_id, self.database_id, self.api_token]):
            logging.error(
                "Missing required Cloudflare D1 environment variables.")

        self.base_url = CLOUDFLARE_BASE_URL[0] + self.account_id + \
            CLOUDFLARE_BASE_URL[1] + self.database_id + CLOUDFLARE_BASE_URL[2]
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        logger.info(f"Entered query of D1Connection with sql={sql}, params={params}")
        """
        Execute SQL Query
        """
        logger.info(f"Entered query of D1Connection with sql={sql}, params={params}")
        payload = {
            "sql": sql,
            "params": params or []
        }

        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload)
        response.raise_for_status()

        data = response.json()

        if not data.get("success"):
            errors = data.get("errors", [])
            logging.error(f"D1 Query failed: {errors}")

        try:
            return data["result"][0].get("results", [])
        except (KeyError, IndexError) as e:
            logging.error(f"Caught error in D1Connection {e}")
