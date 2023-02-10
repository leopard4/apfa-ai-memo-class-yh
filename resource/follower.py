from flask import request # 클라이언트가 보낸 데이터를 받기 위한 라이브러리
from flask_restful import Resource # API를 만들기 위한 라이브러리
from mysql.connector import Error # DB에 연결할 때, 에러가 발생할 수 있으므로, 에러처리를 위한 라이브러리
from flask_jwt_extended import jwt_required, get_jwt_identity # JWT를 사용하기 위한 라이브러리

from mysql_connection import get_connection # DB에 연결하기 위한 함수


class FollowResource(Resource) : # 친구맺기, 내친구의 메모만 불러오기, 친구 끊기
    
    @jwt_required()
    def post(self, followee_id) : # 친추
        
        user_id = get_jwt_identity()

        if followee_id == user_id :
            return {"result": "fail", "error" : "자기 자신을 친구로 추가할 수 없습니다."}, 400
        # 그리고 없는 id도 추가할수 있는문제가 발생
        # mysql에서 포링키 를 설정하면 해결할 수 있다.
        # 포링키는 테스트가 다 끝난 후 마지막에 실행한다.
        
        try :
            connection = get_connection()

            query = '''
                insert into follow
                (followerId, followeeId)
                values
                (%s, %s); '''
            
            record = (user_id, followee_id) 
            
            cursor = connection.cursor() 

            cursor.execute(query, record) 

            connection.commit() 

            cursor.close()
            connection.close()
        
        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"result": "fail", "error" : str(e)}, 500 

        return {"result": "success"}, 200
        
    @jwt_required()
    def delete(self, followee_id) : # 친삭

        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''
                delete from follow
                where followerId = %s and followeeId  = %s ; '''   
            
            record = (user_id, followee_id ) 
            
            cursor = connection.cursor() 

            cursor.execute(query, record) 

            connection.commit() 

            cursor.close()
            connection.close()
        
        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"result": "fail", "error" : str(e)}, 500
        
        return {"result": "success"}, 200
        
