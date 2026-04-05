# 🏪 RetailOS — Complete Retail Store Management System

> A production-grade, full-stack retail management platform with AI-powered insights.
> **Stack:** FastAPI · Supabase · Vanilla JS · Chart.js · Claude AI

---

## ✨ Features

| Module | Capabilities |
|---|---|
| 🏪 **Dashboard** | KPI cards, revenue charts, low-stock alerts, top products |
| 📦 **Inventory** | Add/edit/delete products, stock levels, margin analysis, category filters |
| 🧾 **Billing / POS** | Product grid, cart, discount/tax, invoice generation, print support |
| 🏭 **Suppliers** | Supplier directory, contact info, GST records |
| 🛒 **Procurement** | Record purchases, auto-update inventory on procurement |
| 📈 **Reports** | Sales history, trend charts, payment methods, CSV export |
| 🤖 **AI Chatbot** | Natural language store queries with Claude AI + rule-based fallback |

---

## 🗂️ Project Structure

```
retail-store/
├── frontend/
│   ├── index.html          # Auth (login/signup)
│   ├── dashboard.html      # Analytics dashboard
│   ├── inventory.html      # Product management
│   ├── billing.html        # POS / billing
│   ├── suppliers.html      # Supplier management
│   ├── purchases.html      # Procurement records
│   ├── reports.html        # Sales reports
│   ├── chatbot.html        # AI assistant
│   ├── style.css           # Global design system (Dark Industrial theme)
│   ├── app.js              # Shared API client, utilities, auth
│   └── sidebar.js          # Sidebar HTML injection
│
├── backend/
│   ├── app.py              # FastAPI entry point
│   ├── requirements.txt    # Python dependencies
│   ├── render.yaml         # Render deployment config
│   ├── .env.example        # Environment variables template
│   ├── config/
│   │   └── supabase_client.py
│   └── routes/
│       ├── products.py     # /api/products
│       ├── suppliers.py    # /api/suppliers + /api/suppliers/purchases
│       ├── sales.py        # /api/sales
│       ├── dashboard.py    # /api/dashboard/stats
│       └── chatbot.py      # /api/chatbot
│
├── supabase_schema.sql     # Complete DB schema + sample data
└── vercel.json             # Vercel frontend deployment
```

---

## ⚡ Quick Start

### 1. Supabase Setup (5 minutes)

1. Create a free project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** → paste the full content of `supabase_schema.sql` → **Run**
3. Go to **Settings → API** and copy:
   - `Project URL` → `SUPABASE_URL`
   - `anon public` key → `SUPABASE_ANON_KEY`
   - `service_role` key → `SUPABASE_SERVICE_KEY`

### 2. Backend Setup

```bash
cd backend
cp .env.example .env
# Fill in your SUPABASE_URL, SUPABASE_SERVICE_KEY, and ANTHROPIC_API_KEY

pip install -r requirements.txt
python app.py
# API running at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### 3. Frontend Setup

```bash
# Option A: VS Code Live Server (recommended)
# Open frontend/ folder in VS Code → right-click index.html → "Open with Live Server"

# Option B: Python simple server
cd frontend
python -m http.server 5500
# Open http://localhost:5500
```

### 4. Configure Frontend API URL

Edit `frontend/app.js`, line 5:
```javascript
const CONFIG = {
  API_BASE: 'http://localhost:8000',      // local dev
  SUPABASE_URL: 'https://xxxx.supabase.co',
  SUPABASE_ANON_KEY: 'your-anon-key'
};
```

---

## 🚀 Free Deployment

### Backend → Render.com (Free Tier)

1. Push `backend/` folder to a GitHub repo
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variables:
   ```
   SUPABASE_URL=https://xxxx.supabase.co
   SUPABASE_SERVICE_KEY=your-service-key
   ANTHROPIC_API_KEY=your-key
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```
7. Deploy → copy the URL (e.g. `https://retailos-backend.onrender.com`)

### Frontend → Vercel (Free Tier)

1. Push entire project to GitHub
2. Go to [vercel.com](https://vercel.com) → **Import Project**
3. Set root directory to `frontend/`
4. Deploy → copy the URL
5. Update `app.js` `API_BASE` to your Render backend URL
6. Update Render `CORS_ORIGINS` to your Vercel URL

### Database → Supabase (Free Tier — 500MB)
Already set up in Step 1. ✅

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SUPABASE_URL` | ✅ | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | ✅ | Service role key (bypasses RLS) |
| `SUPABASE_ANON_KEY` | ✅ | Anon key (for frontend auth) |
| `ANTHROPIC_API_KEY` | ⭐ Optional | Enable AI chatbot (falls back to rule-based) |
| `CORS_ORIGINS` | ✅ | Comma-separated allowed frontend URLs |
| `APP_ENV` | Optional | `development` enables hot reload |

---

## 🧪 Demo Mode

No backend? No problem. Click **"Enter Demo Mode"** on the login page to explore all features with realistic sample data — no API keys needed.

---

## 📡 API Reference

All endpoints return `{ success: bool, data: ..., message?: str }`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard/stats` | All KPIs for dashboard |
| GET | `/api/products/` | List all products (with search/filter) |
| POST | `/api/products/` | Create product |
| PUT | `/api/products/{id}` | Update product |
| DELETE | `/api/products/{id}` | Delete product |
| GET | `/api/suppliers/` | List suppliers |
| POST | `/api/suppliers/` | Create supplier |
| GET | `/api/suppliers/purchases/all` | Purchase history |
| POST | `/api/suppliers/purchases` | Record procurement (auto-updates stock) |
| GET | `/api/sales/` | Sales history |
| POST | `/api/sales/` | Process sale (validates stock + deducts) |
| GET | `/api/sales/today` | Today's sales |
| POST | `/api/chatbot/` | AI assistant query |
| GET | `/api/chatbot/suggestions` | Suggested queries |

Interactive Swagger docs at `/docs` when backend is running.

---

## 🎨 Tech Choices

- **Dark Industrial** UI theme — Syne (headings) + Outfit (body) fonts
- CSS-only animations with staggered card reveals
- Supabase RLS (Row Level Security) for data protection
- Full demo mode — all pages work without a backend
- Chart.js v4 for all analytics visualizations
- Invoice printing via `window.print()` — no PDF libraries needed
- CSV export built-in on Reports page

---

## 📦 Key Dependencies

**Backend**
- `fastapi` + `uvicorn` — High-performance async API
- `supabase` — Official Python SDK
- `anthropic` — Claude AI SDK
- `pydantic` — Request/response validation

**Frontend**
- `Chart.js` — Revenue charts, doughnut charts
- `Google Fonts` (Syne + Outfit)
- No frameworks — pure Vanilla JS for portability

---

## 🔒 Security Notes

- Never expose `SUPABASE_SERVICE_KEY` in frontend code
- The frontend uses `SUPABASE_ANON_KEY` only for auth
- All data operations go through the FastAPI backend (service key server-side only)
- Enable Supabase RLS policies before going to production

---

*Built with ❤️ using FastAPI, Supabase, and Claude AI*
