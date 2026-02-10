# No-So-Gong (NSG) Backend

ML 기반 감정 예측 시스템을 활용한 동물 육성 시뮬레이션 게임 백엔드 서비스

## 목차

- [팀원 소개](#팀원-소개)
- [프로젝트 소개](#프로젝트-소개)
- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [게임 흐름](#게임-흐름-architecture)
- [API 개요](#api-개요)
- [시작하기](#시작하기)
- [환경 설정](#환경-설정)
- [프로젝트 구조](#프로젝트-구조)
- [테스트](#테스트)

## 팀원 소개

| Chaehyunlim | DooYee | kimtaeyeon04 |
|:---:|:---:|:---:|
| <img src="https://github.com/Chaehyunli.png" width="120" height="120"> | <img src="https://github.com/DOOYEE0709.png" width="120" height="120"> | <img src="https://github.com/kimtaeyeon04.png" width="120" height="120"> |
| [@Chaehyunli](https://github.com/Chaehyunli) | [@DOOYEE0709](https://github.com/DOOYEE0709) | [@kimtaeyeon04](https://github.com/kimtaeyeon04) |

## 프로젝트 소개

**No-So-Gong (노소공)** 팀의 육성 시뮬레이션 게임 **'노답 삼형제! 이걸 키우라고?'** 의 백엔드 서비스입니다. 세 마리 동물(시바견, 오리, 병아리)을 케어하며 모두 행복도 100을 달성하는 것을 목표로 합니다.

단순한 수치 증감이 아닌, **XGBoost 기반 ML 모델**이 사용자의 행동 패턴을 분석하여 동물의 감정 변화량을 실시간으로 예측합니다. 또한 **편애도(User Pattern Bias) 시스템**을 통해 특정 동물만 집중 케어할 경우 다른 동물의 케어 난이도가 상승하는 전략적 요소를 제공합니다.

## 주요 기능

### ML 기반 감정 예측 시스템

학습된 ML 모델(`emotion_model.pkl`)이 16개의 피처를 입력받아 감정 변화량(predictedDelta)을 예측합니다.

**ML 모델 입력 피처:**

| 구분 | 피처 | 설명 |
|------|------|------|
| 상태 | `current_emotion` | 현재 감정 수치 (0~100) |
| 상태 | `action_count` | 오늘 같은 카테고리 행동 횟수 |
| 상태 | `user_pattern_bias` | 편애도 (0.00~1.00) |
| 상태 | `days_since_last_care` | 마지막 케어 이후 경과 일수 |
| OneHot | `animal_type_*` | 동물 종류 (shiba / duck / chick) |
| OneHot | `action_*` | 행동 종류 (feed1~3 / play1~3 / gift1~3) |

**예측 결과 적용:**
- 양수 delta: `ceil()` 처리, 음수 delta: `floor()` 처리
- 감정 수치는 `[0, 100]` 범위로 클램핑
- 감정이 0 이하로 떨어지면 자동 가출 처리

### 편애도(User Pattern Bias) 시스템

세 동물 간의 케어 균형을 추적하는 핵심 메커니즘입니다. 초기값은 각 동물 `0.33`으로 균등 배분됩니다.

**전이 알고리즘:**
```
Target 동물에게 행동 수행 시:
  - 다른 동물의 편애도 30%가 Target에게 전이
  - transfer = other_bias * 0.3
  - new_target_bias = target_bias + sum(transfers)
  - new_other_bias = other_bias * 0.7
```

편애도가 높은 동물일수록 ML 모델의 감정 변화 예측에 영향을 미치며, 한 동물만 집중 케어할 경우 나머지 동물의 감정 관리가 어려워집니다.

### 진화 시스템

감정 수치에 따라 3단계로 진화하며, 단계별로 사용 가능한 행동과 가격이 달라집니다.

| 진화 단계 | 감정 조건 | 행동 가격 범위 |
|-----------|-----------|---------------|
| Stage 1 | 0 ~ 69 | 30 ~ 50 |
| Stage 2 | 70 ~ 89 | 50 ~ 70 |
| Stage 3 | 90 ~ 100 | 80 ~ 100 |

### 케어(Care) 시스템

3개 카테고리 x 3개 레벨 x 3개 진화 단계 = 총 **27개 행동**이 존재합니다.

| 카테고리 | Level 1 | Level 2 | Level 3 |
|----------|---------|---------|---------|
| 놀아주기 (play) | 산책가기 | 공놀이 | 애견카페 |
| 밥주기 (feed) | 시장사료 | 마트사료 | 유기농사료 |
| 선물하기 (gift) | 장난감 | 예쁜옷 | 유모차 |

### 재화 시스템

| 획득 수단 | 보상 |
|-----------|------|
| 출석 체크 | 30~40원 (7일 주기 순환) |
| 생일 리워드 | 100원 (동물별 연 1회/일) |
| 미니게임 - 똥피하기 | 점수당 2원 |
| 미니게임 - Snake | 점수당 1원 |
| 미니게임 - 테트리스 | 점수당 1원 |

미니게임은 게임당 **하루 최대 3회** 플레이 가능합니다.

### 가출 및 복귀

- 감정이 **0 이하**로 떨어지면 동물이 가출 상태로 전환
- 가출 상태에서는 케어 행동 수행 불가
- **100원**을 소모하여 데려오기 가능 (감정 20으로 초기화)

## 기술 스택

### Backend
- **Python 3.x**
- **FastAPI** - 비동기 웹 프레임워크
- **SQLAlchemy** - ORM
- **Pydantic** - 데이터 검증

### Database
- **PostgreSQL** - 메인 데이터베이스
- **Alembic** - 데이터베이스 마이그레이션

### Machine Learning
- **XGBoost** - 감정 변화량 예측 모델
- **scikit-learn** - 데이터 분할 및 모델 평가
- **pandas** - 데이터 전처리
- **joblib** - 모델 직렬화/로드

### Testing
- **pytest** - 테스트 프레임워크
- **httpx** - 비동기 HTTP 테스트 클라이언트

### Documentation
- **Swagger/OpenAPI** - API 문서 자동화 (`/docs`)

## 게임 흐름 (Architecture)

### 전체 게임 플로우

```mermaid
flowchart TD
    A[유저 생성 - UUID 발급] --> B[동물 3마리 닉네임 설정]
    B --> D[출석 체크]
    B --> E[미니게임]
    B --> F[생일 리워드]
    D --> C[재화 획득]
    E --> C
    F --> C
    C --> G[케어 행동 수행]
    G --> H[ML 모델 감정 예측]
    H --> I{감정 수치 판정}
    I -->|"감정 > 0"| J[감정 & 진화 단계 업데이트]
    I -->|"감정 <= 0"| K[가출 처리]
    J --> L[편애도 재계산]
    K --> M[재화 소모하여 복귀]
    M --> G
    L --> N{전체 동물 행복도 100?}
    N -->|No| D
    N -->|Yes| O[게임 클리어 - 엔딩 요약]
    O --> P[초기화 후 재시작 가능]
```

### ML 감정 예측 파이프라인

```mermaid
flowchart LR
    A[행동 요청] --> B[Feature Engineering]
    B --> C["ML Input 생성<br/>(16 features)"]
    C --> D[emotion_model.pkl<br/>predict]
    D --> E[predictedDelta]
    E --> F["감정 적용<br/>ceil/floor + clamp"]
    F --> G[진화 단계 갱신]
    G --> H[편애도 전이]
    H --> I[ActionLog 기록]
```

### 트랜잭션 관리 흐름

```mermaid
flowchart TD
    subgraph "재화 획득 (IN)"
        A1[출석 체크]
        A2[미니게임 결과]
        A3[생일 리워드]
    end
    subgraph "재화 소모 (OUT)"
        B1[케어 행동]
        B2[가출 복귀 - 100원]
    end
    A1 --> T[MoneyTransaction]
    A2 --> T
    A3 --> T
    B1 --> T
    B2 --> T
    T --> U[User.money 갱신]
    T --> L["트랜잭션 로그<br/>(txId, source, amount, direction)"]
```

## API 개요

사용자 식별은 **UUID 기반 비로그인 인증 체계**를 사용하며, `user-id` 헤더를 통해 전달합니다.

### Users (`/api/v1/users`)

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/start` | 유저 생성 (UUID 발급, 초기 재화 0) |
| GET | `/property` | 현재 잔액 조회 |
| POST | `/transactions` | 트랜잭션 생성 (입금/출금) |

### Pets (`/api/v1/pets`)

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/nickname` | 동물 3마리 닉네임 등록 및 생성 |
| GET | `/{animalId}` | 동물 상세 정보 조회 (감정, 진화, 편애도) |
| POST | `/{animalId}/runaway` | 가출 처리 (감정 0 필요) |
| POST | `/{animalId}/return` | 복귀 처리 (100원 소모, 감정 20 초기화) |

### Cares (`/api/v1/cares`)

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/action` | ML 기반 케어 행동 수행 및 감정 예측 |
| GET | `/pricelist` | 카테고리별 행동 가격 조회 (진화 단계 반영) |
| POST | `/batch/daily-increment` | 일괄 `daySinceLastCare` 증가 (배치) |
| POST | `/emotion-message` | 감정 변화량 기반 반응 메시지 생성 |

### Events (`/api/v1/events`)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/attendance` | 출석 현황 조회 (7일 보드) |
| POST | `/attendance/checkin` | 출석 체크 (중복 방지, 보상 지급) |
| GET | `/birthday` | 오늘 생일인 동물 조회 |
| POST | `/birthday/reward` | 생일 보상 지급 (100원, 중복 방지) |

### Minigames (`/api/v1/minigames`)

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/{gameId}/start` | 미니게임 시작 (일일 3회 제한 확인) |
| POST | `/{gameId}/result` | 미니게임 결과 저장 및 보상 지급 |

### Ending (`/api/v1/endings`)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/summary` | 게임 클리어 요약 (전체 동물 행복도 100 필요) |
| POST | `/reset` | 유저 및 관련 데이터 전체 초기화 |

## 시작하기

### 필수 요구사항

- Python 3.x 이상
- PostgreSQL 13 이상
- ML 모델 파일 (`emotion_model.pkl`)

### 설치 및 실행

1. **저장소 클론**
```bash
git clone <repository-url>
cd nsg-backend
```

2. **가상환경 세팅**
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

3. **패키지 설치**
```bash
pip install -r requirements.txt
```

4. **데이터베이스 생성**
```bash
# pgAdmin4 또는 psql에서 실행
CREATE DATABASE nosogong_db;
```

5. **테이블 생성 및 초기 데이터 삽입**
```bash
python create_tables.py
```

6. **애플리케이션 실행**
```bash
uvicorn app.main:app --host 0.0.0.0 --reload
```

애플리케이션은 기본적으로 `http://localhost:8000`에서 실행됩니다.

- `http://127.0.0.1:8000` - 기본 루트 경로
- `http://127.0.0.1:8000/docs` - Swagger API 문서

## 환경 설정

### 필수 환경 변수

`.env` 파일을 프로젝트 루트에 생성하고, `.env.example`을 참고하여 작성합니다.

```properties
# Database
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/nosogong_db

# ML Model
MODEL_PATH=./ML/emotion_model.pkl

# Timezone
TIMEZONE=Asia/Seoul
```

## 프로젝트 구조

```
nsg-backend/
├── app/
│   ├── main.py                        # FastAPI 앱 진입점 (라우터 등록)
│   ├── api/                           # 도메인별 API 모듈
│   │   ├── care/                      # 케어 도메인: ML 감정 예측 & 행동 처리
│   │   │   ├── controller.py          # 케어 API 라우터
│   │   │   ├── service.py             # 감정 예측, 편애도 계산 비즈니스 로직
│   │   │   ├── repository.py          # 케어 관련 DB 접근 계층
│   │   │   └── schema.py             # 요청/응답 Pydantic 스키마
│   │   ├── pet/                       # 동물 도메인: 정보 조회, 가출/복귀
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── schema.py
│   │   ├── user/                      # 유저 도메인: 생성, 잔액, 트랜잭션
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── schema.py
│   │   ├── event/                     # 이벤트 도메인: 출석, 생일 리워드
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── schema.py
│   │   ├── ending/                    # 엔딩 도메인: 게임 요약, 초기화
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── schema.py
│   │   └── minigame/                  # 미니게임 도메인: 시작/결과 처리
│   │       ├── controller.py
│   │       ├── service.py
│   │       ├── repository.py
│   │       └── schema.py
│   ├── core/                          # 공통 설정
│   │   ├── config.py                  # 환경변수 로딩 (timezone 등)
│   │   ├── database.py                # SQLAlchemy 엔진 & 세션 설정
│   │   └── exception.py               # 커스텀 예외 핸들러
│   ├── models/                        # SQLAlchemy ORM 모델 (12 테이블)
│   │   ├── user.py                    # Users 테이블
│   │   ├── animal.py                  # Animals 테이블
│   │   ├── action.py                  # Actions 테이블 (27개 행동)
│   │   ├── action_log.py             # ActionLog 테이블 (케어 기록)
│   │   ├── category.py               # Categories 테이블
│   │   ├── emotionmessages.py        # EmotionMessages 테이블
│   │   ├── moneyTransaction.py       # MoneyTransaction 테이블
│   │   ├── attendance.py             # AttendanceReward & AttendanceLog
│   │   ├── birthday.py              # BirthdayReward 테이블
│   │   ├── minigames.py             # Minigame 테이블
│   │   ├── minigameattempts.py      # MinigameAttempt 테이블
│   │   └── userminigameplays.py     # UserMinigamePlay 테이블
│   └── tests/                         # pytest 테스트 코드
│       ├── conftest.py               # 테스트 픽스처 (DB 세션, TestClient)
│       ├── care/
│       ├── pet/
│       ├── user/
│       ├── event/
│       ├── ending/
│       └── minigame/
├── ML/
│   └── emotion_model.pkl             # 학습된 감정 예측 ML 모델
├── alembic/                           # DB 마이그레이션
├── create_tables.py                   # 테이블 생성 & 초기 데이터 삽입
├── requirements.txt                   # Python 의존성
└── .env.example                       # 환경 변수 예시
```

## 테스트

```bash
# 전체 테스트 실행
pytest

# 특정 도메인 테스트 실행
pytest app/tests/care/
pytest app/tests/pet/
pytest app/tests/user/
```

테스트는 함수 단위 트랜잭션 롤백 방식으로 격리되며, ML 모델은 `monkeypatch`를 통해 모킹됩니다.

## DB 스키마 (ER 다이어그램)

```mermaid
erDiagram
    Users ||--o{ Animals : owns
    Users ||--o{ MoneyTransaction : has
    Users ||--o{ AttendanceLog : records
    Users ||--o{ BirthdayReward : receives
    Users ||--o{ ActionLog : performs
    Users ||--o{ UserMinigamePlay : plays
    Users ||--o{ MinigameAttempt : attempts

    Animals ||--o{ ActionLog : receives_care
    Animals ||--o{ BirthdayReward : has_birthday

    Actions ||--o{ ActionLog : logged_in
    Actions }o--|| Categories : belongs_to
    Categories ||--o{ EmotionMessages : has

    Minigame ||--o{ MinigameAttempt : attempted
    Minigame ||--o{ UserMinigamePlay : tracked

    Users {
        UUID userId PK
        DateTime createdAt
        int money
    }
    Animals {
        int animalId PK
        UUID userId PK
        string name
        bool isRunaway
        int runawayCount
        int evolutionStage
        numeric currentEmotion
        date birthday
        numeric userPatternBias
        int daySinceLastCare
    }
    ActionLog {
        int logId PK
        numeric emotionBefore
        numeric emotionAfter
        numeric predictedDelta
        numeric actualDelta
        numeric userPatternBias
    }
    MoneyTransaction {
        string txId PK
        string source
        int amount
        enum direction
        int currentMoney
    }
```

---

**No-So-Gong** - ML 기반 감정 예측으로 동물과 교감하는 육성 시뮬레이션
