import pandas as pd
import pymysql
from db_conn import *

# 엑셀 파일 경로
file_path = "movie_list_new.xls"

# 첫 번째 시트: 5번째 줄이 헤더
df1 = pd.read_excel(file_path, sheet_name=0, header=4)

# 두 번째 시트: 1번째 줄이 헤더
df2 = pd.read_excel(file_path, sheet_name=1, header=0)

# 컬럼 정리
df1.columns = df1.columns.str.strip()
df1 = df1[
    [
        "영화명",
        "영화명(영문)",
        "제작연도",
        "제작국가",
        "유형",
        "장르",
        "제작상태",
        "감독",
        "제작사",
    ]
]
df1.columns = [
    "movie_nm",
    "movie_nm_eng",
    "open_year",
    "nation",
    "type",
    "genre",
    "status",
    "director",
    "producer",
]

# 병합 및 전처리
df = pd.concat([df1, df2], ignore_index=True).drop_duplicates()
df = df.where(pd.notnull(df), None)

# 디버깅: 총 병합된 행 수 및 예시 행 출력
print("총 병합된 행 수:", len(df))
print("예시 행:")
print(df.head(5))


# DB 연결
# --- Create tables if not exist ---
with conn.cursor() as cursor:
    cursor.execute("""
        create table if not exists movie_info (
            movie_id int auto_increment primary key,
            movie_nm varchar(200),
            movie_nm_eng varchar(200),
            open_year year,
            nation varchar(100),
            type varchar(50),
            genre varchar(100),
            status varchar(50),
            director varchar(255),
            producer varchar(255)
        );
    """)
    cursor.execute("""
        create table if not exists genre (
            genre_id int auto_increment primary key,
            name varchar(100) unique
        );
    """)
    cursor.execute("""
        create table if not exists movie_genre (
            id int auto_increment primary key,
            movie_id int,
            genre_id int,
            foreign key (movie_id) references movie_info(movie_id),
            foreign key (genre_id) references genre(genre_id)
        );
    """)
    cursor.execute("""
        create table if not exists director (
            director_id int auto_increment primary key,
            name varchar(255) unique
        );
    """)
    cursor.execute("""
        create table if not exists movie_director (
            id int auto_increment primary key,
            movie_id int,
            director_id int,
            foreign key (movie_id) references movie_info(movie_id),
            foreign key (director_id) references director(director_id)
        );
    """)
    cursor.execute("""
        create table if not exists nation (
            nation_id int auto_increment primary key,
            name varchar(100) unique
        );
    """)
    cursor.execute("""
        create table if not exists movie_nation (
            id int auto_increment primary key,
            movie_id int,
            nation_id int,
            foreign key (movie_id) references movie_info(movie_id),
            foreign key (nation_id) references nation(nation_id)
        );
    """)


    # movie_info
    cursor.execute("CREATE INDEX idx_open_year ON movie_info(open_year);") # 제작연도
    cursor.execute("CREATE INDEX idx_status ON movie_info(status);") # 제작상태
    cursor.execute("CREATE INDEX idx_type ON movie_info(type);") # 유형
    # 영화명은 기본 검색에서는 %% search라서 못쓰이지만 인덱싱 검색에서는 가~나 이런식으로 찾아서 쓰이기좋음
    cursor.execute("CREATE INDEX idx_movie_nm ON movie_info(movie_nm);") # 영화명
    cursor.execute("CREATE INDEX idx_movie_nm_eng ON movie_info(movie_nm_eng);") # 영화명 영문

    # 연결 테이블 인덱스 (JOIN 성능 개선용)
    cursor.execute("CREATE INDEX idx_movie_director_movie ON movie_director(movie_id);") # 감독
    cursor.execute("CREATE INDEX idx_movie_director_director ON movie_director(director_id);")

    cursor.execute("CREATE INDEX idx_movie_genre_movie ON movie_genre(movie_id);") # 장르
    cursor.execute("CREATE INDEX idx_movie_genre_genre ON movie_genre(genre_id);")

    cursor.execute("CREATE INDEX idx_movie_nation_movie ON movie_nation(movie_id);") # 국적
    cursor.execute("CREATE INDEX idx_movie_nation_nation ON movie_nation(nation_id);")
    cursor.execute("CREATE INDEX idx_nation_name ON nation(name);")

    conn.commit()

inserted_count = 0

with conn.cursor() as cursor:

    insert_sql = """
        insert into movie_info (movie_nm, movie_nm_eng, open_year, nation, type, genre, status, director, producer)
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    for _, row in df.iterrows():
        values = [
            row.get(col)
            for col in [
                "movie_nm",
                "movie_nm_eng",
                "open_year",
                "nation",
                "type",
                "genre",
                "status",
                "director",
                "producer",
            ]
        ]
        # 모든 컬럼이 None인 행을 출력하고 건너뜀
        if all(v is None for v in values):
            print("⚠️ 모든 컬럼이 None인 행 발견:", row.to_dict())
            continue
        try:
            if values[2] is not None:
                values[2] = int(float(values[2]))
                if not (1901 <= values[2] <= 2155):
                    values[2] = None
        except ValueError:
            values[2] = None
        cursor.execute(insert_sql, tuple(values))
        inserted_count += 1

conn.commit()
print(f"총 {inserted_count}개의 영화 정보가 movie_info 테이블에 삽입되었습니다.")
conn.close()
