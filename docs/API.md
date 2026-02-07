# API Reference

Base URL: `http://localhost:8000/api` (development)

## Authentication

All endpoints except `/health` require a Firebase Auth token in the Authorization header:

```
Authorization: Bearer <firebase-id-token>
```

For local development, set `AUTH_DISABLED=true` to bypass authentication.

## Endpoints

### Health

#### GET /health

Check API health status.

**Response:**
```json
{
  "status": "ok",
  "version": "0.0.1"
}
```

### WebSocket

#### WS /ws

Real-time communication channel.

**Messages:**

Ping (client to server):
```json
{"type": "ping"}
```

Pong (server to client):
```json
{"type": "pong"}
```

Heartbeat (server to client, on timeout):
```json
{"type": "heartbeat"}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

Common status codes:
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## OpenAPI Documentation

Interactive documentation available at:
- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`
- OpenAPI JSON: `/api/openapi.json`
