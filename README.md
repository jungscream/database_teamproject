# database_teamproject

db_conn.py 파일을 따로 만들어서 
```python
import pymysql

conn = pymysql.connect(
    host='yourhost',
    user='your_username',
    password='your_password',
    database='your_dbname',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
```
!!

***TODO***
1. 사용자 입력 있을 때 처리 (JS에서 검색이나 버튼에 따라 다른 값으로 받아서 python으로 넘겨주면될듯)
2. index 설정
3. 테이블 구축 python 코드로 옮기기
4. DB 테이블 정규화해서 구축
