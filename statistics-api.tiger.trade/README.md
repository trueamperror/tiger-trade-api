# Tiger Trade API Client

Internal client for trading statistics and analysis.

## Configuration

```json
{
  "auth": {
    "username": "your_email@example.com",
    "password": "your_uuid_password",
    "access_token": "auto_generated",
    "refresh_token": "auto_generated"
  },
  "api": {
    "auth_url": "https://auth-api.tiger.trade/api/v1/login",
    "refresh_url": "https://auth-api.tiger.trade/api/v1/refresh",
    "timeout": 30
  }
}
```

## Scripts

- `analyzer.py` - Account-specific analysis (with api_key_id filter)
- `analyzer_no_key_id.py` - Aggregated analysis (all accounts) ⭐
- `trades.py` - Transaction data ✅
- `analyzer-week-list.py` - Weekly statistics ✅
- `dashboard.py` - Summary dashboard ❌ 403
- `users.py` - User data ❌ 403
- `exchanges.py` - Exchange information ❌ 403

## Technical Notes

- JWT token auto-refresh
- CORS headers: Origin/Referer required
- UUID request IDs mandatory
- Endpoints requiring paid subscription marked ❌

