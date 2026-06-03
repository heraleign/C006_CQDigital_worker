"""Start the Digital Worker backend server.
Use this instead of `uvicorn app.main:app` to avoid import path issues.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
