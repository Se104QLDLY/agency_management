# 🌐 API Reference (v1)

> **Audience**: Front‑end devs, QA, integrators. Covers all endpoints exposed by the backend, grouped by domain. For rich examples, inspect live Swagger UI at **/docs/** once the stack is running locally.

---

## 0. Conventions

| Concept                                              | Convention                                                                                     |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **Base URL**                                         | `https://<domain>/api/v1/`                                                                     |
| **Auth**                                             | JWT Access token in **HttpOnly cookie** (`access`) *or* `Authorization: Bearer <token>` header |
| **Error Envelope**                                   | `HTTP 4xx/5xx` + JSON `{ "code": "<ERR_CODE>", "message": "Human‑readable", "details": {…} }`  |
| **Pagination**                                       | DRF **LimitOffset**: `?limit=20&offset=40`                                                     |
| Response adds `count`, `next`, `previous`, `results` |                                                                                                |
| **Filtering**                                        | Simple query params (e.g. `?status=PENDING&type=2`). Text search supports `q` (ILIKE)          |
| **Ordering**                                         | `?ordering=‑created_at` (minus = DESC)                                                         |
| **Versioning**                                       | Future versions appear as `/api/v2/…`. v1 remains backward‑compatible for ≥ 12 months          |

---

## 1. Auth & User

| Method | Path                    | Scope           | Summary                               |
| ------ | ----------------------- | --------------- | ------------------------------------- |
| POST   | `auth/login/`           | public          | Login (email + password) → set tokens |
| POST   | `auth/refresh/`         | refresh         | Exchange refresh → new access token   |
| POST   | `auth/logout/`          | any             | Invalidate current refresh token      |
| GET    | `auth/me/`              | `profile:read`  | Current user profile                  |
| PUT    | `auth/change-password/` | `profile:write` | Self‑service password change          |
| GET    | `users/`                | `user:read`     | List users (admin) + filters          |
| CRUD   | `users/{id}/`           | `user:write`    | Create / retrieve / update / delete   |

**Sample: Login**

```http
POST /api/v1/auth/login/ HTTP/1.1
Content-Type: application/json

{ "email": "bob@example.com", "password": "S3cret!" }
```

Response `200 OK` sets cookies:

```json
{ "user": {"id": 42, "email": "bob@example.com"} }
```

---

## 2. Agency Management

| Method | Path                   | Scope          | Notes                                           |
| ------ | ---------------------- | -------------- | ----------------------------------------------- |
| GET    | `agency/`              | `agency:read`  | List agencies (`?status=ACTIVE&PENDING`, `?q=`) |
| POST   | `agency/`              | public         | Register new agency (status=PENDING)            |
| GET    | `agency/{id}/`         | `agency:read`  | Details                                         |
| PATCH  | `agency/{id}/`         | `agency:write` | Update base data                                |
| POST   | `agency/{id}/approve/` | `agency:write` | Approve pending agency → ACTIVE                 |
| POST   | `agency/{id}/block/`   | `agency:write` | Block / unblock                                 |
| GET    | `agency/{id}/debt/`    | `finance:read` | Current debt & aging buckets                    |
| GET    | `agency/{id}/history/` | `finance:read` | All receipts, issues, payments                  |

---

## 3. Inventory (Items, Receipts, Issues)

### 3.1 Items

| Method | Path                   | Scope             | Notes                          |
| ------ | ---------------------- | ----------------- | ------------------------------ |
| GET    | `inventory/items/`     | `inventory:read`  | List + search (`?q=bolt`)      |
| POST   | `inventory/items/`     | `inventory:write` | Create new item                |
| GET    | `inventory/items/{id}` | `inventory:read`  | Item detail                    |
| PATCH  | `inventory/items/{id}` | `inventory:write` | Update (price, name, ...)      |
| DELETE | `inventory/items/{id}` | `inventory:write` | Soft‑delete (flag `is_active`) |

### 3.2 Receipts (Stock‑In)

| Method | Path                      | Scope             | Notes                                                            |
| ------ | ------------------------- | ----------------- | ---------------------------------------------------------------- |
| GET    | `inventory/receipts/`     | `inventory:read`  | Paginated list `?agency_id=&date__gte=`                          |
| POST   | `inventory/receipts/`     | `inventory:write` | Body: `{agency_id, receipt_date, items:[{item_id, qty, price}]}` |
| GET    | `inventory/receipts/{id}` | `inventory:read`  | Includes nested `items[]`                                        |

### 3.3 Issues (Stock‑Out)

| Method | Path                    | Scope             | Notes                             |
| ------ | ----------------------- | ----------------- | --------------------------------- |
| GET    | `inventory/issues/`     | `inventory:read`  | Filters: `agency_id`, `date`      |
| POST   | `inventory/issues/`     | `inventory:write` | Same payload structure as receipt |
| GET    | `inventory/issues/{id}` | `inventory:read`  | Returns debt impact               |

---

## 4. Finance

| Method | Path                    | Scope           | Notes                                 |
| ------ | ----------------------- | --------------- | ------------------------------------- |
| GET    | `finance/payments/`     | `finance:read`  | List (`?agency_id=&date__range=`)     |
| POST   | `finance/payments/`     | `finance:write` | `{agency_id, amount, payment_method}` |
| GET    | `finance/payments/{id}` | `finance:read`  | Detail                                |
| GET    | `finance/debts/`        | `finance:read`  | All debt transactions (`?agency_id=`) |

---

## 5. Regulation & Config

| Method | Path                  | Scope          | Notes                      |
| ------ | --------------------- | -------------- | -------------------------- |
| GET    | `regulation/`         | `config:read`  | List all keys              |
| GET    | `regulation/{key}/`   | `config:read`  | Current value              |
| PUT    | `regulation/{key}/`   | `config:write` | Update JSON value          |
| GET    | `regulation/history/` | `config:read`  | `?key=` returns change log |

---

## 6. Reporting

| Method | Path                  | Scope         | Parameters / Notes                          |
| ------ | --------------------- | ------------- | ------------------------------------------- |
| GET    | `report/stock/daily/` | `report:read` | `?date=YYYY‑MM‑DD`                          |
| GET    | `report/sales/`       | `report:read` | `?from=YYYY‑MM‑DD&to=YYYY‑MM‑DD&agency_id=` |
| GET    | `report/debt‑aging/`  | `report:read` | `?agency_id=` (optional → all agencies)     |

All reports stream data from **materialized views** → expect \~20‑100 ms response on typical dataset.

---

## 7. WebSocket Notifications

`wss://<domain>/ws/notify/` – sends JSON messages:

```json
{ "type": "NEW_ISSUE", "issue_id": 123, "agency_id": 45 }
```

Clients authenticate by appending `?token=<access_jwt>` or reusing cookie.

---

## 8. Standard Error Codes

| Code                | HTTP | Meaning                                  |
| ------------------- | ---- | ---------------------------------------- |
| `DEBT_LIMIT`        | 409  | Issue would exceed configured debt limit |
| `OUT_OF_STOCK`      | 409  | Item stock insufficient                  |
| `INVALID_TOKEN`     | 401  | Access token expired or malformed        |
| `PERMISSION_DENIED` | 403  | JWT valid but missing required scope     |
| `NOT_FOUND`         | 404  | Resource id not found                    |
| `VALIDATION_ERROR`  | 400  | Request body/params failed schema checks |

---

## 9. Quick cURL Cheatsheet

```bash
# Login
curl -X POST https://api.example.com/api/v1/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"email":"demo@ex.com","password":"Passw0rd"}' \
     -c cookies.txt

# Create Stock‑Out Issue (requires cookies)
curl -X POST https://api.example.com/api/v1/inventory/issues/ \
     -H "Content-Type: application/json" \
     -d '{"agency_id":1,"items":[{"item_id":3,"qty":5}]}' \
     -b cookies.txt
```

---

> **Last updated**: 2025‑06‑21

*For any missing endpoint or parameter nuance, open a GitHub issue with label `docs`.*
