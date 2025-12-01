import requests
from requests.exceptions import HTTPError
import json
import os
from dotenv import load_dotenv
from modules.common.common import set_logger
from time import time

load_dotenv()
logger = set_logger()


class AIMSSaaSAPIClient:
    BASE_URL = os.getenv("AIMS_SAAS_URL")

    def __init__(self):
        self.username = os.getenv("AIMS_SAAS_USERNAME", None)
        self.password = os.getenv("AIMS_SAAS_PASSWORD", None)
        self.access_token = None
        self.refresh_token = None
        self.access_token_expiry = 0  # Unix timestamp for token expiration
        self.company = os.getenv("AIMS_SAAS_COMPANY", None)

    def get_access_token(self):
        """
        Retrieve a valid authentication token using username/password.
        Automatically refreshes if missing or expired.
        """
        if self.access_token and time() < self.access_token_expiry:
            return self.access_token

        endpoint = f"{self.BASE_URL}/api/v2/token"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        data = {"username": self.username, "password": self.password}

        response = requests.post(endpoint, headers=headers, data=json.dumps(data))
        response.raise_for_status()

        token_data = response.json()["responseMessage"]
        self.access_token = token_data["access_token"]
        self.refresh_token = token_data["refresh_token"]
        # Set expiry 1 minute earlier than 1 hour
        self.access_token_expiry = time() + 3600 - 60

        logger.info("Successfully obtained new access token.")
        return self.access_token

    # ------------------- Existing methods updated to ensure fresh token -------------------

    def get_article_upload_format(self):
        self.get_access_token()
        endpoint = f"{self.BASE_URL}/api/v2/common/articles/upload/format"
        params = {"company": self.company}
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        response = requests.put(endpoint, headers=headers, params=params)
        if response.status_code in (200, 202):
            return response.json()
        else:
            response.raise_for_status()

    def add_articles(self, store_code, articles, chunk_size=5000):
        self.get_access_token()
        endpoint = f"{self.BASE_URL}/api/v2/common/articles"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        params = {"company": self.company, "store": store_code}
        last_response = None

        while articles:
            chunk, articles = articles[:chunk_size], articles[chunk_size:]
            try:
                response = requests.put(
                    endpoint, headers=headers, params=params, json=chunk, timeout=20
                )
            except Exception as e:
                logger.error(f"HTTP request failed: {e}")
                return None

            last_response = response
            if response.status_code not in (200, 202):
                logger.error(
                    f"Error sending articles: {response.status_code} → {response.text}"
                )
                return response

            logger.debug(
                f"Sent {len(chunk)} articles for store {store_code}, {len(articles)} pending"
            )

        return last_response

    def get_article(self, store_code, article_id):
        self.get_access_token()
        endpoint = f"{self.BASE_URL}/api/v1/articles/article"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        params = {
            "company": self.company,
            "stationCode": store_code,
            "articleId": article_id,
        }

        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code not in (200, 202):
            logger.error(response.json().get("responseMessage", ""))
            response.raise_for_status()
        logger.debug(f"Got {article_id} for store {store_code}")
        return response.json()

    def unlink_label(self, label_code):
        self.get_access_token()
        endpoint = f"{self.BASE_URL}/api/v1/labels/unlink"
        params = {"company": self.company, "labelCode": label_code}
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        response = requests.post(endpoint, headers=headers, params=params)
        if response.status_code in (200, 202):
            return response.json()
        else:
            response.raise_for_status()


def main():
    company = "SEG"
    label_code = "05F0A1B4B09C"
    client = AIMSSaaSAPIClient()
    print(f"Retrieved Access Token: {access_token}")
    print(f"Retrieved Refresh Token: {client.refresh_token}")

    try:
        result = client.unlink_label(label_code)
        print(f"Unlink result: {result}")
    except HTTPError as http_err:
        print(
            f"HTTP error occurred while unlinking label {label_code} for company {company}. "
            f"Error: {http_err}, Response: {http_err.response.text}"
        )
    except Exception as e:
        print(f"Error unlinking label {label_code} for company {company}. Error: {e}")


if __name__ == "__main__":
    main()
