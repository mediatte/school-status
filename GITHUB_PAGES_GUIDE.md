# 🌐 GitHub Pages 배포 가이드

GitHub Pages로 학교 현황 게시판을 무료로 호스팅하는 방법입니다.

## 📋 목차

1. [GitHub Pages 배포 (Google Sheets 버전)](#github-pages-배포)
2. [Streamlit Cloud 배포 (Streamlit 버전)](#streamlit-cloud-배포)

---

## 🚀 GitHub Pages 배포 (Google Sheets 버전)

GitHub Pages는 **정적 웹사이트**만 호스팅 가능하므로, Google Sheets 연동 버전(`index.html`)을 사용합니다.

### 1단계: GitHub 저장소 생성

1. **GitHub 접속** (https://github.com)
2. **New repository** 클릭
3. 저장소 정보 입력:
   - Repository name: `school-status` (또는 원하는 이름)
   - Public 선택
   - ✅ Add a README file (체크)
4. **Create repository** 클릭

### 2단계: 파일 업로드

#### 방법 A: 웹에서 직접 업로드

1. 저장소 페이지에서 **Add file** → **Upload files** 클릭
2. 다음 파일들을 드래그 앤 드롭:
   ```
   index.html
   style.css
   app.js
   README.md
   example_sheet_template.txt
   ```
3. **Commit changes** 클릭

#### 방법 B: Git 명령어 사용

```bash
# 프로젝트 폴더에서
cd "/Users/jhl/Library/CloudStorage/OneDrive-고운고등학교/PROJECTS/school_status"

# Git 초기화
git init
git add index.html style.css app.js README.md example_sheet_template.txt .gitignore
git commit -m "Initial commit: School status board"

# GitHub 저장소 연결 (YOUR_USERNAME를 본인 계정명으로)
git remote add origin https://github.com/YOUR_USERNAME/school-status.git
git branch -M main
git push -u origin main
```

### 3단계: GitHub Pages 활성화

1. 저장소 페이지에서 **Settings** 탭 클릭
2. 왼쪽 메뉴에서 **Pages** 클릭
3. **Source** 섹션에서:
   - Branch: `main` 선택
   - Folder: `/ (root)` 선택
4. **Save** 클릭

### 4단계: 배포 완료! 🎉

몇 분 후 다음 주소로 접속 가능:
```
https://YOUR_USERNAME.github.io/school-status/
```

또는 커스텀 도메인 설정 가능:
```
https://status.your-school.kr
```

### 5단계: Google Sheets API 설정

배포 후에는 `app.js` 파일에서 Google Sheets API 키와 시트 ID를 설정해야 합니다.

자세한 설정 방법은 `README.md` 파일을 참고하세요.

---

## ☁️ Streamlit Cloud 배포 (Streamlit 버전)

Streamlit 앱(Python)을 무료로 배포하는 가장 쉬운 방법입니다.

### 1단계: GitHub 저장소 준비

위의 GitHub Pages 배포 1-2단계와 동일하게 저장소를 만들고, 다음 파일들을 업로드:
```
streamlit_app.py
neis_meal.py
requirements.txt
.streamlit/config.toml
```

### 2단계: Streamlit Cloud 가입

1. **Streamlit Cloud 접속** (https://share.streamlit.io)
2. **Sign up with GitHub** 클릭
3. GitHub 계정으로 로그인
4. Streamlit Cloud에 GitHub 저장소 접근 권한 부여

### 3단계: 앱 배포

1. Streamlit Cloud 대시보드에서 **New app** 클릭
2. 배포 정보 입력:
   - **Repository**: `YOUR_USERNAME/school-status`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
3. **Deploy!** 클릭

### 4단계: 배포 완료! 🎉

몇 분 후 다음과 같은 주소로 접속 가능:
```
https://YOUR_USERNAME-school-status-streamlit-app-RANDOM.streamlit.app
```

### 5단계: 커스텀 URL 설정 (선택)

Streamlit Cloud 설정에서 앱 이름을 변경하여 더 짧은 URL 사용 가능.

---

## 🔄 자동 배포 (CI/CD)

### GitHub Pages 자동 배포

`.github/workflows/deploy.yml` 파일이 이미 생성되어 있습니다.

- `main` 브랜치에 푸시하면 자동으로 GitHub Pages에 배포됩니다
- Actions 탭에서 배포 상태 확인 가능

### Streamlit Cloud 자동 배포

- GitHub 저장소에 푸시하면 자동으로 Streamlit Cloud에 배포됩니다
- 별도 설정 불필요

---

## 📊 비교표

| 항목 | GitHub Pages | Streamlit Cloud |
|------|-------------|----------------|
| **사용 버전** | Google Sheets 연동 | Streamlit + NEIS API |
| **비용** | 무료 | 무료 |
| **설정 난이도** | 중간 | 쉬움 |
| **API 키 필요** | Google Sheets API | 불필요 (선택) |
| **자동 새로고침** | JavaScript | Python |
| **급식 정보** | ❌ (추가 구현 필요) | ✅ NEIS API |
| **커스텀 도메인** | ✅ 무료 | ✅ 유료 플랜 |
| **속도** | 매우 빠름 | 빠름 |
| **서버 관리** | 불필요 | 불필요 |

## 💡 추천

### GitHub Pages를 추천하는 경우:
- ✅ 학교 현황만 표시 (급식 불필요)
- ✅ Google Sheets로 데이터 관리
- ✅ 매우 빠른 로딩 속도 원함
- ✅ 커스텀 도메인 사용 (무료)

### Streamlit Cloud를 추천하는 경우:
- ✅ 급식 정보도 함께 표시
- ✅ NEIS API 활용
- ✅ Python 환경 선호
- ✅ 빠른 배포 원함

## 🔧 문제 해결

### GitHub Pages가 표시되지 않을 때

1. **Settings → Pages**에서 배포 상태 확인
2. **Actions** 탭에서 워크플로우 실행 확인
3. 브라우저 캐시 삭제 후 재접속
4. HTTPS 주소 사용 확인

### Streamlit Cloud 배포 실패 시

1. `requirements.txt` 파일 확인
2. Python 버전 호환성 확인 (3.8-3.12)
3. Streamlit Cloud 로그 확인
4. 저장소가 Public인지 확인

---

## 📱 모바일 앱처럼 사용하기

### iOS (iPhone/iPad)

1. Safari에서 사이트 접속
2. 하단 공유 버튼 탭
3. "홈 화면에 추가" 선택
4. 이름 입력 후 "추가"

### Android

1. Chrome에서 사이트 접속
2. 우측 상단 메뉴 (⋮)
3. "홈 화면에 추가" 선택
4. 이름 입력 후 "추가"

---

## 🔒 보안 및 주의사항

### GitHub Pages
- ✅ HTTPS 자동 지원
- ⚠️ API 키를 코드에 직접 넣지 마세요 (환경 변수 사용)
- ⚠️ Private 저장소는 GitHub Pro 필요

### Streamlit Cloud
- ✅ HTTPS 자동 지원
- ✅ 비밀 정보는 Secrets 기능 사용
- ✅ Private 저장소 지원

---

## 📞 문의 및 지원

배포 과정에서 문제가 발생하면:

1. **GitHub Pages**: [GitHub Pages 문서](https://docs.github.com/pages)
2. **Streamlit Cloud**: [Streamlit 포럼](https://discuss.streamlit.io/)

---

**작성일**: 2025-11-23  
**버전**: 1.0.0

