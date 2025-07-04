#!/usr/bin/env python3

import json
import requests
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Configuration
openBetween = "2025-07-04,2025-07-04"

class TigerTradeAPIException(Exception):
    pass

class AnalyzerAPI:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Ищем config.json в родительской папке
            config_path = os.path.join(os.path.dirname(script_dir), "config.json")

        self.config_path = config_path
        self.config = self._load_config()
        # Use the correct base URL from curl requests
        self.base_url = "https://trade-web-gtw.tiger.trade"
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
    
    def _generate_request_id(self) -> str:
        import uuid
        return str(uuid.uuid4())
    
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
            
            # Test with the correct endpoint
            response = requests.get(
                f"https://x-api.tiger.trade/protected/api/v1/trading/account",
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
        request_id = self._generate_request_id()
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Origin': 'https://account.tiger.com',
            'Referer': 'https://account.tiger.com/',
            'Sec-Ch-Ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Trace-Request-Id': request_id,
            'X-Exchange-Type': 'TIGER_X',
            'X-Request-Id': request_id
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
    
    def get_trading_summary(self, **kwargs) -> Dict[str, Any]:
        params = {}
        
        params["openBetween"] = kwargs.get('open_between', openBetween)
        # Удален параметр api_key_id - получаем данные по всем ключам
            
        endpoint = "/statistics-gtw/protected/api/v1/statistics/proxy/api/v2/analyzer"
        return self._make_request("GET", endpoint, params=params)
    
    def get_today_stats(self) -> Dict[str, Any]:
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_trading_summary(open_between=f"{today},{today}")


def main():
    try:
        api = AnalyzerAPI()
        result = api.get_trading_summary()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except TigerTradeAPIException as e:
        print(json.dumps({"error": str(e)}, indent=2))
    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2))


if __name__ == "__main__":
    main()
