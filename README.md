# PulseWatch

PulseWatch is a lightweight web service monitoring application built with FastAPI.

## Local development

Create and activate a virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy the example environment file:

```bash
cp .env.example .env
```

The example uses a local SQLite database so the application works without a separate
database server. To use PostgreSQL, set `DATABASE_URL` to a SQLAlchemy PostgreSQL URL,
for example `postgresql+psycopg://user:password@localhost:5432/pulsewatch`.

Run the tests:

```bash
pytest
```

Start the development server:

```bash
uvicorn app.main:app --reload
```

The health endpoint is available at <http://127.0.0.1:8000/health>.
