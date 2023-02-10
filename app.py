from flask import Flask 
from flask_restful import Api
from flask_jwt_extended import JWTManager

from config import Config
from resource.follower import FollowResource
from resource.memo import FollowMemoListResource, MemoListResource, MemoResource
from resource.user import UserLoginResource, UserLogoutResource, UserRegisterResource, jwt_blocklist

app = Flask(__name__) 

app.config.from_object(Config) 

jwt = JWTManager(app)

api = Api(app) 

# 로그아웃된 토큰으로 요청하는 경우 처리하는 코드작성.
@jwt.token_in_blocklist_loader # 토큰이 만료되었는지 확인하는 함수를 등록한다.
def check_if_token_is_revoked(jwt_header, jwt_payload): # 토큰이 만료되었는지 확인하는 함수
    jti = jwt_payload['jti'] # jti는 JWT 토큰의 고유 식별자
    return jti in jwt_blocklist 


api.add_resource(UserRegisterResource, '/user/register') 
api.add_resource(UserLoginResource, '/user/login')
api.add_resource(UserLogoutResource, '/user/logout')

api.add_resource(MemoListResource, '/memos') 
api.add_resource(MemoResource, '/memos/<int:memo_id>') # 메모의 프라이마리키를 받아서, 해당 메모를 리턴해주는 엔드포인트
api.add_resource(FollowResource, '/follow/<int:followee_id>') 
api.add_resource(FollowMemoListResource, '/follow/memo')


if __name__ == '__main__': 
    app.run() 