import pymysql
import pandas as pd
import re
from db_conn import *

# 유틸리티 함수: 장르, 감독, 국가 필드를 분리 및 정제
# 쉼표, 슬래시, 앰퍼샌드 등 구분자로 분할 후 공백 제거
# 예: "드라마, 액션/코미디" → ["드라마", "액션", "코미디"]

def split_clean(text):
    if not text or str(text).lower() == 'nan':
        return []
    return [t.strip() for t in re.split(r"[,/&;·]", str(text)) if t.strip() and str(t).lower() != 'nan']


#
# 연도 정제 함수: 1880~2025 범위 내의 연도만 허용
# 유효하지 않으면 None 반환
def clean_year(y):
    try:
        y = int(float(y))
        if 1880 <= y <= 2025:
            return y
    except Exception:
        pass
    return None


# 데이터베이스 연결

with conn.cursor() as cursor:
    # movie_info 불러오기: 영화 정보 테이블 전체를 DataFrame으로 로드
    cursor.execute("SELECT * FROM movie_info")
    df = pd.DataFrame(cursor.fetchall())
    df = df.where(pd.notnull(df), None)
    print(f"✅ movie_info 로드 완료: {len(df)}행")

    # 정규화 테이블에 장르/감독/국가 삽입 (중복 없이)
    genres = set()
    directors = set()
    countries = set()

    # 각 영화의 장르, 감독, 국가를 set에 추가하여 중복 제거
    for idx, row in df.iterrows():
        genres.update(split_clean(row["genre"]))
        directors.update(split_clean(row["director"]))
        countries.update(split_clean(row["nation"]))

    # genre 테이블에 장르 삽입
    for g in genres:
        cursor.execute("INSERT IGNORE INTO genre(name) VALUES (%s)", (g,))
    # director 테이블에 감독 삽입
    for d in directors:
        cursor.execute("INSERT IGNORE INTO director(name) VALUES (%s)", (d,))
    # nation 테이블에 국가 삽입
    for c in countries:
        cursor.execute("INSERT IGNORE INTO nation(name) VALUES (%s)", (c,))

    # 관계 테이블 매핑을 위한 ID 매핑 딕셔너리 생성
    # (영화이름, 영화영문이름, 개봉년도) → movie_id
    cursor.execute("SELECT movie_id, movie_nm, movie_nm_eng, open_year FROM movie_info")
    movie_id_map = {
        (r["movie_nm"], r["movie_nm_eng"], r["open_year"]): r["movie_id"] for r in cursor.fetchall()
    }
    # 장르명 → genre_id
    cursor.execute("SELECT genre_id, name FROM genre")
    genre_id_map = {r["name"]: r["genre_id"] for r in cursor.fetchall()}
    # 감독명 → director_id
    cursor.execute("SELECT director_id, name FROM director")
    director_id_map = {r["name"]: r["director_id"] for r in cursor.fetchall()}
    # 국가명 → nation_id
    cursor.execute("SELECT nation_id, name FROM nation")
    nation_id_map = {r["name"]: r["nation_id"] for r in cursor.fetchall()}

    # 관계 테이블 매핑 (장르)
    genre_inserted = 0
    for idx, row in df.iterrows():
        key = (row["movie_nm"], row["movie_nm_eng"], row["open_year"])
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

    # 관계 테이블 매핑 (감독)
    director_inserted = 0
    for idx, row in df.iterrows():
        key = (row["movie_nm"], row["movie_nm_eng"], row["open_year"])
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

    # 관계 테이블 매핑 (국가)
    nation_inserted = 0
    for idx, row in df.iterrows():
        key = (row["movie_nm"], row["movie_nm_eng"], row["open_year"])
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

    # 관계 매핑 요약 출력
    print("🎯 관계 매핑 요약")
    print(f"  - movie_genre: {genre_inserted}")
    print(f"  - movie_director: {director_inserted}")
    print(f"  - movie_nation: {nation_inserted}")

    # 변경사항 커밋
    conn.commit()

    # 중복 제거: movie_genre
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

    # 중복 제거: movie_director
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

    # 중복 제거: movie_nation
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

    # 중복 제거 확인용: 각 관계 테이블에서 최종 행 수 출력
    cursor.execute("select count(*) as cnt from movie_genre")
    print(f"🧹 중복 제거 후 movie_genre 남은 행: {cursor.fetchone()['cnt']}")

    cursor.execute("select count(*) as cnt from movie_director")
    print(f"🧹 중복 제거 후 movie_director 남은 행: {cursor.fetchone()['cnt']}")

    cursor.execute("select count(*) as cnt from movie_nation")
    print(f"🧹 중복 제거 후 movie_nation 남은 행: {cursor.fetchone()['cnt']}")

    conn.commit()
conn.close()
