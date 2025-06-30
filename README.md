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
uvicorn app.main:app --reload # 자동으로 8000 포트
```
> 💡 --reload는 코드 변경 시 자동으로 서버를 재시작해줍니다.
정상 실행 시 아래 메시지가 표시됩니다:

```bash
Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
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
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── core/                # (예정) 설정, 공통 유틸 등 핵심 구성요소
│   ├── routers/             # API 엔드포인트 라우터
│   │   └── predict.py       # 예시용 엔드포인트 (테스트용)
│   ├── schemas/             # Pydantic 기반 요청/응답 스키마 정의
│   │   └── input.py         # 예시용 입력 스키마 (테스트용)
│   └── services/            # 비즈니스 로직, 모델 로딩/예측 등 처리
│       └── predictor.py     # 예시용 예측 로직 구현 (테스트용)
│
├── model/                   # 학습된 머신러닝 모델 저장 위치
│   └── emotion_model.pkl    # (.gitignore에 의해 Git 추적 제외)
│
├── venv/                    # 가상환경 (.gitignore에 의해 Git 추적 제외)
├── .env                     # 환경 변수 파일 (.gitignore에 의해 Git 추적 제외)
├── .env.example             # 환경 변수 예시 파일
├── .gitignore               # Git 추적 제외 설정
├── requirements.txt         # 프로젝트 의존성 정의
└── README.md                # 프로젝트 설명 문서
```
