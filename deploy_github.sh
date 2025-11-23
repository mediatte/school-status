#!/bin/bash

# GitHub Pages 배포 스크립트

echo "🚀 GitHub Pages 배포를 시작합니다..."
echo ""

# Git 설치 확인
if ! command -v git &> /dev/null; then
    echo "❌ Git이 설치되어 있지 않습니다."
    echo "💡 https://git-scm.com/ 에서 Git을 설치해주세요."
    exit 1
fi

# 현재 디렉토리 확인
if [ ! -f "index.html" ]; then
    echo "❌ index.html 파일을 찾을 수 없습니다."
    echo "💡 프로젝트 폴더에서 실행해주세요."
    exit 1
fi

# Git 초기화
if [ ! -d ".git" ]; then
    echo "📦 Git 저장소 초기화 중..."
    git init
    echo ""
fi

# GitHub 저장소 URL 입력
read -p "📝 GitHub 저장소 URL을 입력하세요 (예: https://github.com/username/school-status.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ 저장소 URL이 입력되지 않았습니다."
    exit 1
fi

# 원격 저장소 설정
if git remote | grep -q "origin"; then
    echo "🔄 기존 원격 저장소를 업데이트합니다..."
    git remote set-url origin "$REPO_URL"
else
    echo "🔗 원격 저장소를 연결합니다..."
    git remote add origin "$REPO_URL"
fi

# 파일 추가
echo "📂 파일을 스테이징합니다..."
git add index.html style.css app.js README.md example_sheet_template.txt .gitignore .github/

# 커밋
echo "💾 커밋을 생성합니다..."
git commit -m "Deploy: School status board to GitHub Pages" || echo "⚠️  변경사항이 없거나 이미 커밋되었습니다."

# 브랜치 확인 및 변경
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "🌿 main 브랜치로 변경합니다..."
    git branch -M main
fi

# 푸시
echo "🚀 GitHub에 푸시합니다..."
git push -u origin main

echo ""
echo "✅ 배포가 완료되었습니다!"
echo ""
echo "📍 다음 단계:"
echo "1. GitHub 저장소 페이지로 이동"
echo "2. Settings → Pages 메뉴 선택"
echo "3. Source에서 'main' 브랜치 선택"
echo "4. 몇 분 후 https://YOUR_USERNAME.github.io/REPO_NAME/ 에서 확인"
echo ""
echo "📚 자세한 가이드: GITHUB_PAGES_GUIDE.md 파일 참고"

