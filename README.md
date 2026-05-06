# HackerNews Data Aggregator API

A FastAPI-based service that retrieves and transforms data from the official Hacker News API.

## Endpoints

### 1. `/top-50-comments`

Returns the first 50 top-level comments from the first 100 top stories.

---

### 2. `/top-10-words`

Returns the 10 most frequently used words from the first 100 top-level comments of the top 30 stories.

---

### 3. `/top-words-all-comments`

Returns the most frequently used words from all comments, including nested comments, from the first 10 top stories.


## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd hn-api
```

---

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install fastapi uvicorn httpx beautifulsoup4 pydantic-settings
```

---

### 4. Create Environment Variables

Create a `.env` file in the project root:

```env
HN_BASE_URL=https://hacker-news.firebaseio.com/v0
```

---

## Running the Application

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

Application URL:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

### What was the hardest part?


### What part of the system could be improved?


### Scaling it handle 1K calls/sec? And 1M?

### How I would automate the testing?

### How would I implement a continuous development system (pipelines) for this particular case?