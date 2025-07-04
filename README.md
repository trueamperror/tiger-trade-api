# API Client

Internal API integration for data retrieval and analysis.

## Setup

1. Install dependencies:
```bash
pip install requests
```

2. Configure credentials:
```bash
cp config.example.json config.json
# Edit config.json with your credentials
```

3. Run scripts:
```bash
python3 statistics-api.tiger.trade/analyzer_no_key_id.py
```

## Configuration

```json
{
    "api": {
        "base_url": "https://...",
        "auth_url": "https://...",
        "timeout": 30
    },
    "auth": {
        "username": "your-username",
        "password": "your-password"
    }
}
```

## Available Scripts

- `analyzer.py` - Filtered data analysis
- `analyzer_no_key_id.py` - Aggregated analysis
- `trades.py` - Transaction history
- `dashboard.py` - Summary metrics
- `users.py` - User management
- `exchanges.py` - Exchange data
