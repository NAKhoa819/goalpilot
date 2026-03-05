# Shared DTOs and Types

## `Transaction`
```json
{
  "id": "tx_123",
  "amount": 105.50,
  "category": "groceries",
  "date": "2026-03-05"
}
```

## `ReceiptOCRResult`
```json
{
  "receipt_id": "rcpt_99",
  "extracted_total": 45.00,
  "merchant": "Local Cafe",
  "confidence": 0.92
}
```

## `UserContextSummary`
```json
{
  "user_id": "usr_1",
  "current_balance": 5200.00,
  "monthly_spend_velocity": 1200.00
}
```

## `AgentEvaluateRequest`
```json
{
  "user_context": { "user_id": "usr_1", "current_balance": 5200.00, "monthly_spend_velocity": 1200.00 },
  "market_context": { "asset_class": "equities", "6mo_trend_forecast": "bullish", "volatility_index": 12.5 }
}
```

## `AgentEvaluateResponse`
```json
{
  "evaluation_id": "eval_77",
  "health_score": 85,
  "flagged_categories": []
}
```

## `AgentInterveneRequest`
```json
{
  "evaluation_id": "eval_77",
  "trigger": "overspend_detected"
}
```

## `AgentInterveneResponse`
```json
{
  "intervention_type": "soft_lock",
  "message": "We recommend reducing dining expenses for the next week."
}
```

## `MarketPrediction`
```json
{
  "asset_class": "equities",
  "6mo_trend_forecast": "bullish",
  "volatility_index": 12.5
}
```

## `RealtimeEventEnvelope`
```json
{
  "event": "soft_lock.updated",
  "timestamp": "2026-03-05T20:52:11Z",
  "data": { "user_id": "usr_123", "lock_category": "dining", "status": "locked", "reason": "Approaching monthly discretionary limit." }
}
```
