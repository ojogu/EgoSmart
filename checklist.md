# Agent Descriptions

## 1. Data Ingestion Agent
```python
description=(
    "Handles all transaction data collection and normalization: "
    "fetching transactions from Open Banking APIs, processing manual "
    "transaction entries, handling receipt uploads with OCR extraction, "
    "validating data integrity, and storing standardized transaction records."
)
```

## 2. Transaction Categorization Agent
```python
description=(
    "Manages transaction classification and learning: "
    "automatically categorizing transactions using rule-based and ML models, "
    "processing user category corrections, learning from feedback patterns, "
    "and re-categorizing transactions when rules are updated."
)
```

## 3. Budget Tracking Agent
```python
description=(
    "Monitors budget compliance and spending limits: "
    "setting and updating budget limits per category, tracking real-time "
    "spending against budgets, detecting when thresholds are approached or "
    "exceeded, and sending timely alerts and notifications to users."
)
```

## 4. Financial Summary Agent
```python
description=(
    "Generates comprehensive financial overviews and insights: "
    "calculating spending by category and time period, showing budget "
    "remaining balances, comparing income versus expenses, and creating "
    "clear visualizations of financial status and trends."
)
```

---

## Post-MVP Agents (For Reference)

### 5. Recommendations Agent
```python
description=(
    "Provides personalized financial guidance and optimization: "
    "analyzing spending patterns to identify savings opportunities, "
    "suggesting budget adjustments based on behavior, recommending "
    "actionable steps to improve financial health, and adapting advice "
    "to user goals and preferences."
)
```

### 6. Financial Analysis Agent
```python
description=(
    "Performs advanced analytical operations on financial data: "
    "identifying spending trends and patterns, detecting anomalies and "
    "unusual transactions, comparing period-over-period changes, forecasting "
    "future expenses, and calculating savings potential across categories."
)
```

### 7. Reporting Agent
```python
description=(
    "Creates formatted financial reports and exports: "
    "generating monthly/quarterly/annual summaries, producing visualizations "
    "and charts, exporting data in multiple formats (PDF, CSV, Excel), and "
    "scheduling automated report delivery."
)
```

### 8. Savings Goals Agent
```python
description=(
    "Manages financial goals and progress tracking: "
    "creating and updating savings goals, tracking progress toward targets, "
    "calculating required monthly savings rates, suggesting budget adjustments "
    "to meet goals, and celebrating milestones with users."
)
```




# Roadmap & Sprint Plan

## 1. Prioritize and Freeze MVP Scope

### Must-Have Features (MVP)
1. **User Onboarding & Authentication**
  - Link phone number to user profile
  - Basic session management via Redis

2. **Transaction Ingestion**
  - **Mono Sync (Background)**
    - Scheduled sync of new transactions into PostgreSQL
  - **Log Expense via WhatsApp**
    - NLP to extract amount, category, description
    - API endpoint to receive and store parsed transaction

3. **Budget Engine**
  - CRUD budgets (FastAPI endpoints)
  - Real-time threshold checks on new transactions
  - Store aggregates in `budget_spend_aggregate`

4. **Analytics & Reporting (Basic)**
  - Daily “total expenses” summary (scheduled)
  - On-demand “total spend by category” via WhatsApp query
  - FastAPI endpoints for ad-hoc report queries

5. **Notification Service**
  - Central module to send WhatsApp messages via Twilio
  - Unified templating for alerts and confirmations

### Nice-to-Have (Post-MVP)
1. **Exports (Sheets, CSV, PDF)**
2. **Financial Advice Engine**
3. **Payment/Transfer Agent**
4. **Fraud & Risk Monitoring**
5. **Personalization & Recommendation Engine**
6. **Customer Support (Ticketing) Engine**
7. **Admin Dashboard**

> **MVP Scope Locked:**  
> We will build **only** the “Must-Have” items above. Everything else is deferred until the MVP is stable and tested.

---

## 2. MVP Technical Tasks (Sprint Breakdown)

### Sprint 1: Foundation & Onboarding

#### Feature: Project Setup & Core Infrastructure
- [ ] Initialize Git repository, README, and project structure
- [ ] Configure Python virtual environment
- [ ] Install core dependencies:
  - FastAPI
  - SQLAlchemy (or psycopg2)
  - redis-py
  - Celery
  - Twilio SDK
  - Pydantic
- [ ] Set up PostgreSQL schema (users, transactions, budgets, budget_spend_aggregate, export_history)
- [ ] Configure Redis for sessions and caching
- [ ] Configure Celery (with Redis broker) and Celery Beat for scheduled tasks
- [ ] Define environment variables for database URLs, Twilio credentials, Mono credentials

#### Feature: User Onboarding & Authentication
- [ ] FastAPI endpoint: `POST /users/register`
  - Input: `{ "phone_number": "+23480xxxxxxx", "full_name": "Alice" }`
  - Create user record in `users` table
- [ ] FastAPI endpoint: `POST /users/verify-otp`
  - Input: `{ "phone_number": "...", "otp": "123456" }`
  - Validate OTP (use Redis to store OTP), mark `users.is_verified = TRUE`
- [ ] Redis Session Management
  - Create key `session:{phone_number}` for multi-turn flows
  - Expire after 5 minutes
- [ ] Twilio “OTP” Messenger
  - On `register`, generate 6-digit OTP, store in Redis, send via WhatsApp

---

### Sprint 2: Transaction Ingestion

#### Feature: Mono Sync (Background)
- [ ] Celery Task: `sync_all_users()`
  - Query `users` with `mono_account_id IS NOT NULL`
  - For each user, enqueue `sync_single_account(user_id)`
- [ ] Celery Task: `sync_single_account(user_id)`
  - Fetch `last_synced_at` from `accounts` table
  - Call Mono API `GET /v1/transactions?from=...&to=...`
  - Upsert each transaction into `transactions` table (fields: `mono_transaction_id`, `user_id`, `date`, `amount`, `description`, `category`, `type`, `source="mono_api"`, `confidence=1.0`)
  - Update `accounts.last_synced_at`

- [ ] SQL: Create `accounts` table (mono_account_id, mono_access_token, last_synced_at)
- [ ] FastAPI endpoint: `POST /accounts/link-mono`
  - Input: `{ "user_id": 1234, "mono_public_token": "abc" }`
  - Exchange for `access_token`, store `mono_account_id` & `access_token`, set `last_synced_at = NULL`
- [ ] Schedule Celery Beat → `sync_all_users()` every 10 minutes

#### Feature: Log Expense via WhatsApp
- [ ] NLP Integration (LLM prompt template)
  - Extract `amount`, `category`, `description` from free text
  - Example: “I spent ₦2,500 on groceries at Shoprite”
- [ ] FastAPI endpoint: `POST /log-expense`
  - Input: `{ "user_id": 1234, "text": "I spent ₦2,500 on groceries at Shoprite" }`
  - Call NLP to parse into `{ "amount": 2500, "category": "groceries", "description": "Shoprite" }`
  - Insert into `transactions` table:
   - `date = today (Africa/Lagos)`
   - `type = "expense"`, `currency="NGN"`, `source="user_text"`, `confidence=0.9`
  - Return `{ "status": "success", "transaction_id": 5678 }`
- [ ] Redis Session for Clarification
  - If NLP confidence < 0.6, store partial parse in `session:{user_id}`
  - Prompt user: “I’m not sure of the amount—please reply with an amount in ₦”

- [ ] Confirm Receipt on WhatsApp
  - On success: send “Logged ₦2,500 as groceries expense. Thank you!”  

---

### Sprint 3: Budget Engine

#### Feature: Budget CRUD
- [ ] FastAPI endpoint: `POST /budgets`
  - Input: `{ "user_id": 1234, "category": "groceries", "limit_amount": 50000, "period_type": "monthly", "start_date": "2025-06-01" }`
  - Insert into `budgets` table
  - Compute current period_start/period_end; insert row into `budget_spend_aggregate` `(user_id, budget_id, period_start, period_end, total_spent=0)`
  - Return `{ "status":"created", "budget_id": 42 }`
- [ ] FastAPI endpoint: `GET /budgets/{budget_id}`
  - Return budget details
- [ ] FastAPI endpoint: `PUT /budgets/{budget_id}`
  - Update limit_amount, period_type, start_date, or description
  - On update, recalc `budget_spend_aggregate` if period changed
- [ ] FastAPI endpoint: `DELETE /budgets/{budget_id}`
  - Soft-delete (set `active = FALSE`) or remove row; remove from `budget_spend_aggregate`

#### Feature: Threshold Monitor & Alert
- [ ] SQL: Create `budget_alert_history` table
- [ ] On insert into `transactions` (Mono sync or user_text), trigger:
  - Query budgets where `user_id` matches and `transaction.category` matches, and transaction.date ∈ period
  - Fetch or lock `budget_spend_aggregate` row; `UPDATE total_spent += amount`
  - For each threshold `[50%, 80%, 100%, 120%]`:
   - If `(prev_spent < threshold_value) AND (new_spent ≥ threshold_value)`
   - Check `budget_alert_history`; if not exists, insert and send WhatsApp alert via Notification Service
- [ ] FastAPI endpoint: `GET /budgets/{budget_id}/status`
  - Return `{ "spent": 31000, "limit": 50000, "remaining": 19000, "percent_used": 62% }`

---

### Sprint 4: Analytics & Reporting (Basic)

#### Feature: Daily Summary (Scheduled)
- [ ] Celery Task: `generate_daily_summary(user_id)`
  - Compute `total_expenses` WHERE `date = today`
  - Compute `total_income` WHERE `date = today`
  - Optionally, top 3 categories:  
   ```sql
   SELECT category, SUM(amount) AS spent
    FROM transactions
    WHERE type='expense' AND date = today AND user_id = :user_id
    GROUP BY category
    ORDER BY spent DESC
    LIMIT 3;
   ```
  - Format text summary
  - Log into `report_history` `(report_type='daily', period_start=today, period_end=today, summary_text, delivery_channel='whatsapp', status='pending')`
  - Send WhatsApp via Notification Service; update `status='sent'`

- [ ] Schedule Celery Beat → `generate_daily_summary` for each `user_id` at 23:59 Africa/Lagos

#### Feature: On-Demand Category Spend Query
- [ ] FastAPI endpoint: `POST /reports/category-spend`
  - Input: `{ "user_id": 1234, "category": "airtime", "start_date": "2025-06-01", "end_date": "2025-06-10" }`
  - Execute:
   ```sql
   SELECT SUM(amount) AS total_spend
    FROM transactions
    WHERE user_id=1234 AND category='airtime'
      AND type='expense'
      AND date BETWEEN '2025-06-01' AND '2025-06-10';
   ```
  - Return `{ "category": "airtime", "total_spend": 14700 }`
- [ ] FastAPI to format and send
  - “You spent ₦14,700 on airtime from 2025-06-01 to 2025-06-10.”

#### Feature: Ad-Hoc Report (Total Spend by Category)
- [ ] FastAPI endpoint: `POST /reports/spend-by-category`
  - Input: `{ "user_id": 1234, "start_date": "2025-06-01", "end_date": "2025-06-30" }`
  - Execute:
   ```sql
   SELECT category, SUM(amount) AS spent
    FROM transactions
    WHERE user_id=1234 AND type='expense'
      AND date BETWEEN :start_date AND :end_date
    GROUP BY category
    ORDER BY spent DESC;
   ```
  - Return list of `{ "category": "...", "spent": ... }`
- [ ] Format text:
  - “You spent the most on rent, followed by groceries and transport.”
   Spend by category (Jun 2025):
   - Rent: ₦100,000
   - Groceries: ₦70,000
   - Transport: ₦25,000
   - Dining: ₦20,000
---



### Sprint 5: Exports & Notification Service

#### Feature: Notification Service Core
- [ ] Implement `notify_user(user_id, channel, message, metadata={})` helper
- Lookup user’s phone number, send via Twilio SDK
- Log into `notification_logs` table (optional)
- [ ] Template store in `templates/whatsapp/` for common messages

#### Feature: Export Engine (Minimal CSV)
- [ ] SQL: Create `export_history` table
- [ ] FastAPI endpoint: `POST /export`
- Input: `{ "user_id": 1234, "format": "CSV", "filters": { "category":"groceries", "start_date":"2025-06-01", "end_date":"2025-06-30" } }`
- Insert into `export_history` `(status='pending')`
- Enqueue Celery Task `generate_export(export_id)`
- Return `{ "status": "pending", "export_id": 789 }`
- Send WhatsApp “Your CSV is being generated…”
- [ ] Celery Task: `generate_export(export_id)`
- Fetch `export_history` row
- Build SQL query with filters
- Load result into pandas DataFrame
- `csv_bytes = df.to_csv(index=False).encode('utf-8')`
- Upload to S3 under `exports/{user_id}/{export_id}.csv`
- Generate presigned URL (24‐hr expiry)
- Update `export_history` `(status='ready', file_url=presigned_url)`
- Send WhatsApp “Your CSV is ready: {file_url}”

---

#### Feature: PDF & Google Sheet Stubs (Post-MVP)
- [ ] Placeholder tasks—defer until core CSV works:
- Integrate Google Sheets API client
- Integrate PDF renderer (WeasyPrint)

---

### Sprint 6: Financial Advice & Threshold Alerts

#### Feature: Financial Advice Engine (Basic)
- [ ] SQL: Create `benchmarks` table with default values (savings_rate=10%, housing_ratio=30%, etc.)
- [ ] FastAPI endpoint: `POST /advice`
- Input: `{ "user_id": 1234, "period": "2025-06" }`
- Inside:
  - Query transactions (same as monthly report)
  - Compute KPIs (savings_rate, housing_ratio, groceries_ratio, transport_ratio)
  - Compare against benchmarks, collect flags
  - Populate advice templates (hardcoded YAML/JSON)
  - Return `{ "advice_text": "..." }`
- Send WhatsApp “Your June advice: …”
- [ ] Celery Task: `generate_monthly_advice(user_id, period='YYYY-MM')`
- Similar to API above, but triggered by Celery Beat on 1st of month
- Send WhatsApp automatically

---

### Sprint 7: Session & Conversational Context Engine

#### Feature: Session Manager (Redis)
- [ ] Define `flow_defs` for multi-turn flows (e.g., create_budget slots)
- [ ] Middleware in FastAPI to check `session:{user_id}` on each incoming message
- [ ] Slot-filling logic:
- If `flow` exists, validate incoming message based on expected slot type
- On success, update Redis session; on all slots filled, call the final handler (e.g., create budget) and clear session
- [ ] Timeout & cleanup: expire sessions after 5 minutes of inactivity

---

## 3. Post-MVP (Nice-to-Have) Roadmap (Future Sprints)

1. **Sprint 8: Payment/Transfer Agent**
 - FastAPI endpoint: `POST /payments/transfer`
 - Integrate Mono “transfer” API
 - OTP/PIN validation flow
 - Store in `payments` table, update `transactions`

2. **Sprint 9: Fraud & Risk Monitoring**
 - Implement `fraud_rules` table
 - On new transaction, run rule engine, insert into `fraud_alerts` if flagged
 - Automatic block or send high-priority alert via Twilio

3. **Sprint 10: Advanced Exports (PDF & Sheets)**
 - Integrate Google Sheets API fully
 - Integrate WeasyPrint for PDF
 - Scheduled cleanup of old export objects in S3

4. **Sprint 11: Personalization & Recommendation Engine**
 - Build simple time-series forecasts for next month
 - Cohort comparisons (e.g., “similar users”)
 - A/B testing infrastructure for templates

5. **Sprint 12: Customer Support Engine & Admin Dashboard**
 - FastAPI: `POST /support/ticket`, `GET /support/ticket/{id}`, `PUT /support/ticket/{id}`
 - Slack or email integration for new ticket notifications
 - ReactJS admin UI for user management, benchmark settings, and support ticket queue

6. **Sprint 13: Security & Compliance Hardening**
 - Encrypt PII (Mono tokens, PINs) at rest
 - Audit logging hooks for critical actions
 - Backup & DR: nightly DB dump, test restores
 - Implement NDPR compliance checklist

---

## 4. Summary

- **MVP Locked**:  
1. User Onboarding & Authentication  
2. Transaction Ingestion (Mono sync + WhatsApp logging)  
3. Budget Engine (CRUD + threshold alerts)  
4. Analytics & Reporting (Daily summary + ad-hoc category spend)  
5. Notification Service (WhatsApp templating)  
6. Basic CSV Export  

- **Post-MVP Roadmap** (nice-to-have): Exports (PDF/Sheets), Financial Advice, Payments, Fraud Monitoring, Personalization, Support, Admin Dashboard, Security hardening.

Each feature has been broken down into clear, actionable technical tasks—using **FastAPI** for API endpoints, **Celery** for background jobs, **Redis** for sessions and caching, and **PostgreSQL** for persistence. By following this sprint plan, we can avoid scope creep and deliver a focused MVP rapidly before expanding to advanced functionality.  
