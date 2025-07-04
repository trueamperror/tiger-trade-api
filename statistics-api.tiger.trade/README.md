# Tiger Trade API Scripts

Набор автономных Python скриптов для работы с Tiger Trade API со встроенной авторизацией.

## 📖 Документация API
Полная документация API доступна по адресу: https://statistics-api.tiger.trade/api/v2/swagger/index.html#/

## 🔧 Настройка

### Требования
- Python 3.7+
- requests

### Установка зависимостей
```bash
pip install requests
```

### Конфигурация
Все скрипты используют файл `config.json` для хранения настроек авторизации и API endpoints.

Пример `config.json`:
```json
{
  "auth": {
    "username": "your_email@example.com",
    "password": "your_uuid_password",
    "access_token": "will_be_auto_generated",
    "refresh_token": "will_be_auto_generated"
  },
  "api": {
    "base_url": "https://trade-web-gtw.tiger.trade/statistics-gtw/protected/api/v1/statistics/proxy/api/v2",
    "auth_url": "https://auth-api.tiger.trade/api/v1/login",
    "refresh_url": "https://auth-api.tiger.trade/api/v1/refresh",
    "timeout": 30
  }
}
```

## 🔐 Подробное руководство по авторизации

### Процесс авторизации
Tiger Trade API использует JWT токены для авторизации. Процесс состоит из нескольких этапов:

1. **Первичная авторизация**: POST запрос на `/api/v1/login` с email и password
2. **Получение токенов**: API возвращает `accessToken` в JSON и `refreshToken` в cookie
3. **Использование токенов**: Все запросы требуют заголовок `Authorization: Bearer {accessToken}`
4. **Обновление токенов**: При истечении accessToken используется refreshToken для получения нового

### Заголовки запросов
Все запросы к API должны содержать следующие заголовки:

```python
headers = {
    'Authorization': f'Bearer {access_token}',
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
    'Trace-Request-Id': '{uuid}',  # Уникальный UUID для каждого запроса
    'X-Exchange-Type': 'TIGER_X',
    'X-Request-Id': '{uuid}'       # Тот же UUID что и в Trace-Request-Id
}
```

### Обработка ошибок авторизации
- **401 Unauthorized**: Токен истек, нужно обновить через refresh endpoint
- **403 Forbidden**: Недостаточно прав доступа (требуется платная подписка)
- **429 Too Many Requests**: Превышен лимит запросов, нужна пауза

## 📊 Доступные скрипты

### 1. analyzer.py - Торговая аналитика (с фильтрацией по API ключу)
Получение торговой аналитики с фильтрацией по конкретному торговому счету.

**Настройки в начале файла:**
```python
# Configuration
api_key_id = [106115]  # ID конкретного API ключа для фильтрации
openBetween = "2025-06-30,2025-07-06"  # Период в формате YYYY-MM-DD,YYYY-MM-DD
```

**Запуск:**
```bash
python analyzer.py
```

**Endpoint:** `GET /statistics-gtw/protected/api/v1/statistics/proxy/api/v2/analyzer`

**Параметры запроса:**
- `openBetween`: Период для анализа (формат: "YYYY-MM-DD,YYYY-MM-DD")
- `api_key_id`: Массив ID API ключей для фильтрации данных

**Что возвращает:**
- Статистику торгов за указанный период для конкретного торгового счета
- История баланса по часам
- Агрегированные данные по сделкам (прибыль, количество, комиссии и т.д.)

### 2. analyzer_no_key_id.py - Торговая аналитика (все счета) ⭐ РЕКОМЕНДУЕТСЯ
Получение агрегированной торговой аналитики по всем торговым счетам без фильтрации.

**Настройки в начале файла:**
```python
# Configuration
openBetween = "2025-06-30,2025-07-06"  # Период в формате YYYY-MM-DD,YYYY-MM-DD
# api_key_id параметр ОТСУТСТВУЕТ - получаем данные по всем счетам
```

**Запуск:**
```bash
python analyzer_no_key_id.py
```

**Endpoint:** `GET /statistics-gtw/protected/api/v1/statistics/proxy/api/v2/analyzer`

**Параметры запроса:**
- `openBetween`: Период для анализа (формат: "YYYY-MM-DD,YYYY-MM-DD")
- `api_key_id`: ОТСУТСТВУЕТ (получаем агрегированные данные)

**Особенности:**
- **Больше данных**: Показывает агрегированную статистику по всем торговым счетам
- **Полная картина**: История баланса включает все операции на всех счетах
- **api_key_id: 0**: В ответе указывается как агрегированные данные

**Что возвращает:**
- Полную торговую статистику за период по всем счетам
- Детальную историю баланса (больше колебаний и данных)
- Суммарные показатели по всем торговым операциям

### 🔍 Подробный разбор analyzer_no_key_id.py

#### Структура запроса
```python
# URL для запроса
base_url = "https://trade-web-gtw.tiger.trade"
endpoint = "/statistics-gtw/protected/api/v1/statistics/proxy/api/v2/analyzer"
full_url = f"{base_url}{endpoint}"

# Параметры запроса
params = {
    "openBetween": "2025-06-30,2025-07-06"
### 3. trades.py - Управление сделками ✅ ПОЛНОСТЬЮ РАБОТАЕТ
Получение списка сделок и категорий.

**Настройки в начале файла:**
```python
TRADES_PARAMS = {
    "page": 1,               # Номер страницы (начинается с 1)
    "items_per_page": 20,    # Количество элементов на странице (1-100)
    "sort_by": "id",         # Поле для сортировки
    "sort_order": "desc",    # Порядок сортировки: "asc" или "desc"
    
    # Фильтры (используйте None если не нужны)
    "symbol": None,          # Символ торговой пары, например "BTCUSDT"
    "side": None,            # Сторона сделки: "buy" или "sell"
    "status": None,          # Статус сделки
    "date_from": None,       # Дата начала в формате YYYY-MM-DD
    "date_to": None,         # Дата окончания в формате YYYY-MM-DD
}
```

**Запуск:**
```bash
python trades.py
```

**Endpoint:** `GET /trades/`

**Что возвращает:**
- ✅ Полный список сделок с детальной информацией
- ✅ Список категорий сделок

## 🛠️ Архитектура и техническая реализация

### Базовый класс TigerTradeAPIException
```python
class TigerTradeAPIException(Exception):
    """Кастомное исключение для API ошибок"""
    pass
```

### Архитектура класса AnalyzerAPI
```python
class AnalyzerAPI:
    def __init__(self, config_path: Optional[str] = None):
        # Инициализация с автоматической загрузкой конфигурации
        
    def _load_config(self) -> Dict[str, Any]:
        # Загрузка и валидация config.json
        
    def _generate_request_id(self) -> str:
        # Генерация уникального UUID для каждого запроса
        
    def _test_token(self, token: str) -> bool:
        # Проверка валидности токена через тестовый запрос
        
    def _refresh_token(self) -> str:
        # Обновление токена через refresh endpoint
        
    def _generate_new_token(self) -> str:
        # Получение нового токена через логин
        
    def _ensure_valid_token(self):
        # Проверка и обновление токена при необходимости
        
    def _update_headers(self):
        # Обновление заголовков сессии с новым токеном
        
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        # Универсальный метод для выполнения запросов
        
    def get_trading_summary(self, **kwargs) -> Dict[str, Any]:
        # Основной метод для получения торговой аналитики
```

### Автоматическое управление токенами
```python
def _ensure_valid_token(self):
    existing_token = self.config['auth'].get('access_token')
    
    # Проверяем существующий токен
    if existing_token and self._test_token(existing_token):
        self.access_token = existing_token
        return
    
    # Если токен не валиден, обновляем
    self.access_token = self._refresh_token()
```

### Обработка ошибок и повторных попыток
```python
def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                 data: Optional[Dict] = None) -> Dict[str, Any]:
    url = f"{self.base_url}{endpoint}"
    
    try:
        response = self.session.request(method=method, url=url, params=params, 
                                      json=data, timeout=self.timeout)
        
        # Автоматическая обработка истекших токенов
        if response.status_code == 401:
            self._ensure_valid_token()
            self._update_headers()
            # Повторный запрос с новым токеном
            response = self.session.request(method=method, url=url, params=params, 
                                          json=data, timeout=self.timeout)
        
        # Обработка специфических ошибок
        if response.status_code == 417:
            raise TigerTradeAPIException(f"Expectation Failed (417): {endpoint}")
        elif response.status_code == 429:
            raise TigerTradeAPIException("Rate limit exceeded (429)")
        elif response.status_code >= 400:
            raise TigerTradeAPIException(f"HTTP {response.status_code}: {response.text}")
        
        return response.json()
        
    except requests.exceptions.Timeout:
        raise TigerTradeAPIException(f"Timeout: {url}")
    except requests.exceptions.ConnectionError:
        raise TigerTradeAPIException(f"Connection error: {url}")
    except requests.exceptions.RequestException as e:
        raise TigerTradeAPIException(f"Request error: {e}")
```

### Критически важные детали для разработчиков

#### 1. Тестирование токена
```python
def _test_token(self, token: str) -> bool:
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # ВАЖНО: Используем ДРУГОЙ endpoint для тестирования
        response = requests.get(
            f"https://x-api.tiger.trade/protected/api/v1/trading/account",
            headers=headers,
            timeout=10
        )
        return response.status_code == 200
    except Exception:
        return False
```

#### 2. Структура config.json (обязательная)
```json
{
  "auth": {
    "username": "user@email.com",
    "password": "uuid-password",
    "access_token": "",
    "refresh_token": ""
  },
  "api": {
    "auth_url": "https://auth-api.tiger.trade/api/v1/login",
    "refresh_url": "https://auth-api.tiger.trade/api/v1/refresh", 
    "timeout": 30
  }
}
```

#### 3. Обязательная последовательность запросов
1. Загрузить config.json
2. Проверить существующий access_token
3. Если токен не валиден - обновить через refresh_token
4. Если refresh не работает - получить новый через логин
5. Сохранить новые токены в config.json
6. Выполнить основной запрос

#### 4. Обязательные заголовки для каждого запроса
```python
# КРИТИЧЕСКИ ВАЖНО: Эти заголовки обязательны!
headers = {
    'Authorization': f'Bearer {access_token}',  # JWT токен
    'Origin': 'https://account.tiger.com',      # Обязательно для CORS
    'Referer': 'https://account.tiger.com/',    # Обязательно для CORS
    'X-Exchange-Type': 'TIGER_X',               # Обязательно для API
    'Trace-Request-Id': str(uuid.uuid4()),      # Уникальный ID
    'X-Request-Id': str(uuid.uuid4())           # Уникальный ID
}
```
    print(f"Error: {response.status_code} - {response.text}")
```

#### Структура ответа
```json
{
  "balanceGain": "0",
  "balanceHistory": {
    "2025-07-04 12:00:00": {
      "value": "64.49757212",      // Основное значение баланса
      "value2": "63.12249113",     // Альтернативное значение
      "value3": "64.79943045",     // Третье значение
      "percent": "0",              // Процентное изменение
      "dateValue": "2025-07-04 12:00:00"  // Временная метка
    }
  },
  "data": [
    {
      "net_profit": "-0.27637028",         // Чистая прибыль
      "count": 6,                          // Количество сделок
      "win_count": 0,                      // Количество прибыльных сделок
      "avg_win": "0",                      // Средняя прибыль
      "avg_loss": "0.046061713333",        // Средний убыток
      "total_loss": "-0.27637028",         // Общий убыток
      "total_win": "0",                    // Общая прибыль
      "long_count": 5,                     // Количество длинных позиций
      "commission": "0.25479428",          // Общие комиссии
      "volume": "509.588316",              // Объем торгов
      "leverage": "4.519385361667",        // Средний леверидж
      "api_key_id": 0,                     // 0 = агрегированные данные
      "percent": "-0.051",                 // Процент от депозита
      "first_trade": "2025-07-04T12:45:00.175Z"  // Первая сделка
    }
  ]
}
```

#### Критические моменты для разработчиков

1. **Авторизация**: Без валидного JWT токена запрос вернет 401
2. **User-Agent**: Обязателен, иначе возможен блок как бот
3. **CORS заголовки**: Обязательны для cross-origin запросов
4. **UUID в заголовках**: Trace-Request-Id и X-Request-Id должны быть уникальными
5. **Таймаут**: Запросы могут быть медленными, устанавливайте таймаут 30+ секунд
6. **Обработка ошибок**: 401 = обновить токен, 403 = нет прав, 429 = лимит запросов

#### Тестирование параметров
```python
# Без api_key_id - агрегированные данные (БОЛЬШЕ данных)
params = {"openBetween": "2025-06-30,2025-07-06"}

# С api_key_id - данные конкретного счета (МЕНЬШЕ данных)
params = {
    "openBetween": "2025-06-30,2025-07-06",
    "api_key_id": [106115]
}
```

### 3. trades.py - Управление сделками ✅ ПОЛНОСТЬЮ РАБОТАЕТ
Получение списка сделок и категорий.

**Настройки в начале файла:**
```python
TRADES_PARAMS = {
    "page": 1,               # Номер страницы (начинается с 1)
    "items_per_page": 20,    # Количество элементов на странице (1-100)
    "sort_by": "id",         # Поле для сортировки
    "sort_order": "desc",    # Порядок сортировки: "asc" или "desc"
    
    # Фильтры (используйте None если не нужны)
    "symbol": None,          # Символ торговой пары, например "BTCUSDT"
    "side": None,            # Сторона сделки: "buy" или "sell"
    "status": None,          # Статус сделки
    "date_from": None,       # Дата начала в формате YYYY-MM-DD
    "date_to": None,         # Дата окончания в формате YYYY-MM-DD
}
```

**Запуск:**
```bash
python trades.py
```

**Что возвращает:**
- ✅ Полный список сделок с детальной информацией
- ✅ Список категорий сделок

### 3. users.py - Работа с пользователями ❌ НЕ РАБОТАЕТ
Получение информации о пользователях и топ трейдерах.

**Статус:** ❌ Все endpoints возвращают 403 Forbidden

**Настройки в начале файла:**
```python
USERS_PARAMS = {
    "page": 1,               # Номер страницы
    "items_per_page": 20,    # Количество элементов на странице
    "search": None,          # Поиск по имени/email (или None)
    "status": None,          # Фильтр по статусу: "active", "inactive" (или None)
    "role": None,            # Фильтр по роли (или None)
}
```

**Запуск:**
```bash
python users.py
```

### 4. exchanges.py - Работа с биржами ❌ НЕ РАБОТАЕТ
Получение информации о биржах и торговых парах.

**Статус:** ❌ Все endpoints возвращают 403 Forbidden

**Настройки в начале файла:**
```python
EXCHANGES_PARAMS = {
    "active_only": True,     # Только активные биржи
    "with_stats": True,      # Включить статистику
}
```

**Запуск:**
```bash
python exchanges.py
```

### 5. dashboard.py - Дашборд и уведомления ❌ НЕ РАБОТАЕТ
Получение статистики дашборда и уведомлений.

**Статус:** ❌ Все endpoints возвращают 403 Forbidden

**Настройки в начале файла:**
```python
DASHBOARD_PARAMS = {
    "period": "month",       # Период: "day", "week", "month", "year"
    "timezone": "UTC",       # Временная зона
    "include_charts": True,  # Включить данные для графиков
}
```

**Запуск:**
```bash
python dashboard.py
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
            config_path = os.path.join(script_dir, "config.json")

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

## 🔒 Безопасность
- Никогда не делитесь файлом `config.json` - он содержит ваши учетные данные
- Добавьте `config.json` в `.gitignore` если используете git

## 📋 Реальный статус endpoint'ов (проверено 04.07.2025)

### ✅ Работающие endpoints:
- `/analyzer/week-list` - Список торговых недель с полной статистикой
- `/trades` - Полный список сделок с детальной информацией  
- `/trades/categories` - Список категорий сделок

### ❌ Endpoints с ошибкой 403 Forbidden:
- `/analyzer/` с параметрами (статистика за день/период)
- `/users/top-traders/{league}` - топ трейдеры
- `/users/public-profile` - публичный профиль
- `/exchanges/` - список бирж
- `/exchanges/{id}` - информация о бирже
- `/dashboard/*` - все endpoints дашборда

**Вывод:** Большинство endpoints требуют специальные права доступа или платную подписку.

## 🆘 Поддержка
При возникновении проблем:
1. Убедитесь, что `config.json` содержит корректные учетные данные
2. Проверьте подключение к интернету
3. Ознакомьтесь с официальной документацией API

## 📄 Лицензия
Эти скрипты предназначены для личного использования с Tiger Trade API.
