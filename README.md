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
