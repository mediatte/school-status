# 📚 실시간 학교 시간표 (Streamlit 버전)

[pycomcigan](https://github.com/hegelty/pycomcigan) 라이브러리를 활용한 **컴시간알리미** 연동 실시간 시간표 앱입니다.

Streamlit으로 제작되어 별도의 Google API 설정 없이 바로 사용할 수 있습니다!

## ✨ 주요 기능

- ✅ **학교 검색**: 컴시간알리미에 등록된 전국 학교 검색
- ✅ **실시간 시간표**: 이번 주 / 다음 주 시간표 조회
- ✅ **담임 정보**: 학급별 담임 선생님 정보
- ✅ **자동 새로고침**: 설정한 시간마다 자동 업데이트
- ✅ **반응형 디자인**: 모바일, 태블릿, PC 모두 지원
- ✅ **직관적인 UI**: 요일별 탭으로 깔끔하게 표시

## 🚀 빠른 시작

### 1단계: 패키지 설치

```bash
pip install -r requirements.txt
```

또는 개별 설치:

```bash
pip install streamlit pycomcigan
```

### 2단계: 앱 실행

```bash
streamlit run streamlit_app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 앱이 실행됩니다.

### 3단계: 학교 검색 및 시간표 조회

1. 왼쪽 사이드바에서 학교명 입력 (예: "고운고등학교")
2. 검색된 학교 목록에서 선택
3. 학년과 반 선택
4. 주차 선택 (이번 주 / 다음 주)
5. "시간표 불러오기" 버튼 클릭

## 📖 사용 방법

### 학교 검색

<img src="https://img.shields.io/badge/1-학교명_입력-blue" alt="Step 1"/>

사이드바의 "학교명 검색" 입력창에 학교 이름을 입력합니다.

```
예시:
- 고운고등학교
- 경기북과학고
- 서울고
- 부산
```

검색어에 해당하는 모든 학교가 표시됩니다.

### 시간표 조회

<img src="https://img.shields.io/badge/2-학교_선택-green" alt="Step 2"/>

검색 결과에서 원하는 학교를 선택합니다.

<img src="https://img.shields.io/badge/3-학년/반_선택-orange" alt="Step 3"/>

학년(1-3)과 반(1-20)을 입력합니다.

<img src="https://img.shields.io/badge/4-주차_선택-red" alt="Step 4"/>

- **이번 주**: 현재 주의 시간표
- **다음 주**: 다음 주의 시간표

<img src="https://img.shields.io/badge/5-시간표_불러오기-purple" alt="Step 5"/>

"시간표 불러오기" 버튼을 클릭하면 시간표가 로드됩니다.

### 자동 새로고침

자동 새로고침을 활성화하면 설정한 간격마다 시간표가 자동으로 업데이트됩니다.

- ☑️ 자동 새로고침 체크박스 활성화
- 🎚️ 슬라이더로 간격 설정 (10초 ~ 300초)

## 🎨 화면 구성

### 메인 화면

```
┌─────────────────────────────────────────────┐
│  📚 실시간 학교 시간표                         │
├─────────────────────────────────────────────┤
│  🏫 학교  │  👥 학년/반  │  🕐 마지막 업데이트  │
├─────────────────────────────────────────────┤
│  👨‍🏫 담임 선생님: OOO                        │
├─────────────────────────────────────────────┤
│  [월] [화] [수] [목] [금]  ← 탭              │
│                                             │
│  1교시  국어   👨‍🏫 김선생                    │
│  2교시  수학   👨‍🏫 이선생                    │
│  3교시  영어   👨‍🏫 박선생                    │
│  ...                                        │
└─────────────────────────────────────────────┘
```

### 사이드바

```
┌────────────────────┐
│  ⚙️ 설정            │
├────────────────────┤
│  🏫 학교명 검색     │
│  [입력창]          │
│                    │
│  학교 선택          │
│  [드롭다운]        │
│                    │
│  📖 학년  🏛️ 반     │
│  [1] [1]           │
│                    │
│  📅 주차 선택       │
│  ◉ 이번 주         │
│  ○ 다음 주         │
│                    │
│  🔄 자동 새로고침   │
│  ☑️ 60초           │
│                    │
│  [시간표 불러오기]  │
└────────────────────┘
```

## 🔧 커스터마이징

### 색상 테마 변경

`.streamlit/config.toml` 파일 수정:

```toml
[theme]
primaryColor = "#667eea"        # 메인 색상
backgroundColor = "#ffffff"     # 배경색
secondaryBackgroundColor = "#f0f2f6"  # 보조 배경색
textColor = "#262730"           # 텍스트 색상
```

### 포트 변경

```toml
[server]
port = 8501  # 원하는 포트 번호로 변경
```

또는 실행 시 옵션으로:

```bash
streamlit run streamlit_app.py --server.port 8080
```

### CSS 커스터마이징

`streamlit_app.py` 파일의 `st.markdown()` 섹션에서 CSS를 수정할 수 있습니다.

```python
st.markdown("""
<style>
    .subject-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        /* 여기에 원하는 스타일 추가 */
    }
</style>
""", unsafe_allow_html=True)
```

## 🌐 배포하기

### Streamlit Cloud (무료, 추천)

1. **GitHub 저장소 생성**
   - 이 프로젝트를 GitHub에 업로드

2. **Streamlit Cloud 접속**
   - [share.streamlit.io](https://share.streamlit.io) 접속
   - GitHub 계정으로 로그인

3. **앱 배포**
   - "New app" 클릭
   - 저장소 선택
   - Main file path: `streamlit_app.py`
   - "Deploy!" 클릭

4. **공개 URL 받기**
   - 배포 완료 후 `https://your-app.streamlit.app` 형식의 URL 생성

### Heroku

```bash
# Procfile 생성
echo "web: streamlit run streamlit_app.py --server.port $PORT" > Procfile

# runtime.txt 생성
echo "python-3.11.0" > runtime.txt

# Heroku 배포
heroku create your-app-name
git push heroku main
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t school-timetable .
docker run -p 8501:8501 school-timetable
```

## 💡 활용 예시

### 교실 디스플레이

TV나 모니터에 전체화면으로 표시하여 학급 시간표로 활용

```bash
streamlit run streamlit_app.py --server.headless true
```

### 학교 홈페이지 임베딩

Streamlit Cloud로 배포 후 iframe으로 임베딩:

```html
<iframe src="https://your-app.streamlit.app" width="100%" height="800px"></iframe>
```

### 모바일 앱처럼 사용

스마트폰 브라우저에서:
1. 앱 URL 접속
2. 브라우저 메뉴 → "홈 화면에 추가"
3. 앱 아이콘으로 바로 접속 가능

## 🐛 문제 해결

### "학교를 찾을 수 없습니다"

- **원인**: 컴시간알리미에 등록되지 않은 학교
- **해결**: 
  - 정확한 학교명으로 검색
  - 지역명으로 검색 (예: "부산", "경기")
  - [컴시간알리미](http://comci.kr/) 사이트에서 학교 확인

### "시간표를 불러올 수 없습니다"

- **원인**: 
  - 네트워크 오류
  - 컴시간알리미 서버 문제
  - 해당 학급에 시간표 없음
- **해결**:
  - 인터넷 연결 확인
  - 잠시 후 다시 시도
  - 다른 학년/반으로 테스트

### "모듈을 찾을 수 없습니다" (ModuleNotFoundError)

```bash
# 모든 패키지 재설치
pip install -r requirements.txt --upgrade

# 특정 패키지 설치
pip install pycomcigan
```

### 자동 새로고침이 작동하지 않음

- **원인**: 브라우저 백그라운드 탭 일시중지
- **해결**: 탭을 활성화 상태로 유지

### Streamlit 실행 오류

```bash
# Streamlit 업데이트
pip install streamlit --upgrade

# 캐시 삭제
streamlit cache clear
```

## 📊 데이터 소스

이 앱은 [컴시간알리미](http://comci.kr/)의 데이터를 사용합니다.

- **pycomcigan 라이브러리**: [https://github.com/hegelty/pycomcigan](https://github.com/hegelty/pycomcigan)
- **컴시간알리미 공식 사이트**: [http://comci.kr/](http://comci.kr/)

## 🔒 개인정보 및 보안

- ✅ 이 앱은 **공개된 시간표 정보만** 조회합니다
- ✅ 개인정보를 수집하거나 저장하지 않습니다
- ✅ 모든 데이터는 컴시간알리미 공식 API를 통해 가져옵니다
- ✅ 학교 외부에 공개하지 말아야 할 정보는 표시하지 마세요

## 🚀 추가 기능 아이디어

이 기본 버전이 잘 작동한다면, 다음과 같은 기능을 추가할 수 있습니다:

- [ ] 📅 달력 뷰로 시간표 표시
- [ ] 🔔 다음 수업 알림 기능
- [ ] 📊 과목별 통계 (주당 수업 시간)
- [ ] 🔍 선생님 이름으로 시간표 검색
- [ ] 💾 즐겨찾기 (자주 보는 학급 저장)
- [ ] 📱 PWA (Progressive Web App) 지원
- [ ] 🌙 다크 모드
- [ ] 📤 시간표 PDF 다운로드
- [ ] 📧 시간표 변경 알림 (이메일/카카오톡)

## 📞 문의 및 지원

문제가 발생하거나 기능 추가가 필요하면 언제든지 문의하세요!

### 관련 링크

- **pycomcigan 라이브러리**: [https://github.com/hegelty/pycomcigan](https://github.com/hegelty/pycomcigan)
- **Streamlit 공식 문서**: [https://docs.streamlit.io](https://docs.streamlit.io)
- **컴시간알리미**: [http://comci.kr/](http://comci.kr/)

## 📄 라이선스

MIT License

이 프로젝트는 [pycomcigan](https://github.com/hegelty/pycomcigan) 라이브러리를 사용합니다.

---

**만든 날짜**: 2025-11-23  
**버전**: 1.0.0  
**기술 스택**: Python, Streamlit, pycomcigan  
**참고**: [pycomcigan GitHub](https://github.com/hegelty/pycomcigan)

