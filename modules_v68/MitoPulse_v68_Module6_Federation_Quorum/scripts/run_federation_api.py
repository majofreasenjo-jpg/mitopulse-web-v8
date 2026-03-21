import uvicorn

if __name__ == "__main__":
    uvicorn.run("mitopulse_federation.api:app", host="0.0.0.0", port=8010, reload=True)
