#!/usr/bin/env python3
"""
Tiger Trade API - Exchanges Module (/exchanges endpoint)
"""

EXCHANGES_PARAMS = {
    "active_only": True,
    "with_stats": True,
}

import json
import requests
import os
from typing import Dict, Any, Optional

class TigerTradeAPIException(Exception):
    pass

class ExchangesAPI:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Ищем config.json в родительской папке
            config_path = os.path.join(os.path.dirname(script_dir), "config.json")

        self.config_path = config_path
        self.config = self._load_config()
        self.base_url = self.config['api']['base_url']
        self.timeout = self.config['api'].get('timeout', 30)
        self.access_token = None
        self.session = requests.Session()
        
        self._ensure_valid_token()
        self._update_headers()
    
    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise TigerTradeAPIException(f"Config not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise TigerTradeAPIException(f"Invalid JSON: {e}")
    
    def _save_token_to_config(self, token: str):
        try:
            self.config['auth']['access_token'] = token
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save token: {e}")
    
    def _test_token(self, token: str) -> bool:
        if not token:
            return False
        
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/exchanges",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def _refresh_token(self) -> str:
        current_token = self.config['auth'].get('access_token')
        refresh_token = self.config['auth'].get('refresh_token')
        
        if not current_token or not refresh_token:
            return self._generate_new_token()
        
        refresh_url = self.config['api']['refresh_url']
        refresh_data = {"accessToken": current_token}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Cookie': f'refreshToken={refresh_token}'
        }
        
        response = requests.post(refresh_url, json=refresh_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'accessToken' in result:
                token = result['accessToken']
                self._save_token_to_config(token)
                
                for cookie in response.cookies:
                    if cookie.name == 'refreshToken':
                        self.config['auth']['refresh_token'] = cookie.value
                        with open(self.config_path, 'w', encoding='utf-8') as f:
                            json.dump(self.config, f, indent=4, ensure_ascii=False)
                        break
                
                return token
            else:
                return self._generate_new_token()
        else:
            return self._generate_new_token()
    
    def _generate_new_token(self) -> str:
        username = self.config['auth'].get('username')
        password = self.config['auth'].get('password')
        
        if not username or not password:
            raise TigerTradeAPIException("Username and password required")
        
        auth_url = self.config['api']['auth_url']
        auth_data = {"username": username, "password": password}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        
        response = requests.post(auth_url, json=auth_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'accessToken' in result:
                token = result['accessToken']
                self._save_token_to_config(token)
                
                for cookie in response.cookies:
                    if cookie.name == 'refreshToken':
                        self.config['auth']['refresh_token'] = cookie.value
                        with open(self.config_path, 'w', encoding='utf-8') as f:
                            json.dump(self.config, f, indent=4, ensure_ascii=False)
                        break
                
                return token
            else:
                raise TigerTradeAPIException(f"No accessToken in response: {result}")
        elif response.status_code == 400:
            try:
                error_response = response.json()
                error_desc = error_response.get('detail', 'Unknown error')
            except:
                error_desc = response.text
            raise TigerTradeAPIException(f"Auth API error: {error_desc}")
        elif response.status_code == 429:
            raise TigerTradeAPIException("Rate limit exceeded")
        else:
            raise TigerTradeAPIException(f"Auth error: {response.status_code} - {response.text}")
    
    def _ensure_valid_token(self):
        existing_token = self.config['auth'].get('access_token')
        
        if existing_token and self._test_token(existing_token):
            self.access_token = existing_token
            return
        
        self.access_token = self._refresh_token()
    
    def _update_headers(self):
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Tiger Trade API Client/1.0',
            'Origin': 'https://statistics-api.tiger.trade',
            'Referer': 'https://statistics-api.tiger.trade/'
        })
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                self._ensure_valid_token()
                self._update_headers()
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=self.timeout
                )
            
            if response.status_code == 417:
                raise TigerTradeAPIException(f"Expectation Failed (417): {endpoint}")
            elif response.status_code == 429:
                raise TigerTradeAPIException("Rate limit exceeded (429)")
            elif response.status_code >= 400:
                raise TigerTradeAPIException(f"HTTP {response.status_code}: {response.text}")
            
            try:
                return response.json()
            except json.JSONDecodeError:
                return {'raw_response': response.text}
                
        except requests.exceptions.Timeout:
            raise TigerTradeAPIException(f"Timeout: {url}")
        except requests.exceptions.ConnectionError:
            raise TigerTradeAPIException(f"Connection error: {url}")
        except requests.exceptions.RequestException as e:
            raise TigerTradeAPIException(f"Request error: {e}")
    
    def get_exchanges(self, active_only: bool = True, with_stats: bool = True) -> Dict[str, Any]:
        params = {"active_only": active_only, "with_stats": with_stats}
        return self._make_request("GET", "/exchanges", params=params)
    
    def get_exchange_symbols(self, exchange_id: int, active_only: bool = True) -> Dict[str, Any]:
        params = {"active_only": active_only}
        return self._make_request("GET", f"/exchanges/{exchange_id}/symbols", params=params)
    
    def get_exchange_stats(self, exchange_id: int) -> Dict[str, Any]:
        return self._make_request("GET", f"/exchanges/{exchange_id}/stats")


def main():
    print("Tiger Trade Exchanges - /exchanges endpoint")
    print("-" * 43)
    
    try:
        api = ExchangesAPI()
        
        print("Endpoint: /exchanges")
        print(f"Active only: {EXCHANGES_PARAMS['active_only']}")
        print(f"With stats: {EXCHANGES_PARAMS['with_stats']}")
        
        result = api.get_exchanges(
            active_only=EXCHANGES_PARAMS['active_only'],
            with_stats=EXCHANGES_PARAMS['with_stats']
        )
        
        if result and isinstance(result, dict):
            if 'data' in result:
                exchanges = result['data']
                
                print(f"Found {len(exchanges)} exchanges")
                
                for exchange in exchanges[:5]:  # Show first 5
                    if isinstance(exchange, dict):
                        print(f"ID: {exchange.get('id')}, Name: {exchange.get('name', 'N/A')}, "
                              f"Status: {exchange.get('status', 'N/A')}")
            else:
                print("Raw response:")
                print(json.dumps(result, indent=2))
        
    except TigerTradeAPIException as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
