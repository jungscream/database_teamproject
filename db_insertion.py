import pymysql
import pandas as pd
import re
from db_conn import *

def split_clean(text):
    if not text or str(text).lower() == 'nan':
        return []
    return [t.strip() for t in re.split(r"[,/&;·]", str(text)) if t.strip() and str(t).lower() != 'nan']

def clean_year(y):
    try:
        y = int(float(y))
        if 1880 <= y <= 2025:
            return y
    except Exception:
        pass
    return None

with conn.cursor() as cursor:
    # movie_info 불러오기
    cursor.execute("SELECT * FROM movie_info")
    df = pd.DataFrame(cursor.fetchall())
    df = df.where(pd.notnull(df), None)
    print(f"✅ movie_info 로드 완료: {len(df)}행")

    # 정규화 테이블 데이터 수집
    genres = set()
    directors = set()
    countries = set()

    for idx, row in df.iterrows():
        genres.update(split_clean(row["genre"]))
        directors.update(split_clean(row["director"]))
        countries.update(split_clean(row["nation"]))

    # executemany를 위한 튜플 리스트 생성
    genre_values = [(g,) for g in genres]
    director_values = [(d,) for d in directors]
    nation_values = [(c,) for c in countries]

    cursor.executemany("INSERT IGNORE INTO genre(name) VALUES (%s)", genre_values)
    cursor.executemany("INSERT IGNORE INTO director(name) VALUES (%s)", director_values)
    cursor.executemany("INSERT IGNORE INTO nation(name) VALUES (%s)", nation_values)

    # ID 매핑
    cursor.execute("SELECT movie_id, movie_nm, movie_nm_eng, open_year FROM movie_info")
    movie_id_map = {
        (r["movie_nm"], r["movie_nm_eng"], r["open_year"]): r["movie_id"] for r in cursor.fetchall()
    }

    cursor.execute("SELECT genre_id, name FROM genre")
    genre_id_map = {r["name"]: r["genre_id"] for r in cursor.fetchall()}

    cursor.execute("SELECT director_id, name FROM director")
    director_id_map = {r["name"]: r["director_id"] for r in cursor.fetchall()}

    cursor.execute("SELECT nation_id, name FROM nation")
    nation_id_map = {r["name"]: r["nation_id"] for r in cursor.fetchall()}

    # 관계 테이블 데이터 수집
    genre_data = []
    director_data = []
    nation_data = []

    for idx, row in df.iterrows():
        key = (row["movie_nm"], row["movie_nm_eng"], row["open_year"])
        movie_id = movie_id_map.get(key)
        if not movie_id:
            continue

        for genre in split_clean(row["genre"]):
            genre_id = genre_id_map.get(genre)
            if genre_id:
                genre_data.append((movie_id, genre_id))

        for director in split_clean(row["director"]):
            director_id = director_id_map.get(director)
            if director_id:
                director_data.append((movie_id, director_id))

        for nation in split_clean(row["nation"]):
            nation_id = nation_id_map.get(nation)
            if nation_id:
                nation_data.append((movie_id, nation_id))

    cursor.executemany(
        "INSERT IGNORE INTO movie_genre(movie_id, genre_id) VALUES (%s, %s)",
        genre_data
    )
    print(f"✅ 장르 매핑 완료: {len(genre_data)}건")

    cursor.executemany(
        "INSERT IGNORE INTO movie_director(movie_id, director_id) VALUES (%s, %s)",
        director_data
    )
    print(f"✅ 감독 매핑 완료: {len(director_data)}건")

    cursor.executemany(
        "INSERT IGNORE INTO movie_nation(movie_id, nation_id) VALUES (%s, %s)",
        nation_data
    )
    print(f"✅ 국가 매핑 완료: {len(nation_data)}건")

    print("🎯 관계 매핑 요약")
    print(f"  - movie_genre: {len(genre_data)}")
    print(f"  - movie_director: {len(director_data)}")
    print(f"  - movie_nation: {len(nation_data)}")

    conn.commit()

    # 중복 제거
    cursor.execute("""
        delete from movie_genre
        where id not in (
            select min_id from (
                select min(id) as min_id
                from movie_genre
                group by movie_id, genre_id
            ) as sub
        );
    """)
    print(f"🧹 movie_genre 중복 제거 완료, 삭제된 행 수: {cursor.rowcount}")

    cursor.execute("""
        delete from movie_director
        where id not in (
            select min_id from (
                select min(id) as min_id
                from movie_director
                group by movie_id, director_id
            ) as sub
        );
    """)
    print(f"🧹 movie_director 중복 제거 완료, 삭제된 행 수: {cursor.rowcount}")

    cursor.execute("""
        delete from movie_nation
        where id not in (
            select min_id from (
                select min(id) as min_id
                from movie_nation
                group by movie_id, nation_id
            ) as sub
        );
    """)
    print(f"🧹 movie_nation 중복 제거 완료, 삭제된 행 수: {cursor.rowcount}")

    cursor.execute("select count(*) as cnt from movie_genre")
    print(f"🧹 중복 제거 후 movie_genre 남은 행: {cursor.fetchone()['cnt']}")

    cursor.execute("select count(*) as cnt from movie_director")
    print(f"🧹 중복 제거 후 movie_director 남은 행: {cursor.fetchone()['cnt']}")

    cursor.execute("select count(*) as cnt from movie_nation")
    print(f"🧹 중복 제거 후 movie_nation 남은 행: {cursor.fetchone()['cnt']}")

    conn.commit()
conn.close()