from data.db import ensure_database_initialized


if __name__ == "__main__":
    ensure_database_initialized()
    print("Database initialized.")
