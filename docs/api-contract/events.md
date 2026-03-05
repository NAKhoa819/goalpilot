# Realtime Events

These events form the realtime push channel. (Implement as AppSync/WebSocket)

## Event Payload: `soft_lock.updated`
Output of Strategy A (e.g., dynamic limits).

```json
{
  "event_type": "soft_lock.updated",
  "timestamp": "2026-03-05T20:52:11Z",
  "payload": {
    "user_id": "usr_123",
    "lock_category": "dining",
    "status": "locked",
    "reason": "Approaching monthly discretionary limit."
  }
}
```

## Event Payload: `goal_plan.updated`
Output of Strategy B (e.g., plan realignment).

```json
{
  "event_type": "goal_plan.updated",
  "timestamp": "2026-03-05T20:52:11Z",
  "payload": {
    "user_id": "usr_123",
    "goal_id": "goal_456",
    "new_target_date": "2027-12-01",
    "variance_reason": "Market forecast upgraded expected yield."
  }
}
```
