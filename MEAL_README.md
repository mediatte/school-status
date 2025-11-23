# 🍽️ 급식 기능 가이드

NEIS(나이스) 오픈API를 활용한 학교 급식 정보 조회 기능입니다.

참고: [alvin0319/NeisAPI](https://github.com/alvin0319/NeisAPI)

## ✨ 주요 기능

- ✅ **학교 검색**: NEIS에 등록된 전국 학교 검색
- ✅ **급식 조회**: 조식, 중식, 석식 정보
- ✅ **주간 급식**: 월~금요일 급식 정보
- ✅ **상세 정보**: 메뉴, 칼로리, 원산지 정보
- ✅ **실시간 연동**: NEIS 오픈API 직접 연동

## 🚀 사용 방법

### Streamlit 앱에서 사용

1. 학교명 검색
2. "🍽️ 급식 불러오기" 버튼 클릭
3. "급식" 탭에서 요일별 급식 확인

### Python 코드로 사용

```python
from neis_meal import NeisAPI, search_school_by_name, get_today_meal_simple

# 1. 학교 검색
schools = search_school_by_name("고운고등학교")

for school in schools:
    print(f"학교명: {school['SCHUL_NM']}")
    print(f"주소: {school['ORG_RDNMA']}")
    print(f"학교코드: {school['SD_SCHUL_CODE']}")
    print(f"교육청코드: {school['ATPT_OFCDC_SC_CODE']}")

# 2. 오늘의 급식 조회
today_meal = get_today_meal_simple("고운고등학교")

if "error" not in today_meal:
    print(f"학교: {today_meal['school']['SCHUL_NM']}")
    print(f"날짜: {today_meal['date']}")
    
    meals = today_meal.get("meals", {})
    for meal_type, meal_info in meals.items():
        meal_name = {"breakfast": "조식", "lunch": "중식", "dinner": "석식"}
        print(f"\n[{meal_name.get(meal_type)}]")
        print(meal_info.get("menu"))
        print(f"칼로리: {meal_info.get('calories')}")
```

## 📚 API 사용 예시

### 학교 검색

```python
from neis_meal import NeisAPI

neis = NeisAPI()
schools = neis.search_school("고운고등학교")

# 여러 학교가 검색될 수 있음
for school in schools:
    print(school['SCHUL_NM'])  # 학교명
    print(school['LCTN_SC_NM'])  # 지역
```

### 월간 급식 조회

```python
from neis_meal import NeisAPI

neis = NeisAPI()

# 학교 정보
school_code = "학교코드"
atpt_code = "교육청코드"

# 2025년 11월 전체 급식
meals = neis.get_meal(school_code, atpt_code, 2025, 11)

for day, day_meals in meals.items():
    print(f"\n{day}일:")
    
    if "lunch" in day_meals:
        print(f"중식: {day_meals['lunch']['menu']}")
```

### 오늘의 급식 조회

```python
from neis_meal import NeisAPI

neis = NeisAPI()

# 학교 정보
school_code = "학교코드"
atpt_code = "교육청코드"

# 오늘의 급식
today_meals = neis.get_today_meal(school_code, atpt_code)

for meal_type, meal_info in today_meals.items():
    print(f"{meal_type}: {meal_info['menu']}")
```

### 이번 주 급식 조회

```python
from neis_meal import NeisAPI

neis = NeisAPI()

# 학교 정보
school_code = "학교코드"
atpt_code = "교육청코드"

# 이번 주 급식 (월~금)
week_meals = neis.get_week_meal(school_code, atpt_code)

for day_name, day_info in week_meals.items():
    print(f"\n{day_name}요일 ({day_info['date']}):")
    meals = day_info['meals']
    
    if "lunch" in meals:
        print(f"중식: {meals['lunch']['menu']}")
```

## 🔑 NEIS API 키 (선택사항)

기본적으로 API 키 없이 사용 가능하지만, 많은 요청을 하는 경우 API 키를 발급받는 것을 권장합니다.

### API 키 발급 방법

1. **NEIS 오픈API 포털 접속**
   - [https://open.neis.go.kr/](https://open.neis.go.kr/)

2. **회원가입 및 로그인**

3. **API 인증키 신청**
   - 마이페이지 → 인증키 신청
   - 용도 및 활용계획 작성
   - 승인 대기 (보통 1-2일)

4. **API 키 사용**

```python
from neis_meal import NeisAPI

# API 키로 초기화
api_key = "발급받은_API_키"
neis = NeisAPI(api_key)

# 이후 동일하게 사용
schools = neis.search_school("고운고등학교")
```

## 📊 응답 데이터 형식

### 학교 정보

```json
{
  "ATPT_OFCDC_SC_CODE": "교육청코드",
  "ATPT_OFCDC_SC_NM": "교육청명",
  "SD_SCHUL_CODE": "표준학교코드",
  "SCHUL_NM": "학교명",
  "ENG_SCHUL_NM": "영문학교명",
  "SCHUL_KND_SC_NM": "학교종류명",
  "LCTN_SC_NM": "소재지명",
  "JU_ORG_NM": "관할조직명",
  "FOND_SC_NM": "설립명",
  "ORG_RDNZC": "도로명우편번호",
  "ORG_RDNMA": "도로명주소",
  "ORG_RDNDA": "도로명상세주소"
}
```

### 급식 정보

```python
{
  1: {  # 날짜 (1일)
    "lunch": {  # 중식
      "menu": "쌀밥\n김치찌개\n불고기\n김치\n우유",
      "calories": "850.5 Kcal",
      "nutrition": "탄수화물(g) : 120.0 ...",
      "origin": "쌀:국내산\n돼지고기:국내산\n배추김치:국내산"
    },
    "dinner": {  # 석식
      "menu": "...",
      "calories": "...",
      "nutrition": "...",
      "origin": "..."
    }
  },
  2: {  # 2일
    ...
  }
}
```

### 이번 주 급식 정보

```python
{
  "월": {
    "date": "2025-11-24",
    "meals": {
      "lunch": {...},
      "dinner": {...}
    }
  },
  "화": {
    "date": "2025-11-25",
    "meals": {...}
  },
  ...
}
```

## 🎨 커스터마이징

### 급식 카드 스타일 변경

`streamlit_app.py`의 CSS 섹션에서 수정:

```python
.meal-card {
    background: white;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #ff6b6b;  # 색상 변경
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
```

### 급식 종류별 색상 변경

```python
meal_types = {
    "breakfast": ("🌅 조식", "#ffd93d"),  # 노란색
    "lunch": ("☀️ 중식", "#ff6b6b"),      # 빨간색
    "dinner": ("🌙 석식", "#6c5ce7")      # 보라색
}
```

## 🐛 문제 해결

### "학교를 찾을 수 없습니다"

- **원인**: NEIS에 등록되지 않은 학교 또는 네트워크 오류
- **해결**:
  - 정확한 학교명으로 검색
  - [NEIS 오픈API](https://open.neis.go.kr/)에서 학교 확인
  - 인터넷 연결 확인

### "급식 정보가 없습니다"

- **원인**: 해당 날짜에 급식이 없음 (주말, 방학 등)
- **해결**: 다른 날짜 시도

### API 오류 (HTTP 429 - Too Many Requests)

- **원인**: 너무 많은 요청
- **해결**:
  - API 키 발급받아 사용
  - 요청 간격 늘리기
  - 캐싱 활용

### "connection timeout" 오류

- **원인**: NEIS API 서버 응답 지연
- **해결**:
  - 잠시 후 다시 시도
  - timeout 값 증가

```python
# neis_meal.py에서 timeout 조정
response = requests.get(url, params=params, timeout=30)  # 30초로 증가
```

## 📖 NEIS 오픈API 상세 정보

### 학교기본정보

- **서비스명**: schoolInfo
- **설명**: 학교명, 주소, 전화번호 등 기본 정보

### 급식식단정보

- **서비스명**: mealServiceDietInfo
- **설명**: 학교 급식 식단, 원산지, 칼로리, 영양 정보
- **제공기간**: 최근 3개월 ~ 1년

### 주요 파라미터

| 파라미터 | 설명 | 예시 |
|---------|------|------|
| KEY | 인증키 | (발급받은 키) |
| Type | 데이터 형식 | json, xml |
| pIndex | 페이지 번호 | 1 |
| pSize | 페이지 크기 | 100 |
| ATPT_OFCDC_SC_CODE | 시도교육청코드 | B10 |
| SD_SCHUL_CODE | 표준학교코드 | 7091234 |
| MLSV_YMD | 급식일자 | 20251124 |
| MLSV_FROM_YMD | 급식시작일자 | 20251101 |
| MLSV_TO_YMD | 급식종료일자 | 20251130 |

## 💡 활용 예시

### 1. 급식 알림봇

```python
import schedule
from neis_meal import get_today_meal_simple

def send_meal_notification():
    meal = get_today_meal_simple("고운고등학교")
    # 카카오톡, 디스코드, 이메일 등으로 전송
    print(f"오늘의 중식: {meal['meals']['lunch']['menu']}")

# 매일 오전 8시에 실행
schedule.every().day.at("08:00").do(send_meal_notification)
```

### 2. 학급 전광판

Raspberry Pi + 디스플레이로 학급 전광판 구현

```python
from neis_meal import get_today_meal_simple
import tkinter as tk

def update_display():
    meal = get_today_meal_simple("학교명")
    # GUI 업데이트
```

### 3. 학교 홈페이지 연동

```python
from flask import Flask, jsonify
from neis_meal import get_week_meal

app = Flask(__name__)

@app.route('/api/meal/week')
def get_week_meal_api():
    meals = get_week_meal("학교코드", "교육청코드")
    return jsonify(meals)
```

## 🔗 관련 링크

- **NEIS 오픈API**: [https://open.neis.go.kr/](https://open.neis.go.kr/)
- **NeisAPI (Kotlin)**: [https://github.com/alvin0319/NeisAPI](https://github.com/alvin0319/NeisAPI)
- **pycomcigan**: [https://github.com/hegelty/pycomcigan](https://github.com/hegelty/pycomcigan)

## 📄 라이선스

MIT License

이 모듈은 NEIS 오픈API를 사용합니다. NEIS 오픈API 이용약관을 준수해야 합니다.

---

**만든 날짜**: 2025-11-23  
**버전**: 1.0.0  
**참고**: [alvin0319/NeisAPI](https://github.com/alvin0319/NeisAPI)

