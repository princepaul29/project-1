---

# :shopping_bags: Web Scraper API

Search products across platforms like **Amazon** and **Flipkart** using a unified API.

Supports filtering by price and multiple pages. Built with **FastAPI**.

---

## :rocket: Features

- :mag: Unified product search (`/search`)
- :moneybag: Filter by min/max price
- :page_facing_up: Data auto-saved to JSON
- :zap: FastAPI + Swagger UI
- :floppy_disk: Pluggable provider architecture

---

## :bricks: Project Structure

```bash
web_scraper/
├── app/
│   ├── models/           # Product dataclass
│   ├── providers/        # Base + Amazon, Flipkart providers
│   ├── services/         # StorageManager (JSON-based)
│   └── main.py           # FastAPI app
├── data/                 # Output directory (JSON saved here)
├── requirements.txt
└── README.md
```

---

## :tools: Setup Instructions

### 1. :key: API Key

Set your API key as an environment variable:

```bash
export SCRAPEHERO_API=your_super_secret_key
```

*(It is recommended to include this in the ~/.bashrc or ~/.zshrc file).*

### 2. :package: Install Dependencies

Create a virtual environment and install:

```bash
python3 -m venv venv
source venv/bin/activate

# Recommended: using `uv` (blazing fast)
uv pip install -r requirements.txt

# Or with pip
pip install -r requirements.txt
```

---

## :arrow_forward: Run the Server

```bash
uvicorn app.main:app --reload
```

> The server will run on `http://127.0.0.1:8000`

---

## :test_tube: API Endpoints

### `GET /`
Simple root endpoint for health check
Redirects to Swagger documentation

---

### `GET /search` — Main API

Query Amazon or Flipkart.

#### :inbox_tray: Query Parameters:

| Name        | Type     | Description                            |
|-------------|----------|----------------------------------------|
| `query`     | string   | :white_check_mark: Required — e.g., `laptop`           |
| `pages`     | integer  | Optional — Number of pages to fetch    |
| `min_price` | integer  | Optional — Filter below this price     |
| `max_price` | integer  | Optional — Filter above this price     |

#### :white_check_mark: Response:

```json
{
  "flipkart_results": [
    {
      name: "RTX 5090",
      price: "3459" (in USD),
      url: "https://test.url.com"
    },
    ...
  ],
  "amazon_results": [
    {
      name: "RX 9070 XT",
      price: "650",
      url: "https://amazon.test.com"
    },
    ...
  ]
}
```

---

## :blue_book: API Docs (Swagger)

FastAPI includes interactive Swagger docs:

- [http://localhost:8000/docs](http://localhost:8000/docs) – Swagger UI  
- [http://localhost:8000/redoc](http://localhost:8000/redoc) – ReDoc  
- [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json) – OpenAPI schema  

---

## :dividers: Data Output

Scraped results are saved in the `data/` folder as JSON files.

You can configure the folder and filename inside `app/services/storage.py`.

---

## :brain: Tech Stack

- **FastAPI**
- **Requests** for scraping
- **Dataclasses** for modeling
- **JSON-based Storage** (no DB required)

---