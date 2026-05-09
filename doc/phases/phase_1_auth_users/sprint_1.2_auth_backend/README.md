## Sprint 1.2 — Auth Backend ✅

| # | Task | File | Status |
|---|------|------|--------|
| 1 | Password hashing utils | `app/core/security.py` | ✅ |
| 2 | JWT create/verify | `app/core/security.py` | ✅ |
| 3 | `UserRepository` | `app/repositories/user.py` | ✅ |
| 4 | `AuthService` (register, login) | `app/services/auth.py` | ✅ |
| 5 | `UserService` (CRUD, approve) | `app/services/user.py` | ⬜ |
| 6 | `POST /api/v1/auth/register` | `app/api/v1/endpoints/auth.py` | ✅ |
| 7 | `POST /api/v1/auth/login` | `app/api/v1/endpoints/auth.py` | ✅ |
| 8 | `GET /api/v1/auth/me` | `app/api/v1/endpoints/auth.py` | ✅ |
| 9 | `get_current_user` dependency | `app/api/deps.py` | ✅ |