from fastapi import FastAPI

app = FastAPI(title="PulseWatch")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}
