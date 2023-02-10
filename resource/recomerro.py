from flask import request # 클라이언트가 보낸 데이터를 받기 위한 라이브러리
from flask_restful import Resource # API를 만들기 위한 라이브러리
from mysql.connector import Error # DB에 연결할 때, 에러가 발생할 수 있으므로, 에러처리를 위한 라이브러리
from flask_jwt_extended import jwt_required, get_jwt_identity # JWT를 사용하기 위한 라이브러리

from mysql_connection import get_connection # DB에 연결하기 위한 함수
import pandas as pd



class MovieRecommendResource(Resource) : # 영화 추천 APi

    @jwt_required()
    def get(self) : 

        # 1. 클라이언트로부터 데이터를 받아온다.
        user_id = get_jwt_identity()

        # 2. 추천을 위한, 상관계수 데이터프레임을 읽어온다.
        movie_correlations = pd.read_csv('data/movie_correlations.csv', index_col='title')
        print(movie_correlations)


        
        # -현재 : 추천영화 10개씩 가져오게 개발되었다.
        # -업데이트 : 추천영화를 클라이언트에서 셋팅할 수 있께 
        # 	예 ) 7개보내라, 10개 보내라, 5개 보내라.

        # API를 수정하시오!! (API 설계변경 및 코드 수정)
        # order 를 추가하면될듯
        count = int(request.args.get('count'))   # 쿼리스트링으로 받는 데이터는, 전부 문자열로 처리된다!!

        # 3. 이 유저의 별점 정보를 가져온다. => DB에서 가져온다
        try :
            connection = get_connection()

            query = '''   
                select m.title, r.rating
                from rating r 
                join movie m
                on r.movie_id = m.id
                where r.user_id = %s; '''

            record = (user_id,)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

           
            result_list
            print(result_list)

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500

        # 4. db로부터 가져온 이 유저가 본 영화의 제목과 별점을 데이터프레임으로 만든다.
        my_rating = pd.DataFrame(data = result_list)

        # 5. 내 별점정보 기반으로, 추천 영화 목록을 만든다.

        similar_movies_list = pd.DataFrame()

        for i in range( my_rating.shape[0] ) : 
            movie_title = my_rating['title'][i] 
            recom_movies = movie_correlations[movie_title].dropna().sort_values(ascending=False).to_frame()
            recom_movies.columns = ['Correlation']
            recom_movies['Weight'] = my_rating["rating"][i] * recom_movies['Correlation']
            similar_movies_list  = similar_movies_list.append( recom_movies ) 

        # 6. 내가 본 영화 제거

        drop_index_list = my_rating["title"].to_list()

        for name in drop_index_list :
            if name in similar_movies_list.index :
                similar_movies_list.drop(name, axis = 0, inplace=True )

        # 7. 중복 추천된 영화는, Weight 가 가장 큰 값으로만 
        #    유지하고, 나머지는 삭제한다.
        print("count",type(count)) # 따옴표를 띄고 찍는다 때문에 type(count)
        recomm_movie_list = similar_movies_list.groupby('title')['Weight'].max().sort_values(ascending=False).head(count)

        
        # 추천결과가 음수인것도 나올수가 있다 = > 수정 !! (세이프코딩)
        recomm_movie_list = recomm_movie_list[recomm_movie_list.values.astype('float64')>0]
        print(recomm_movie_list)
        

        # 8. JSON 으로 클라이언트에 보내야 한다.
        recomm_movie_list = recomm_movie_list.to_frame()
        recomm_movie_list = recomm_movie_list.reset_index()
        recomm_movie_list = recomm_movie_list.to_dict('records')
        
        return {'result' : recomm_movie_list, 'count' : len(recomm_movie_list)}, 200    

# 실시간으로 추천하는 API
# 상관계수 테이블이 최신화 대신 느림
class MovieRecommendRealTimeResource(Resource) :  

    @jwt_required()
    def get(self) :

        user_id = get_jwt_identity()

        count = int(request.args.get('count'))
        
        try :
            connection = get_connection()

            query = '''
                    select m.title, r.user_id , r.rating
                    from movie m
                    left join rating r
                    on m.id = r.movie_id; '''
                    
            cursor = connection.cursor(dictionary=True)

            cursor.execute(query)

            result_list = cursor.fetchall()
          
            print(111111111111111111111111111)
            df = pd.DataFrame(data=result_list)
            df.pivot_table(index='user_id', columns='title', values='rating')
            print(22222222222222222222222222222)
            movie_correlations = df.corr(min_periods=50)
            print(333333333333333333333333333333)
            # 내 별점정보를 가져와야, 나의 맞춤형 추천 가능
            query = '''   
                select m.title, r.rating
                from rating r 
                join movie m
                on r.movie_id = m.id
                where r.user_id = %s; '''

            record = (user_id,)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500

        my_rating = pd.DataFrame(data = result_list)
       
        print(444444444444444444444444444444444444)
        # 5. 내 별점정보 기반으로, 추천 영화 목록을 만든다.

        similar_movies_list = pd.DataFrame()
        print(555555555555555555555555555555)
        for i in range( my_rating.shape[0] ) : 
            movie_title = my_rating['title'][i] 
            recom_movies = movie_correlations[movie_title].dropna().sort_values(ascending=False).to_frame()
            recom_movies.columns = ['Correlation']
            recom_movies['Weight'] = my_rating["rating"][i] * recom_movies['Correlation']
            similar_movies_list  = similar_movies_list.append( recom_movies ) 
        print(666666666666666666666666666666666)
        # 6. 내가 본 영화 제거

        drop_index_list = my_rating["title"].to_list()
        print(77777777777777777777777777777777)
        for name in drop_index_list :
            if name in similar_movies_list.index :
                similar_movies_list.drop(name, axis = 0, inplace=True )
        print(8888888888888888888888888888)
        # 7. 중복 추천된 영화는, Weight 가 가장 큰 값으로만 
        #    유지하고, 나머지는 삭제한다.
        print("count",type(count)) # 따옴표를 띄고 찍는다 때문에 type(count)
        recomm_movie_list = similar_movies_list.groupby('title')['Weight'].max().sort_values(ascending=False).head(count)

        
        # 추천결과가 음수인것도 나올수가 있다 = > 수정 !! (세이프코딩)
        recomm_movie_list = recomm_movie_list[recomm_movie_list.values.astype('float64')>0]
        print(recomm_movie_list)
        

        # 8. JSON 으로 클라이언트에 보내야 한다.
        recomm_movie_list = recomm_movie_list.to_frame()
        recomm_movie_list = recomm_movie_list.reset_index()
        recomm_movie_list = recomm_movie_list.to_dict('records')
        
        return {'result' : recomm_movie_list, 'count' : len(recomm_movie_list)}, 200    