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

## Docker Compose

Copy the safe development environment placeholders, build, and start the API and
PostgreSQL services:

```bash
cp .env.example .env
docker compose config
docker compose build
docker compose up -d
```

Open <http://localhost:8000/>. View logs with:

```bash
docker compose logs -f
```

Stop the containers without deleting PostgreSQL data:

```bash
docker compose down
```

The named `postgres_data` volume persists database data between container restarts.
Run `docker compose down -v` only when you intentionally want to delete that data.
