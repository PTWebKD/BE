# FitFuel+ Backend — Design Specification

**Date:** 2026-06-09  
**Status:** Approved  
**Author:** PTWebKD (via Claude Code brainstorming)

---

## 1. Overview

FitFuel+ is a multi-role gym/food/gear web platform. This spec covers the complete FastAPI backend that exposes REST APIs consumed by the React frontend at `github.com/PTWebKD/FE`.

### Roles
| Role | Description |
|------|-------------|
| `guest` | Unauthenticated; can browse gear/food, place food orders via OTP |
| `member` | Registered user; full platform access; can rent (not sell) gear |
| `vendor` | Food supplier; manages products and orders |
| `gym_owner` | Gym business; can sell AND rent gear; has admin-level access |

---

## 2. Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Framework | FastAPI | Async-native, auto OpenAPI docs, fast |
| ORM | SQLAlchemy 2.0 async | Type-safe, async session management |
| DB driver | asyncpg | Fastest async PostgreSQL driver |
| Migrations | Alembic | Standard for SQLAlchemy projects |
| Auth tokens | python-jose (JWT) | 7-day access tokens, HS256 |
| Password hashing | passlib (bcrypt) | Industry standard |
| Validation | Pydantic v2 | Schema validation + serialization |
| Server | Uvicorn | ASGI server for FastAPI |

**Python:** 3.11+  
**PostgreSQL:** 15+

---

## 3. Architecture: Feature-based Modular

Each feature module is self-contained with 4 files:

```
module/
├── model.py    # SQLAlchemy ORM models
├── schema.py   # Pydantic request/response schemas
├── router.py   # FastAPI route definitions
└── service.py  # Business logic (enforces all BRs)
```

Business rules are enforced in the **service layer**, not just DB constraints. DB constraints (CHECK, triggers) serve as a secondary safety net.

---

## 4. Folder Structure

```
BE/                              ← D:\doanWEDKD\database
├── app/
│   ├── main.py                  ← FastAPI app, CORS, router registration
│   ├── core/
│   │   ├── config.py            ← Settings from .env (pydantic-settings)
│   │   ├── database.py          ← Async engine + session factory
│   │   ├── security.py          ← JWT create/verify, bcrypt hash/verify
│   │   └── dependencies.py      ← get_db, get_current_user, role guards
│   └── modules/
│       ├── auth/                ← Login, register, OTP, refresh
│       ├── users/               ← Profile CRUD, avatar, role data
│       ├── gym/                 ← Gyms, memberships, workout sessions, exercise logs
│       ├── food/                ← Products, orders (guest + member), reviews
│       ├── gear/                ← Items, lifecycle, transactions, disputes
│       ├── gamification/        ← Challenges, badges, leaderboard, passport
│       ├── fitcoin/             ← Balance, earn/spend transactions
│       ├── social/              ← Posts, follows, feed
│       └── notifications/       ← In-app notifications
├── database/
│   ├── schema.sql               ← Full DDL (19 tables, 21 ENUMs, triggers)
│   └── seed.sql                 ← Dev seed data (6 users, 9 gear, 8 food...)
├── alembic/
│   ├── alembic.ini
│   └── versions/
├── .env.example
├── requirements.txt
└── README.md
```

---

## 5. Database Schema Summary

19 tables across 6 domains:

| Domain | Tables |
|--------|--------|
| Users | `users`, `fitness_passport`, `follows` |
| Gym | `gyms`, `gym_memberships`, `workout_sessions`, `exercise_logs` |
| Food | `food_products`, `food_orders`, `food_reviews` |
| Gear | `gear_items`, `gear_lifecycle`, `gear_transactions` |
| Gamification | `challenges`, `user_challenges`, `badges` |
| Economy | `fitcoin_transactions` |
| Social | `social_posts`, `notifications` |

Key DB-level enforcement:
- `gear_items.member_rent_only` CHECK: member lister can only have `listing_type = 'rent'` (BR-11B)
- `prevent_lifecycle_mutation` trigger: gear_lifecycle is append-only (BR-37)
- `update_fitcoin_balance` trigger: auto-syncs `users.fitcoin_balance` (BR-24)

---

## 6. API Endpoints (~55 total)

### Auth (`/api/auth`)
| Method | Path | Description | BR |
|--------|------|-------------|-----|
| POST | `/register` | Member registration | BR-40 (Checkout Modal flow) |
| POST | `/login` | Email + password → JWT | — |
| POST | `/guest/otp/request` | Guest OTP for order | BR-02 |
| POST | `/guest/otp/verify` | Verify OTP (5 min, 3 attempts) | BR-02 |
| POST | `/refresh` | Rotate JWT | — |
| POST | `/logout` | Invalidate token (client-side) | — |

### Users (`/api/users`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/me` | Current user profile |
| PUT | `/me` | Update profile |
| GET | `/{id}` | Public profile |
| GET | `/me/passport` | Fitness passport |

### Gym (`/api/gym`)
| Method | Path | Description | BR |
|--------|------|-------------|-----|
| GET | `/` | List gyms | — |
| GET | `/{id}` | Gym detail | — |
| POST | `/sessions` | Log workout session | BR-05 |
| GET | `/sessions` | My sessions | — |
| POST | `/sessions/{id}/exercises` | Log exercise | — |
| GET | `/records` | Personal records (PR flags) | — |
| GET | `/progress` | Progress chart data | — |
| GET | `/memberships` | My memberships | BR-06 |
| POST | `/memberships` | Buy membership | BR-06, BR-08 |

### Food (`/api/food`)
| Method | Path | Description | BR |
|--------|------|-------------|-----|
| GET | `/products` | List products (public) | — |
| GET | `/products/{id}` | Product detail | — |
| POST | `/products` | Create product (vendor only) | BR-15 |
| PUT | `/products/{id}` | Update product | BR-15 |
| POST | `/orders` | Place order (member or guest) | BR-18 |
| GET | `/orders` | My orders | — |
| GET | `/orders/{id}` | Order detail | — |
| PUT | `/orders/{id}/status` | Update order status (vendor) | — |
| POST | `/orders/{id}/reviews` | Post review | BR-27 |
| GET | `/products/{id}/reviews` | Product reviews | — |

### Gear (`/api/gear`)
| Method | Path | Description | BR |
|--------|------|-------------|-----|
| GET | `/` | List gear (public) | — |
| GET | `/{id}` | Gear detail | — |
| POST | `/` | List new gear item | BR-11B |
| PUT | `/{id}` | Update gear item | BR-11B |
| DELETE | `/{id}` | Remove listing | — |
| POST | `/{id}/rent` | Initiate rental | BR-13 (50% deposit) |
| POST | `/{id}/return` | Return gear | BR-33 |
| GET | `/my/listings` | My gear listings | — |
| GET | `/my/rentals` | Gear I'm renting | — |
| GET | `/{id}/lifecycle` | Lifecycle history | BR-37 (read-only) |
| POST | `/disputes` | File dispute | — |
| GET | `/disputes` | List disputes (admin) | — |
| PUT | `/disputes/{id}` | Resolve dispute (admin) | — |

### Gamification (`/api/gamification`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/challenges` | List active challenges |
| POST | `/challenges/{id}/join` | Join challenge |
| GET | `/challenges/my` | My challenges + progress |
| PUT | `/challenges/{id}/progress` | Update challenge progress |
| GET | `/leaderboard` | Global leaderboard |
| GET | `/badges` | All badge definitions |
| GET | `/badges/my` | My earned badges |

### FitCoin (`/api/fitcoin`)
| Method | Path | Description | BR |
|--------|------|-------------|-----|
| GET | `/balance` | My balance | — |
| GET | `/history` | Transaction history | — |
| POST | `/earn` | Earn FitCoins (internal) | BR-24 |
| POST | `/spend` | Spend FitCoins | BR-24 |

### Social (`/api/social`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/feed` | Followed users' posts |
| GET | `/posts` | All posts (public) |
| POST | `/posts` | Create post |
| DELETE | `/posts/{id}` | Delete own post |
| POST | `/follow/{user_id}` | Follow user |
| DELETE | `/follow/{user_id}` | Unfollow user |

### Notifications (`/api/notifications`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | My notifications |
| PUT | `/{id}/read` | Mark as read |
| PUT | `/read-all` | Mark all as read |

---

## 7. Business Rules Enforcement

| Rule | Where Enforced | Description |
|------|----------------|-------------|
| BR-02 | `auth/service.py` | OTP 5-min TTL, max 3 attempts per phone/email |
| BR-05 | `gym/service.py` | Cannot log session to gym without active membership |
| BR-06 | `gym/service.py` | Membership tiers: 1/3/12 month, no overlap |
| BR-08 | `gym/service.py` | FitCoin discount on membership payment |
| BR-11B | `gear/service.py` + DB CHECK | Member can only list gear for rent, not sell |
| BR-13 | `gear/service.py` | Rental deposit = 50% of item value |
| BR-15 | `food/service.py` | Only vendor role can create/edit food products |
| BR-18 | `food/service.py` | Guest orders require OTP verification |
| BR-24 | `fitcoin/service.py` + DB trigger | FitCoin balance updated atomically |
| BR-27 | `food/service.py` | Review only after confirmed delivery |
| BR-33 | `gear/service.py` | Return flow: gear condition check, deposit refund |
| BR-37 | `gear/service.py` + DB trigger | gear_lifecycle is append-only |
| BR-40 | `auth/service.py` | Member registration only via Checkout Modal flag |

---

## 8. Auth & Security

- **JWT**: HS256, 7-day expiry, payload: `{sub: user_id, role, email}`
- **Guest OTP**: 6-digit code, 5-minute TTL, max 3 attempts, stored in DB (`guest_otp` temp table or `users` guest row)
- **Password**: bcrypt via passlib, cost factor 12
- **Role guards**: FastAPI dependencies `require_member`, `require_vendor`, `require_gym_owner`
- **CORS origins**: `http://localhost:5173`, `https://*.vercel.app`

---

## 9. Error Response Format

All errors follow:
```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Human-readable message in Vietnamese or English",
  "detail": null
}
```

Common error codes: `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `VALIDATION_ERROR`, `BUSINESS_RULE_VIOLATION`, `OTP_EXPIRED`, `OTP_MAX_ATTEMPTS`, `INSUFFICIENT_FITCOIN`, `MEMBER_CANNOT_SELL`, `DEPOSIT_REQUIRED`

---

## 10. Success Response Format

All successful responses follow:
```json
{
  "success": true,
  "data": { ... },
  "message": null
}
```

Paginated lists include:
```json
{
  "success": true,
  "data": { "items": [...], "total": 100, "page": 1, "per_page": 20 }
}
```

---

## 11. Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/fitfuel
SECRET_KEY=<random-256-bit>
ACCESS_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256
CORS_ORIGINS=http://localhost:5173,https://fitfuel.vercel.app
```

---

## 12. Implementation Order

1. `core/` — config, database, security, dependencies
2. `auth/` — register, login, OTP
3. `users/` — profile CRUD
4. `gear/` — core marketplace feature (highest business value)
5. `food/` — orders and vendor flow
6. `gym/` — sessions, records, memberships
7. `gamification/` — challenges, badges, leaderboard
8. `fitcoin/` — transactions
9. `social/` — posts, follows
10. `notifications/` — in-app alerts
