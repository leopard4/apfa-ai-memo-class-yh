from flask import request
from flask_restful import Resource
from mysql.connector import Error
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from mysql_connection import get_connection
from datetime import datetime

from email_validator import validate_email, EmailNotValidError

from utils import hash_password, check_password

class UserRegisterResource(Resource):
    def post(self):
        # {"email": "abc@naver.com",
        # "password": "1234",
        # "nickname": "홍길동"}
        
        data = request.get_json()
        
        try:
            validate_email(data['email'])
        except EmailNotValidError as e:
            return {'message': str(e)}, 400

        if len(data['password']) < 4 or len(data['password']) > 12: 
            return {'message': '비밀번호는 4자리 이상, 12자리 이하로 입력해주세요.'}, 400 
        
        hashed_password = hash_password( data['password'] ) 

        try:
            connection = get_connection()

            query = """
                INSERT INTO user ( email, password, nickname) 
                VALUES (%s, %s, %s);
            """
            
            record = (data['email'], hashed_password, data['nickname'])
            
            cursor = connection.cursor() # 커서를 가져온다.
            cursor.execute(query, record) # 쿼리를 실행한다.
            connection.commit() # 커밋한다.
            
            ### DB에 회원가입하여, insert 된 후에
            ### user 테이블의 id 값을 가져오는 코드!
            user_id = cursor.lastrowid # 마지막에 추가된 row의 id를 가져온다.

            cursor.close() # 커서를 닫는다.
            connection.close() # 커넥션을 닫는다.

        except Error as e:
            print(e)
            cursor.close() 
            connection.close()
            return {'message': str(e) }, 500 # 500은 서버에러를 리턴하는 에러코드
       
        # user_id를 바로 클라이언트에게 보내면 안되고,
        # jwt로 암호화 해서, 인증토큰을 보낸다.

        acces_token = create_access_token(identity=user_id ) # identity는 토큰에 담길 내용이다. # 담을게 여러개면 딕셔너리 형태로담는다.  
        # expires_delta는 토큰의 유효기간이다. # timedelta로 지정한다. # timedelta는 datetime에서 가져온다.

        return {'access_token': acces_token}, 200 # 200은 성공했다는 의미의 코드

class UserLoginResource(Resource):
   
    def post(self) :
        # {"email":"zzez@naver.com",
        # "password" : "1234" } # 클라이언트가 보낸 데이터
        
        # 1. 클라이언트가 보낸 데이터를 받는다.
        data = request.get_json()

        # 2. DB 로부터 해당 유저의 데이터를 가져온다.
        try :
            connection = get_connection()
            query = """
                select * 
                from user
                where email = %s;
            """
            record = (data['email'],) 
            
            cursor = connection.cursor(dictionary=True) # dictionary=True를 하면, 컬럼명을 key로 가지는 딕셔너리를 리턴한다.
            cursor.execute(query, record)
            
            result_list = cursor.fetchall() # 튜플의 리스트를 리턴한다. 
            
            if len(result_list) == 0 :
                return {'message' : '존재하지 않는 이메일입니다.'}, 400
                
            print("리설트리스트", result_list[0]) # 디버깅용
            i = 0
            for row in result_list :
                result_list[i]['createdAt'] = row['createdAt'].isoformat() 
                i += 1 

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'message' : str(e)}, 500 # 500은 서버에러를 리턴하는 에러코드

        print(result_list)

        # 3. 비밀번호를 비교한다.

        print("data['password']",data['password'])
        print("result_list[0]['password']",result_list[0]['password'])
        
        check = check_password(data['password'], result_list[0]['password']) 

        if check == False :
            return {'message' : '비밀번호가 틀렸습니다.'}, 400

        # 4. id를 jwt 토큰을 만들어서 클라이언트에게 보낸다.
        acces_token = create_access_token(identity=result_list[0]['id'] ) # identity는 토큰에 담길 내용이다. # 담을게 여러개면 딕셔너리 형태로담는다.

        return {'access_token': acces_token}, 200 # 200은 성공했다는 의미의 코드

### 로그 아웃 ####

# 로그아웃된 토큰을 저장할 set 만든다.

jwt_blocklist = set()

class UserLogoutResource(Resource) :

    @jwt_required() # jwt 토큰이 필요한 리소스이다.
    def post(self) :
        
        jti = get_jwt()['jti'] # jti는 jwt 토큰의 고유한 식별자이다.
        print(jti) # 디버깅용
        jwt_blocklist.add(jti) # 로그아웃된 토큰을 저장한다.

        return {'message' : '로그아웃 성공'}, 200
        

