from flask import Flask, jsonify, request
from flask_cors import CORS
from db_conn import *
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5500"}})

# 초기에 테이블 작성
@app.route('/api/movies', methods=['GET'])
def get_movies():
    with conn.cursor() as cursor:
        sql = """
            SELECT movie_nm, movie_nm_eng, movie_id, open_year, nation, type, genre, status, director, producer
            FROM movie_info
        """
        cursor.execute(sql)
        results = cursor.fetchall()

        # None 값을 빈 문자열로 바꾸기
        clean_results = []
        for row in results:
            clean_row = {k: (v if v is not None else '') for k, v in row.items()}
            clean_results.append(clean_row)

    return jsonify(clean_results)

# 검색했을때 테이블 재생성
@app.route('/api/search', methods=['GET'])
def search_movies():
    reg = re.compile(r'[a-zA-Z]')

    sort = request.args.get('sort', 'none')

    # movie_info 테이블에서 select 
    movie_nm = request.args.get('movie_nm', '').strip() # 영화명, 영화명_영문 %% search
    open_year1 = request.args.get('open_year1', '').strip() # 제작연도 range search
    open_year2 = request.args.get('open_year2', '').strip() # 제작연도 range search
    status = request.args.get('status', '').strip() # 제작상태 match search
    type = request.args.get('type', '').strip() # 유형 match search

    # 정규화된 다른 테이블에서 select
    director = request.args.get('director', '').strip() # 감독 %% search 감독 자체를 감독 테이블에서 찾는건 full search로 찾고 join할때 성능 높이기위한 index처리
    genre = request.args.get('genre', '').strip() # 장르 match search
    nation = request.args.get('nation', '').strip() # 국적 match search
    bossNation = request.args.get('bossNation', '').strip() # 국적 match search

    conditions = []
    values = []

    # movie_info에서 바로 select
    sql = """
        SELECT 
            *
        FROM movie_info mi
    """

    # 제작연도 정렬
    if sort == 'open_year':
        sql += " ORDER BY open_year ASC"

    # 영화명 정렬
    if sort == 'movie_nm':
        sql += " ORDER BY movie_nm ASC"
    
    # 감독 (부분 검색 유지)
    if director:
        conditions.append("""
            EXISTS (
                SELECT 1 FROM movie_director md
                JOIN director d ON md.director_id = d.director_id
                WHERE md.movie_id = mi.movie_id AND d.name LIKE %s
            )
        """)
        values.append(f"%{director}%")

    # 장르 (정확히 일치하는 match search)
    if genre:
        conditions.append("""
            EXISTS (
                SELECT 1 FROM movie_genre mg
                JOIN genre g ON mg.genre_id = g.genre_id
                WHERE mg.movie_id = mi.movie_id AND g.name = %s
            )
        """)
        values.append(genre)

    # 국가 (정확히 일치하는 match search)
    if nation:
        conditions.append("""
            EXISTS (
                SELECT 1 FROM movie_nation mc
                JOIN nation n ON mc.nation_id = n.nation_id
                WHERE mc.movie_id = mi.movie_id AND n.name = %s
            )
        """)
        values.append(nation)

    if bossNation:
        conditions.append("""
            EXISTS (
                SELECT 1
                FROM movie_nation mc
                JOIN nation n ON mc.nation_id = n.nation_id
                WHERE mc.movie_id = mi.movie_id
                GROUP BY mc.movie_id
                HAVING COUNT(*) = 1 AND MAX(n.name) = %s
            )
        """)
        values.append(bossNation)

    # 한글, 영어 확인해서 영화명 검색
    if movie_nm:
        conditions.append("(movie_nm LIKE %s OR movie_nm_eng LIKE %s)")
        values.append(f"%{movie_nm}%")
        values.append(f"%{movie_nm}%")

    # 제작연도
    if open_year1 and open_year2:
        conditions.append("open_year BETWEEN %s AND %s")
        values.extend([open_year1, open_year2])

    # 제작상태
    if status:
        conditions.append("status = %s")
        values.append(status)

    # 유형
    if type:
        conditions.append("type = %s")
        values.append(type)       

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    with conn.cursor() as cursor:
        cursor.execute(sql, values)
        results = cursor.fetchall()

        clean_results = []
        for row in results:
            clean_row = {k: (v if v is not None else '') for k, v in row.items()}
            clean_results.append(clean_row)

    return jsonify(clean_results)

# 인덱싱 할때 테이블 재생성
@app.route('/api/indexing', methods=['GET'])
def indexing_search():
    index = request.args.get('index', '').strip()
    cursor = conn.cursor()

    # 한글 초성 처리 (ㄱ~ㅎ)
    초성_map = {
        'ㄱ': ('가', '나'),
        'ㄴ': ('나', '다'),
        'ㄷ': ('다', '라'),
        'ㄹ': ('라', '마'),
        'ㅁ': ('마', '바'),
        'ㅂ': ('바', '사'),
        'ㅅ': ('사', '아'),
        'ㅇ': ('아', '자'),
        'ㅈ': ('자', '차'),
        'ㅊ': ('차', '카'),
        'ㅋ': ('카', '타'),
        'ㅌ': ('타', '파'),
        'ㅍ': ('파', '하'),
        'ㅎ': ('하', '힣'),
    }

    if index in 초성_map:
        start, end = 초성_map[index]
        sql = "SELECT * FROM movie_info WHERE movie_nm >= %s AND movie_nm < %s"
        cursor.execute(sql, (start, end))
    else:
        # 영어 대문자
        sql = "SELECT * FROM movie_info WHERE movie_nm_eng LIKE %s"
        cursor.execute(sql, (f"{index}%",))

    results = cursor.fetchall()
    clean_results = []
    for row in results:
        clean_row = {k: (v if v is not None else '') for k, v in row.items()}
        clean_results.append(clean_row)
    return jsonify(clean_results)

if __name__ == '__main__':
    print("서버 실행 중...")
    app.run(port=5050, debug=True)
