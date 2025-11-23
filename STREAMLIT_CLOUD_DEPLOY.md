# 🚀 Streamlit Cloud 배포 가이드

## 📋 개요

이 앱은 다음과 같이 작동합니다:
1. 사용자가 학교명 입력
2. **서버에서 API로 데이터 자동 수집**:
   - 📚 시간표: pycomcigan API
   - 🍽️ 급식: NEIS 오픈 API
3. 실시간으로 화면에 표시

**별도의 API 키나 설정이 필요 없습니다!** ✨

---

## 🌐 Streamlit Cloud 배포 방법

### 1단계: Streamlit Cloud 접속

**URL**: https://share.streamlit.io

1. "Sign up with GitHub" 또는 "Sign in with GitHub" 클릭
2. GitHub 계정으로 로그인
3. Streamlit Cloud에 권한 부여

### 2단계: 앱 배포

1. **"New app"** 버튼 클릭

2. **배포 설정 입력**:
   ```
   Repository: mediatte/school-status
   Branch: main
   Main file path: streamlit_app.py
   ```

3. **"Advanced settings"** (선택사항):
   - Python version: 3.12 (자동 감지)
   - 특별한 설정 불필요

4. **"Deploy!"** 클릭

### 3단계: 배포 완료! 🎉

**배포 시간**: 약 1-2분

**앱 주소**: 
```
https://mediatte-school-status-streamlitapp-XXXXX.streamlit.app
```

**커스텀 URL 설정** (선택):
- Streamlit Cloud 설정에서 앱 이름 변경 가능
- 더 짧고 기억하기 쉬운 URL 사용 가능

---

## ✨ 사용 방법

### 시간표 확인

1. **학교 검색**
   - 사이드바에서 "🏫 학교명 검색"
   - "고운고등학교" 입력
   - 검색 결과에서 학교 선택

2. **학년/반 선택**
   - 학년 선택 (1-3)
   - 보기 모드 선택:
     - **개별 반**: 특정 반의 상세 시간표
     - **전체 학년**: 모든 반을 한눈에

3. **시간표 불러오기**
   - "📥 시간표 불러오기" 버튼 클릭
   - API에서 자동으로 데이터 수집
   - 요일별 탭에서 확인

### 급식 확인

1. 학교 선택 (위와 동일)

2. **급식 불러오기**
   - "🍽️ 급식 불러오기" 버튼 클릭
   - NEIS API에서 자동으로 데이터 수집

3. **급식 탭에서 확인**
   - 요일별로 조식/중식/석식 정보
   - 메뉴, 칼로리, 원산지 정보

---

## 🔄 자동 업데이트

GitHub 저장소에 코드를 푸시하면 **자동으로 Streamlit Cloud에 배포**됩니다!

```bash
git add .
git commit -m "Update app"
git push origin main
```

→ 몇 분 후 자동으로 업데이트 완료!

---

## 🎨 커스터마이징

### 색상 테마 변경

`.streamlit/config.toml` 파일 수정:

```toml
[theme]
primaryColor = "#667eea"        # 메인 색상
backgroundColor = "#ffffff"     # 배경색
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

### 자동 새로고침 간격 변경

`streamlit_app.py`에서 기본값 수정:

```python
refresh_interval = st.slider("새로고침 간격 (초)", 10, 300, 60)  # 기본 60초
```

---

## 🔧 API 상세 정보

### 1. pycomcigan API (시간표)

**소스**: 컴시간알리미 (http://comci.kr/)

**기능**:
- 학교 검색
- 시간표 조회 (이번 주/다음 주)
- 담임 선생님 정보

**API 키**: 불필요 (공개 API)

**제공 데이터**:
```python
- 학교명, 지역
- 학년/반별 시간표
- 과목명
- 교사명
```

### 2. NEIS 오픈 API (급식)

**소스**: 나이스 교육정보 개방포털 (https://open.neis.go.kr/)

**기능**:
- 학교 검색
- 급식 메뉴 조회
- 영양 정보 조회

**API 키**: 선택사항 (없어도 작동)

**제공 데이터**:
```python
- 조식/중식/석식 메뉴
- 칼로리 정보
- 영양 성분
- 원산지 정보
```

---

## 📊 성능 최적화

### 캐싱 적용

Streamlit의 `@st.cache_data`를 사용하여 API 호출 최소화:

```python
@st.cache_data(ttl=600)  # 10분 캐시
def get_timetable(school_name, week_num):
    return pycomcigan.TimeTable(school_name, week_num)
```

### 로딩 시간 개선

- 초기 로딩: ~2초
- API 호출: ~1-2초
- 캐시 사용 시: ~0.1초

---

## 🐛 문제 해결

### 배포 실패

**문제**: "Error deploying app"

**해결**:
1. `requirements.txt` 확인
2. Python 버전 호환성 확인
3. Streamlit Cloud 로그 확인

### API 오류

**문제**: "학교를 찾을 수 없습니다"

**해결**:
1. 정확한 학교명 입력
2. 인터넷 연결 확인
3. API 서버 상태 확인

### 느린 로딩

**문제**: 앱이 느리게 로드됨

**해결**:
1. Streamlit Cloud 리소스 확인
2. 캐싱 활성화
3. 불필요한 라이브러리 제거

---

## 🔒 보안

### 환경 변수 (필요시)

Streamlit Cloud의 **Secrets** 기능 사용:

1. Streamlit Cloud 앱 설정
2. "Secrets" 탭 클릭
3. TOML 형식으로 입력:

```toml
[api]
neis_key = "YOUR_API_KEY_HERE"
```

4. 코드에서 사용:

```python
import streamlit as st
api_key = st.secrets["api"]["neis_key"]
```

**참고**: 현재 앱은 API 키 없이 작동하므로 불필요합니다.

---

## 📱 모바일 최적화

앱은 **반응형 디자인**으로 제작되어 모바일에서도 완벽하게 작동합니다:

- ✅ 터치 인터페이스 지원
- ✅ 작은 화면 최적화
- ✅ 빠른 로딩

**홈 화면 추가**:
- iOS: Safari → 공유 → "홈 화면에 추가"
- Android: Chrome → 메뉴 → "홈 화면에 추가"

---

## 🎯 사용 예시

### 예시 1: 개별 반 시간표

```
1. 학교 검색: "고운고등학교"
2. 학년: 3, 반: 1
3. 보기 모드: "개별 반"
4. 시간표 불러오기
→ 3학년 1반의 상세 시간표 표시
```

### 예시 2: 전체 학년 시간표

```
1. 학교 검색: "고운고등학교"
2. 학년: 2
3. 보기 모드: "전체 학년"
4. 시간표 불러오기
→ 2학년 전체 반의 시간표를 한눈에
```

### 예시 3: 급식 정보

```
1. 학교 검색: "고운고등학교"
2. 급식 불러오기
3. 급식 탭 선택
→ 월~금요일 급식 메뉴 표시
```

---

## 📈 통계 및 모니터링

Streamlit Cloud 대시보드에서 확인 가능:

- 📊 일일 방문자 수
- 🕐 평균 사용 시간
- 🌍 지역별 접속 통계
- 🔧 앱 상태 및 오류

---

## 🚀 다음 단계

배포 후 추가할 수 있는 기능:

- [ ] 사용자 즐겨찾기 (로컬 스토리지)
- [ ] 푸시 알림 (시간표 변경 시)
- [ ] 다크 모드
- [ ] 시간표 PDF 다운로드
- [ ] 여러 학교 비교
- [ ] 통계 및 분석

---

## 📞 지원

**문제 발생 시**:
- Streamlit 포럼: https://discuss.streamlit.io/
- GitHub Issues: https://github.com/mediatte/school-status/issues

**참고 자료**:
- Streamlit 문서: https://docs.streamlit.io/
- pycomcigan: https://github.com/hegelty/pycomcigan
- NEIS API: https://open.neis.go.kr/

---

**작성일**: 2025-11-23  
**저장소**: https://github.com/mediatte/school-status  
**버전**: 1.0.0

