from flask import request # 클라이언트가 보낸 데이터를 받기 위한 라이브러리
from flask_restful import Resource # API를 만들기 위한 라이브러리
from mysql.connector import Error # DB에 연결할 때, 에러가 발생할 수 있으므로, 에러처리를 위한 라이브러리
from flask_jwt_extended import jwt_required, get_jwt_identity # JWT를 사용하기 위한 라이브러리

from mysql_connection import get_connection # DB에 연결하기 위한 함수

class MemoListResource(Resource): # 메모를 생성하고 내 메모를 조회하는 API를 만들기 위한 클래스
    
    # APi를 처리하는 함수 개발
    # HTTP Method 를 보고 ! 똑같이 만들어준다.
    # @jwt_required() == jwt 토큰이 필수라는 뜻! : 토큰이 없으면, 이 api는 실행할수 없다.
    @jwt_required() # 헤더에 Authorization 토큰이 있어야만, API를 사용할 수 있다. 
    def post(self):
        # 1. 클라이언트가 보내준 데이터가 있으면
        #    그 데이터를 받아준다.

        # {"title": "저녁약속",
        # "datetime": "2023-01-11 15",
        # "content": "친구랑 저녁"}

        data = request.get_json()
        
        # 1.1 헤더에 jwt 토큰이 있으면, 토큰 정보를 받아준다.
        user_id = get_jwt_identity() # 유저 id 토큰 정보를 받아준다. # 복호화하는 함수

        # 2. 받은 데이터를 DB에 저장한다.         

        try :
            ### 1 . DB 연결
            # mysql_connection.py 에서 만든 함수를 호출
            connection = get_connection()

            ### 2. 쿼리문 만들기
            query = '''
                    insert into memo
                    (userId, title, datetime,content)
                    values
                    (%s, %s, %s, %s);'''
            ### 3. 쿼리에 매칭되는 변수 처리 해준다. 
            # # 딕셔너리의 키값으로 접근
            record = (user_id, data['title'], data['datetime'], data['content']) 
            
            ### 4. 커서를 가져온다.
            cursor = connection.cursor() # 커서는 DB에 쿼리문을 실행시키는 역할을 한다.

            ### 5. 쿼리문을, 커서로 실행한다.
            cursor.execute(query, record) # 쿼리문과, 쿼리에 매칭되는 변수를 넣어준다.

            ### 6. 커밋 해줘야, DB에 실제 반영한다.
            connection.commit() 

            ### 7. 자원 해제
            cursor.close()
            connection.close()

        except Error as e:          
            print(e)
            cursor.close()
            connection.close()

            return {"result": "fail", "error" : str(e)}, 500


        # API 를 끝낼때는
        # 클라이언트에 보내줄 정보(json)와 http상태코드를
        # 리턴한다(보내준다)
        return {"result": "success" }, 200

    # get 메소드를 처리하는 함수를 만든다.
    # 내가만든 메모만 가져온다.
    @jwt_required()
    def get(self):
        # 1. 클라이언트로부터 데이터를 받아온다.
        # 없다.
        user_id = get_jwt_identity() # 유저 id 토큰 정보를 받아준다. # 복호화하는 함수
        # 클라이언트에서 쿼리스트링으로 보내는 데이터는
        # request.args.get('키값', '기본값') 으로 받아온다.
        # 키값은 쿼리 스트링과 같아야한다.

        # 헤드에서 가져오는것 {{url}}/follow/memo?offset=0&limit=5
        offset = request.args.get('offset') # page가 없으면 1을 가져온다.
        limit = request.args.get('limit') # limit가 없으면 3을 가져온다.
        # 2. db에 저장된 데이터를 가져온다.
        try :
            ### 3 . DB 연결
            # mysql_connection.py 에서 만든 함수를 호출
            connection = get_connection()

            ### 4. 쿼리문 만들기
            query = '''
                    SELECT id, title, datetime, content, createdAt, updatedAt
                    FROM memo
                    where userId = %s
                    order by datetime desc
                    limit ''' + offset + ''', ''' + limit + ''';
                    '''
                     # %s 는 = 기호가 있을때만 사용하는것.
            record = (user_id, )

            ## 중요 : select 문은!!!!!!
            ## 커서 가져올때, dictionary = True 로 해준다.
            ### 5. 커서를 가져온다.
            cursor = connection.cursor(dictionary=True)

            ### 6. 쿼리문을, 커서로 실행한다.
            cursor.execute(query, record)

            ### 7. 결과를 가져온다.
            result_list = cursor.fetchall()
            
            print(result_list)

            # 중요! 디비에서 가져온 timestamp 는
            # 파이썬에서 datetime 으로 자동 변환된다.
            # 그래서, json 으로 변환해서 클라이언트한테 보내야하는데 에러가난다.
            # 따라서, 시간을 문자열로 변환해서 보내준다.
           
            
            i = 0
            for row in result_list :
                result_list[i]['datetime'] = row['datetime'].isoformat()
                result_list[i]['createdAt'] = row['createdAt'].isoformat()
                result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
                i += 1

            ### 8. 자원 해제
            cursor.close()
            connection.close()

        except Error as e:          
            print(e)
            cursor.close()
            connection.close()

            return {"result": "fail", "error" : str(e)}, 500

 # 2. DB에서 가져온 레시피 정보를 클라이언트에 보낸다.
        return {"result": "success", 
            'items' : result_list, # 리스트를 보내준다.
            'count' : len(result_list) }, 200 # 리스트의 길이를 보내준다.

class MemoResource(Resource) : # 상속 # 메모를 수정 삭제하는 api


    @jwt_required() # 토큰이 필요함
    def put(self, memo_id) : # 수정
       
        data = request.get_json() 

        user_id = get_jwt_identity() # 토큰에 있는 유저아이디를 가져옴
        # 토큰에서 가져온 user_id를 쿼리문과 record에 추가함

        # 2. 클라이언트로부터 받은 데이터를 디비에 업데이트한다.
        # {
        #     "title": "마이크의 타이틀임1234",
        #     "datetime": "2024-01-11 15",
        #     "content": "마이크 콘텐츠1234"
        # }

        try :
            connection = get_connection()

            query = '''
                update memo
                set
                title = %s,
                datetime = %s,
                content = %s
                where id = %s and userId = %s; '''   # %s 는 변수처리 할것임 # 
            
            
            record = (data['title'], data['datetime'], data['content'], memo_id, user_id) # 튜플로 만들어줘야함
            
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
    def delete(self, memo_id) : # 삭제 

        user_id = get_jwt_identity() 

        try :
            connection = get_connection()

            query = '''
                delete from memo
                where id = %s and userId = %s; '''  
            
            record = (memo_id, user_id) 
            
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

class FollowMemoListResource(Resource): # 내 친구의 메모를 가져오기

    @jwt_required()
    def get(self) : # 친구의 메모를 가져온다.
        
        user_id = get_jwt_identity() # 토큰에서 유저아이디를 가져온다.
        offset = request.args.get('offset') 
        limit = request.args.get('limit')

        
        try :
            connection = get_connection()

            query = '''
                select u.nickname, m.title, m.datetime, m.content, m.createdAt, f.followeeId, m.Id as memoId
                from follow f
                join user u
                on f.followeeId = u.id
                join memo m
                on m.userId = f.followeeId
                where f.followerId = %s
                order by m.datetime desc
                limit '''+ offset + ''',''' + limit + ''' ;'''
            
            record = (user_id, ) 
            
            cursor = connection.cursor(dictionary=True) 

            cursor.execute(query, record) 

            result_list = cursor.fetchall() 

            i = 0
            for row in result_list :
                result_list[i]['datetime'] = row['datetime'].isoformat()
                result_list[i]['createdAt'] = row['createdAt'].isoformat()
                i += 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"result": "fail", "error" : str(e)}, 500

        # 3. 가져온 메모를 클라이언트에 보낸다.
        return {"result": "success",
                'items' : result_list, # 리스트를 보내준다.
                'count' : len(result_list) }, 200 # 리스트의 길이를 보내준다.


