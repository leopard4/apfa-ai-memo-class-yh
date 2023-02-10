class Config :
    HOST = "yh-db.cipgkgybgqkj.ap-northeast-2.rds.amazonaws.com"
    DATABASE = 'memo_DB'
    DB_USER = 'memo_user'
    DB_PASSWORD = 'yh1234db'
    SALT = 'dkanfjgrpsk' 

    # JWT 관련 변수 셋팅
    JWT_SECRET_KEY = 'yhacdemy' # JWT 토큰을 만들때 사용하는 비밀키 # 관리할 문자열
    JWT_ACCESS_TOKEN_EXPIRES = False # False 가아니고 만약, 60 * 60 * 24 # JWT 토큰의 유효기간 # 1일
    PROPAGATE_EXCEPTIONS = True # JWT 관련 에러를 발생시키는지 여부
