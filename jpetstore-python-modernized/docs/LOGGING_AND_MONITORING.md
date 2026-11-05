# Logging and Monitoring



## Environment



See `.env.example`: `LOG_LEVEL`, `LOG_DIR`, `LOG_RETENTION_DAYS`, `LOG_ROTATION`, `LOG_JSON`, JWT and rate-limit variables.



On Windows, use a relative or absolute path for `LOG_DIR` (default `./logs`). The directory is created on startup.



## Log files



| File | Content |

|------|---------|

| `application.log` | General application logs (INFO+) |

| `error.log` | Errors (ERROR+) |

| `security-audit.log` | `jpetstore.security` logger only |



Rotation: daily at UTC midnight, 30 backups, gzip compressed.



## Security audit format (Phase 3)



JSON lines when `LOG_JSON=true`. Typical fields:



```json

{

  "timestamp": "2026-11-04T18:00:00+00:00",

  "level": "INFO",

  "logger": "jpetstore.security",

  "message": "security audit",

  "request_id": "uuid",

  "event": "auth.login",

  "outcome": "success",

  "user_identifier": "j2ee",

  "method": "POST",

  "route": "/api/v1/auth/login"

}

```



Failure events may include `failure_category` (e.g. `invalid_credentials`, `invalid_token`, `login` for rate limit).



Sensitive values are redacted by `RedactingFilter` on other loggers; audit payloads are constructed without secrets.



## Prometheus



The application always exposes metrics at **`http://127.0.0.1:8000/metrics`** when running locally. Prometheus itself is **optional** and does not block startup.



Local scrape config: `monitoring/prometheus.yml` (target `127.0.0.1:8000`).



Install Prometheus separately (see `docs/DEPLOYMENT_GUIDE.md` or `README.md`), then:



```powershell

prometheus --config.file=monitoring/prometheus.yml

```



| Metric | Labels | Phase |

|--------|--------|-------|

| `http_requests_total` | method, normalized_route, status_code | 1 |

| `auth_login_attempts_total` | outcome (`success` \| `failure`) | 3 |

| `auth_registration_total` | outcome (`success` \| `failure`) | 3 |

| `cart_add_total` | outcome | 5 |

| `cart_update_total` | outcome | 5 |

| `cart_remove_total` | outcome | 5 |



No usernames or tokens in metric labels.

