from fastapi import FastAPI
import psycopg2
import os
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Izinkan akses dari Google Colab
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan asal tertentu jika ingin lebih aman
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Konfigurasi koneksi database
DB_USER = 'albudi'
DB_PASS = 'albudi'
DB_HOST = 'IPBD-postgres'
DB_PORT = '5432'
DB_NAME = 'IMDB'

# Gunakan f-string untuk membentuk DATABASE_URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

@app.get("/training-data")
def get_training_data():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        query = """
            SELECT
                t.title_id,
                t.primary_title,
                t.title_type,
                t.is_adult,
                t.start_year::INT AS start_year,
                t.runtime_minutes,
                t.genres,
                r.region,
                r.region_title,
                r.region_title_type,
                f.average_rating,
                f.num_votes
            FROM fact_title_ratings f
            JOIN dim_titles t
              ON f.title_id = t.title_id
            JOIN dim_region_titles r
              ON f.region_id = r.region_id
             AND f.ordering = r.ordering
            WHERE f.average_rating IS NOT NULL
              AND t.is_adult = FALSE
            LIMIT 100000;
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        return result

    except Exception as e:
        return {"error": str(e)}

    finally:
        if conn:
            cursor.close()
            conn.close()
