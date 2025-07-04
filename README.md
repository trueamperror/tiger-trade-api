# Tiger Trade API Client

Клиент для работы с API Tiger Trade - получение торговой статистики, аналитики и данных о сделках.

## 🚀 Возможности

- **Торговая аналитика** - получение детальной статистики по сделкам
- **Автоматическая авторизация** - управление JWT токенами
- **Данные о сделках** - история торговых операций
- **Dashboard метрики** - агрегированные показатели
- **Пользователи и биржи** - управление аккаунтами

## 📋 Доступные endpoints

### Аналитика (`analyzer.py`, `analyzer_no_key_id.py`)
```bash
# Получить статистику за период
python3 analyzer.py

# Получить агрегированную статистику по всем аккаунтам
python3 analyzer_no_key_id.py
```

### Сделки (`trades.py`)
```bash
# Получить историю сделок
python3 trades.py
```

### Dashboard (`dashboard.py`)
```bash
# Получить dashboard метрики
python3 dashboard.py
```

### Пользователи (`users.py`)
```bash
# Получить список пользователей
python3 users.py
```

### Биржи (`exchanges.py`)
```bash
# Получить список бирж
python3 exchanges.py
```

## ⚙️ Установка и настройка

### 1. Клонирование репозитория
```bash
git clone https://github.com/YOUR_USERNAME/tiger-trade-api.git
cd tiger-trade-api
```

### 2. Установка зависимостей
```bash
pip install requests
```

### 3. Настройка конфигурации
```bash
# Скопировать пример конфига
cp config.example.json config.json

# Отредактировать config.json и добавить ваши учетные данные
nano config.json
```

### 4. Заполнение config.json
```json
{
    "api": {
        "base_url": "https://trade-web-gtw.tiger.trade/statistics-gtw/protected/api/v1/statistics/proxy/api/v2",
        "auth_url": "https://auth-api.tiger.trade/api/v1/login",
        "refresh_url": "https://auth-api.tiger.trade/api/v1/refresh",
        "timeout": 30,
        "max_retries": 3,
        "retry_delay": 1
    },
    "auth": {
        "username": "your-email@tiger.trade",
        "password": "your-password-or-api-key",
        "access_token": "",
        "refresh_token": ""
    }
}
```

## 🔧 Использование

### Базовый пример
```python
from analyzer_no_key_id import AnalyzerAPI

# Создать клиент API
api = AnalyzerAPI()

# Получить торговую статистику за сегодня
result = api.get_today_stats()
print(result)

# Получить статистику за период
result = api.get_trading_summary(open_between="2025-07-01,2025-07-31")
print(result)
```

### Пример ответа API
```json
{
  "data": [
    {
      "net_profit": "-0.27637028",
      "count": 6,
      "win_count": 0,
      "commission": "0.25479428",
      "volume": "509.588316",
      "leverage": "4.519385361667",
      "first_trade": "2025-07-04T12:45:00.175Z"
    }
  ],
  "balanceHistory": {
    "2025-07-04 12:00:00": {
      "value": "64.49757212",
      "percent": "0"
    }
  }
}
```

## 📁 Структура проекта

```
tiger-trade-api/
├── statistics-api.tiger.trade/
│   ├── analyzer.py              # Аналитика с фильтрацией по api_key_id
│   ├── analyzer_no_key_id.py    # Агрегированная аналитика
│   ├── trades.py               # История сделок
│   ├── dashboard.py            # Dashboard метрики
│   ├── users.py                # Управление пользователями
│   ├── exchanges.py            # Список бирж
│   └── analyzer-week-list.py   # Недельная аналитика
├── config.example.json         # Пример конфигурации
├── README.md                   # Документация
└── .gitignore                  # Исключения Git
```

## ⚡ Особенности

### Автоматическая авторизация
- Все скрипты автоматически управляют токенами авторизации
- При запуске проверяется действующий токен
- При необходимости автоматически генерируется новый токен
- Токены сохраняются в `config.json` для повторного использования

### Обработка ошибок
- Автоматическая обработка истекших токенов (401)
- Обработка лимитов запросов (429)
- Информативные сообщения об ошибках

### Настраиваемость
- Все параметры запросов вынесены в начало каждого файла
- Легко изменять фильтры, лимиты, даты без редактирования основного кода
- Чистый JSON вывод без эмодзи и лишнего форматирования

## 🔍 Полный пример с нуля для analyzer_no_key_id.py

### Минимальный рабочий код
```python
#!/usr/bin/env python3

import json
import requests
import os
import uuid
from typing import Dict, Any, Optional

# Конфигурация
openBetween = "2025-06-30,2025-07-06"  # Период для анализа

class TigerTradeAPIException(Exception):
    pass

class AnalyzerAPI:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(os.path.dirname(script_dir), "config.json")

        self.config_path = config_path
        self.config = self._load_config()
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
            
            # КРИТИЧЕСКИ ВАЖНО: Используем отдельный endpoint для тестирования!
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
                
                # Обновляем refresh token из cookies
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
                
                # Сохраняем refresh token из cookies
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
        
        # КРИТИЧЕСКИ ВАЖНЫЕ ЗАГОЛОВКИ!
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Origin': 'https://account.tiger.com',      # ОБЯЗАТЕЛЬНО!
            'Referer': 'https://account.tiger.com/',    # ОБЯЗАТЕЛЬНО!
            'Sec-Ch-Ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Trace-Request-Id': request_id,             # ОБЯЗАТЕЛЬНО!
            'X-Exchange-Type': 'TIGER_X',               # ОБЯЗАТЕЛЬНО!
            'X-Request-Id': request_id                  # ОБЯЗАТЕЛЬНО!
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
            
            # Автоматическая обработка истекших токенов
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
        
        # ОСНОВНЫЕ ПАРАМЕТРЫ
        params["openBetween"] = kwargs.get('open_between', openBetween)
        # НЕ ВКЛЮЧАЕМ api_key_id для получения агрегированных данных
            
        endpoint = "/statistics-gtw/protected/api/v1/statistics/proxy/api/v2/analyzer"
        return self._make_request("GET", endpoint, params=params)


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
```

### Проверочный список для разработчиков

✅ **Обязательные файлы:**
- `config.json` с корректными учетными данными
- Python скрипт с правильной структурой классов

✅ **Обязательные зависимости:**
```bash
pip install requests
```

✅ **Обязательные заголовки в каждом запросе:**
- `Authorization: Bearer {token}`
- `Origin: https://account.tiger.com`
- `Referer: https://account.tiger.com/`
- `X-Exchange-Type: TIGER_X`
- `Trace-Request-Id: {uuid}`
- `X-Request-Id: {uuid}`

✅ **Обязательная последовательность:**
1. Загрузить config.json
2. Проверить токен через отдельный endpoint
3. Обновить токен при необходимости
4. Выполнить основной запрос
5. Обработать ошибки (401, 403, 429)

✅ **Критические детали:**
- Таймаут минимум 30 секунд
- Автоматическое сохранение токенов
- Обработка refresh токенов из cookies
- Уникальные UUID для каждого запроса

## 🔧 Детальное описание методов API

### Аутентификация и токены

#### 1. Тестирование токена
```python
def _test_token(self, token: str) -> bool:
    # ВАЖНО: Используем отдельный endpoint для проверки!
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.get(
        "https://x-api.tiger.trade/protected/api/v1/trading/account",
        headers=headers,
        timeout=10
    )
    return response.status_code == 200
```

#### 2. Получение нового токена
```python
auth_data = {"username": username, "password": password}
response = requests.post(
    "https://trade-web-gtw.tiger.trade/protected/api/v1/authentication",
    json=auth_data,
    headers={'Content-Type': 'application/json'},
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    token = result['accessToken']
    
    # Сохраняем refresh token из cookies
    for cookie in response.cookies:
        if cookie.name == 'refreshToken':
            refresh_token = cookie.value
```

#### 3. Обновление токена
```python
refresh_data = {"accessToken": current_token}
headers = {
    'Content-Type': 'application/json',
    'Cookie': f'refreshToken={refresh_token}'
}

response = requests.post(
    "https://trade-web-gtw.tiger.trade/protected/api/v1/authentication/refresh",
    json=refresh_data,
    headers=headers,
    timeout=30
)
```

### Формирование заголовков

```python
def _update_headers(self):
    request_id = str(uuid.uuid4())
    
    self.session.headers.update({
        # АВТОРИЗАЦИЯ
        'Authorization': f'Bearer {self.access_token}',
        
        # ОСНОВНЫЕ ЗАГОЛОВКИ
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        
        # КРИТИЧЕСКИ ВАЖНЫЕ CORS ЗАГОЛОВКИ
        'Origin': 'https://account.tiger.com',      # БЕЗ ЭТОГО НЕ РАБОТАЕТ!
        'Referer': 'https://account.tiger.com/',    # БЕЗ ЭТОГО НЕ РАБОТАЕТ!
        
        # БЕЗОПАСНОСТЬ
        'Sec-Ch-Ua': '"Google Chrome";v="137", "Chromium";v="137"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        
        # TIGER-СПЕЦИФИЧНЫЕ ЗАГОЛОВКИ
        'Trace-Request-Id': request_id,             # ОБЯЗАТЕЛЬНО!
        'X-Exchange-Type': 'TIGER_X',               # ОБЯЗАТЕЛЬНО!
        'X-Request-Id': request_id                  # ОБЯЗАТЕЛЬНО!
    })
```

### Параметры запросов

#### Статистика торговли (analyzer endpoint)
```python
params = {
    # ВРЕМЕННЫЕ ФИЛЬТРЫ
    "openBetween": "2025-06-30,2025-07-06",    # Период открытия позиций
    "closeBetween": "2025-01-01,2025-12-31",   # Период закрытия позиций
    
    # ФИЛЬТРЫ СЧЕТОВ
    "api_key_id": "12345",                      # Конкретный аккаунт (опционально)
    
    # ЛИМИТЫ И СОРТИРОВКА
    "limit": 100,                               # Максимум записей (по умолчанию 100)
    "offset": 0,                                # Смещение для пагинации
    "sortBy": "openTime",                       # Поле сортировки
    "sortOrder": "desc",                        # Направление сортировки
    
    # ДОПОЛНИТЕЛЬНЫЕ ФИЛЬТРЫ
    "symbol": "AAPL",                           # Конкретный инструмент
    "side": "buy",                              # Направление сделки (buy/sell)
    "status": "filled"                          # Статус сделки
}
```

#### Получение списка счетов
```python
# Endpoint для получения доступных api_key_id
GET /protected/api/v1/trading/account
```

### Обработка ошибок

```python
def _make_request(self, method: str, endpoint: str, params=None, data=None):
    response = self.session.request(method, url, params=params, json=data)
    
    # АВТОМАТИЧЕСКАЯ ПЕРЕАВТОРИЗАЦИЯ
    if response.status_code == 401:
        self._ensure_valid_token()
        self._update_headers()
        response = self.session.request(method, url, params=params, json=data)
    
    # ОБРАБОТКА СПЕЦИФИЧНЫХ ОШИБОК
    if response.status_code == 417:
        raise TigerTradeAPIException("Expectation Failed - проверьте параметры")
    elif response.status_code == 429:
        raise TigerTradeAPIException("Rate limit exceeded - слишком много запросов")
    elif response.status_code == 403:
        raise TigerTradeAPIException("Forbidden - недостаточно прав")
    elif response.status_code >= 400:
        raise TigerTradeAPIException(f"HTTP {response.status_code}: {response.text}")
```

### Структура ответа API

```json
{
  "data": {
    "trading_summary": {
      "total_pnl": 123.45,
      "total_trades": 42,
      "win_rate": 0.65,
      "balance_data": [
        {
          "date": "2025-01-01",
          "balance": 1000.00,
          "pnl": 50.00
        }
      ]
    },
    "account_info": {
      "api_key_id": "12345",
      "account_name": "Main Account"
    }
  },
  "status": "success",
  "timestamp": "2025-01-09T10:30:00Z"
}
```

## 🛠️ Готовые шаблоны для разработчиков

### Минимальный клиент
```python
import requests
import json

class SimpleTigerClient:
    def __init__(self, username, password):
        self.base_url = "https://trade-web-gtw.tiger.trade"
        self.token = self._authenticate(username, password)
        
    def _authenticate(self, username, password):
        auth_data = {"username": username, "password": password}
        response = requests.post(
            f"{self.base_url}/protected/api/v1/authentication",
            json=auth_data,
            headers={'Content-Type': 'application/json'}
        )
        return response.json()['accessToken']
    
    def get_trading_data(self, open_between):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Origin': 'https://account.tiger.com',
            'Referer': 'https://account.tiger.com/',
            'X-Exchange-Type': 'TIGER_X'
        }
        
        params = {"openBetween": open_between}
        response = requests.get(
            f"{self.base_url}/statistics-gtw/protected/api/v1/statistics/proxy/api/v2/analyzer",
            headers=headers,
            params=params
        )
        return response.json()

# Использование
client = SimpleTigerClient("username", "password")
data = client.get_trading_data("2025-01-01,2025-01-31")
print(json.dumps(data, indent=2))
```

### Расширенный клиент с обработкой ошибок
```python
import requests
import json
import time
from typing import Optional

class RobustTigerClient:
    def __init__(self, config_file: str):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.base_url = "https://trade-web-gtw.tiger.trade"
        self.session = requests.Session()
        self.token = None
        self._authenticate()
    
    def _authenticate(self):
        auth_data = {
            "username": self.config['auth']['username'],
            "password": self.config['auth']['password']
        }
        
        response = self.session.post(
            f"{self.base_url}/protected/api/v1/authentication",
            json=auth_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            self.token = response.json()['accessToken']
            self._update_headers()
        else:
            raise Exception(f"Authentication failed: {response.status_code}")
    
    def _update_headers(self):
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Origin': 'https://account.tiger.com',
            'Referer': 'https://account.tiger.com/',
            'X-Exchange-Type': 'TIGER_X'
        })
    
    def _make_request(self, endpoint: str, params: Optional[dict] = None, retries: int = 3):
        for attempt in range(retries):
            try:
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 401 and attempt < retries - 1:
                    self._authenticate()
                    continue
                elif response.status_code == 429:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                elif response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"API error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                raise Exception("Request timeout")
        
        raise Exception("Max retries exceeded")
    
    def get_analyzer_data(self, **kwargs):
        params = {}
        if 'open_between' in kwargs:
            params['openBetween'] = kwargs['open_between']
        if 'api_key_id' in kwargs:
            params['api_key_id'] = kwargs['api_key_id']
        if 'limit' in kwargs:
            params['limit'] = kwargs['limit']
            
        return self._make_request(
            "/statistics-gtw/protected/api/v1/statistics/proxy/api/v2/analyzer",
            params
        )

# Использование
client = RobustTigerClient("config.json")
data = client.get_analyzer_data(
    open_between="2025-01-01,2025-01-31",
    limit=50
)
print(json.dumps(data, indent=2, ensure_ascii=False))
```

## 📋 Чек-лист для внедрения

### Этап 1: Подготовка
- [ ] Создать `config.json` с учетными данными
- [ ] Установить библиотеку `requests`
- [ ] Протестировать подключение к интернету
- [ ] Проверить доступность домена `trade-web-gtw.tiger.trade`

### Этап 2: Базовая интеграция
- [ ] Реализовать класс аутентификации
- [ ] Добавить обязательные заголовки (Origin, Referer, X-Exchange-Type)
- [ ] Протестировать получение токена
- [ ] Протестировать базовый запрос

### Этап 3: Обработка ошибок
- [ ] Добавить обработку 401 (переавторизация)
- [ ] Добавить обработку 429 (rate limiting)
- [ ] Добавить обработку таймаутов
- [ ] Добавить логирование ошибок

### Этап 4: Продакшн
- [ ] Настроить сохранение/загрузку токенов
- [ ] Добавить валидацию параметров
- [ ] Настроить мониторинг
- [ ] Добавить юнит-тесты

### Типичные ошибки при интеграции

❌ **Отсутствуют CORS заголовки**
```
Error 403/417: Missing Origin or Referer headers
```
Решение: Всегда включать `Origin` и `Referer`

❌ **Неправильный endpoint для тестирования токена**
```
Error 404: /statistics-gtw/... returns 404 for token test
```
Решение: Использовать `/protected/api/v1/trading/account` для проверки токена

❌ **Игнорирование refresh токенов**
```
Auth fails after token expiry
```
Решение: Сохранять refresh токены из cookies

❌ **Отсутствие уникальных ID запросов**
```
Error 417: Duplicate request IDs
```
Решение: Генерировать UUID для каждого запроса

## 🤝 Контрибьютинг

1. Fork проект
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Контакты

Project Link: [https://github.com/YOUR_USERNAME/tiger-trade-api](https://github.com/YOUR_USERNAME/tiger-trade-api)
