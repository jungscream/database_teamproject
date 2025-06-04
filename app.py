from flask import Flask, jsonify
from flask_cors import CORS
from db_conn import *

app = Flask(__name__)
CORS(app)

### 조건문 써서 js에서 받아오는 입력으로 어떤 sql문 사용할지 
@app.route('/api/movies', methods=['GET'])
def get_movies():
    with conn.cursor() as cursor:
        sql = """
            SELECT movie_nm, movie_nm_eng, movie_id, open_year, nation, type, genre, status, director, producer
            FROM movie_info
            limit 500
        """
        cursor.execute(sql)
        results = cursor.fetchall()
    return jsonify(results)

if __name__ == '__main__':
    print("서버 실행 중...")
    app.run(port=5000, debug=True)
