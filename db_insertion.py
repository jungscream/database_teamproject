import pymysql
import pandas as pd
import re
from db_conn import *

# Utility function to split and clean genre, director, nation fields
def split_clean(text):
    if not text or str(text).lower() == 'nan':
        return []
    return [t.strip() for t in re.split(r"[,/&;·]", str(text)) if t.strip() and str(t).lower() != 'nan']


# Clean year: only allow valid years in range
def clean_year(y):
    try:
        y = int(float(y))
        if 1880 <= y <= 2025:
            return y
    except Exception:
        pass
    return None

with conn.cursor() as cursor:
    cursor.execute("SELECT * FROM movie_info")
    df = pd.DataFrame(cursor.fetchall())
    df = df.where(pd.notnull(df), None)
    print(f"✅ movie_info 로드 완료: {len(df)}행")

    # Step 0: Insert distinct genre/director/nation into normalized tables
    genres = set()
    directors = set()
    countries = set()

    for idx, row in df.iterrows():
        genres.update(split_clean(row["genre"]))
        directors.update(split_clean(row["director"]))
        countries.update(split_clean(row["nation"]))

    for g in genres:
        cursor.execute("INSERT IGNORE INTO genre(name) VALUES (%s)", (g,))
    for d in directors:
        cursor.execute("INSERT IGNORE INTO director(name) VALUES (%s)", (d,))
    for c in countries:
        cursor.execute("INSERT IGNORE INTO nation(name) VALUES (%s)", (c,))

    # Build ID maps
    
    cursor.execute("SELECT movie_id, movie_nm, open_year FROM movie_info")
    movie_id_map = {
        (r["movie_nm"], r["open_year"]): r["movie_id"] for r in cursor.fetchall()
    }
    cursor.execute("SELECT genre_id, name FROM genre")

    genre_id_map = {r["name"]: r["genre_id"] for r in cursor.fetchall()}
    cursor.execute("SELECT director_id, name FROM director")
    director_id_map = {r["name"]: r["director_id"] for r in cursor.fetchall()}
    cursor.execute("SELECT nation_id, name FROM nation")
    nation_id_map = {r["name"]: r["nation_id"] for r in cursor.fetchall()}

    # Map N:M relationships for genres
    genre_inserted = 0
    for idx, row in df.iterrows():
        key = (row["movie_nm"], row["open_year"])
        movie_id = movie_id_map.get(key)
        if not movie_id:
            continue
        for genre in split_clean(row["genre"]):
            genre_id = genre_id_map.get(genre)
            if genre_id:
                cursor.execute(
                    
                    "INSERT IGNORE INTO movie_genre(movie_id, genre_id) VALUES (%s, %s)",
                    (movie_id, genre_id),
                )
                genre_inserted += 1
    print(f"✅ 장르 매핑 완료: {genre_inserted}건")

    # Map N:M relationships for directors
    director_inserted = 0
    for idx, row in df.iterrows():
        key = (row["movie_nm"], row["open_year"])
        movie_id = movie_id_map.get(key)
        if not movie_id:
            continue
        for director in split_clean(row["director"]):
            director_id = director_id_map.get(director)
            if director_id:
                cursor.execute(
                    "INSERT IGNORE INTO movie_director(movie_id, director_id) VALUES (%s, %s)",
                    (movie_id, director_id),
                )
                director_inserted += 1
    print(f"✅ 감독 매핑 완료: {director_inserted}건")

    # Map N:M relationships for nations
    nation_inserted = 0
    for idx, row in df.iterrows():
        key = (row["movie_nm"], row["open_year"])
        movie_id = movie_id_map.get(key)
        if not movie_id:
            continue
        for nation in split_clean(row["nation"]):
            nation_id = nation_id_map.get(nation)
            if nation_id:
                cursor.execute(
                    "INSERT IGNORE INTO movie_nation(movie_id, nation_id) VALUES (%s, %s)",
                    (movie_id, nation_id),
                )
                nation_inserted += 1
    print(f"✅ 국가 매핑 완료: {nation_inserted}건")

    print("🎯 관계 매핑 요약")
    print(f"  - movie_genre: {genre_inserted}")
    print(f"  - movie_director: {director_inserted}")
    print(f"  - movie_nation: {nation_inserted}")


    conn.commit()
conn.close()
