# NSG Backend Template (FastAPI + Scikit-learn)

**No-So-Gong 팀 프로젝트**의 백엔드 개발을 위한 FastAPI 템플릿입니다.

## 📦 로컬 개발 가이드

### 1. 가상환경 세팅
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 실행
```bash
uvicorn app.main:app --host 0.0.0.0 --reload # 자동으로 8000 포트
```
> 💡 --reload는 코드 변경 시 자동으로 서버를 재시작해줍니다.
정상 실행 시 아래 메시지가 표시됩니다:

```bash
Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

- http://127.0.0.1:8000 → 기본 루트 경로
- http://127.0.0.1:8000/docs → Swagger API 문서 확인 (자동 생성됨)

### 4. 환경 변수 설정
`.env` 파일을 프로젝트 루트에 생성하고, `.env.example` 파일을 참고하여 작성합니다.
```bash
# 예시
MODEL_PATH=./model/emotion_model.pkl
```

### 5. 머신러닝 모델 파일 준비
`/model/emotion_model.pkl` 파일을 프로젝트 루트의 `model/` 디렉토리에 위치시킵니다.

## 🔁 requirements.txt 업데이트 방법
새로운 라이브러리를 설치한 후 아래 명령어로 의존성 파일을 업데이트하세요:

```bash
pip freeze > requirements.txt
```

> 팀원들과 동일한 실행 환경을 유지하기 위함입니다.

## 📁 프로젝트 디렉토리 구조

```
nsg-backend-template/
├── create_tables.py              # 테이블을 DB에 실제로 생성하는 스크립트
├── test_connection.py             # PostgreSQL 연동 확인 테스트
app/
├── api/                            # 각 기능별 API 라우터, 서비스, 스키마 모듈
│   ├── care/                       # '케어' 도메인: 감정 예측 등 동물 관리 기능
│   │   ├── controller.py          # 케어 관련 라우터 정의 (FastAPI @router)
│   │   ├── schema.py              # 케어 기능용 요청/응답 Pydantic 모델 정의
│   │   ├── service.py             # 케어 서비스 로직 처리 (비즈니스 로직)
│   │   └── __init__.py            # 모듈 임포트를 위한 초기화 파일
│   ├── pet/                       # '반려동물' 도메인: 동물 정보 기능
│   │   ├── controller.py          # 반려동물 관련 API 라우터
│   │   ├── schema.py              # 반려동물 요청/응답 데이터 구조
│   │   ├── service.py             # 반려동물 관련 로직 처리
│   │   └── __init__.py            # 모듈 초기화용
│   ├── user/                      # '유저' 도메인: 사용자 관리 기능 (예: 인증, 정보)
│   │   ├── controller.py          # 유저 관련 API 라우터
│   │   ├── schema.py              # 유저 요청/응답 데이터 구조
│   │   └── __init__.py            # 모듈 초기화용
│   └── __init__.py                # api 패키지 초기화
├── core/                          # 공통 유틸리티 및 시스템 설정
│   ├── config.py                  # 환경변수 로딩 및 설정값 정의
│   ├── database.py                # DB 연결 및 세션 생성 설정 (SQLAlchemy)
│   └── exceptions.py              # 커스텀 예외 및 예외 처리 핸들러 정의
├── models/                        # SQLAlchemy ORM 모델 정의
│   ├── __init__.py                # 모든 모델을 import하는 초기화 파일
│   ├── animal.py                  # 동물(Animal) 테이블 정의
│   └── user.py                    # 사용자(User) 테이블 정의
├── main.py                        # FastAPI 앱 진입점 (라우터 등록, 실행 등)
ML/
└── emotion_model.pkl             # 학습된 감정 예측 머신러닝 모델 (피클 파일)

```

## PostgreSQL 연동(진행중)

```bash
pip install sqlalchemy

pip install asyncpg

pip install databases
```
