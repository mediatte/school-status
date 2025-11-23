// ===== 설정 =====
// Google Sheets 설정
const CONFIG = {
    // 여기에 Google Sheets ID를 입력하세요
    // 예: https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit
    // -> SHEET_ID는 "1ABC...XYZ" 부분입니다
    SHEET_ID: 'YOUR_SHEET_ID_HERE',
    
    // Google Sheets API 키 (README 참고)
    API_KEY: 'YOUR_API_KEY_HERE',
    
    // 읽을 시트의 범위 (예: 'Sheet1!A1:D10' 또는 'Sheet1' 전체)
    SHEET_RANGE: 'Sheet1',
    
    // 자동 새로고침 간격 (밀리초, 10000 = 10초)
    REFRESH_INTERVAL: 10000
};

// ===== 전역 변수 =====
let refreshTimer = null;

// ===== DOM 요소 =====
const elements = {
    loading: document.getElementById('loading'),
    statusBoard: document.getElementById('statusBoard'),
    errorMessage: document.getElementById('errorMessage'),
    lastUpdate: document.getElementById('lastUpdate'),
    manualRefresh: document.getElementById('manualRefresh'),
    refreshInterval: document.getElementById('refreshInterval')
};

// ===== 초기화 =====
function init() {
    // 새로고침 간격 표시
    elements.refreshInterval.textContent = CONFIG.REFRESH_INTERVAL / 1000;
    
    // 수동 새로고침 버튼 이벤트
    elements.manualRefresh.addEventListener('click', () => {
        fetchData();
    });
    
    // 첫 데이터 로드
    fetchData();
    
    // 자동 새로고침 시작
    startAutoRefresh();
}

// ===== Google Sheets 데이터 가져오기 =====
async function fetchData() {
    try {
        showLoading();
        
        // Google Sheets API URL
        const url = `https://sheets.googleapis.com/v4/spreadsheets/${CONFIG.SHEET_ID}/values/${CONFIG.SHEET_RANGE}?key=${CONFIG.API_KEY}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.values || data.values.length === 0) {
            throw new Error('데이터가 없습니다.');
        }
        
        // 데이터 표시
        displayData(data.values);
        
        // 마지막 업데이트 시간 표시
        updateLastUpdateTime();
        
        hideError();
        
    } catch (error) {
        console.error('데이터 가져오기 실패:', error);
        showError(error.message);
    }
}

// ===== 데이터 표시 =====
function displayData(rows) {
    const board = elements.statusBoard;
    board.innerHTML = '';
    
    // 첫 번째 행이 헤더인지 확인
    const hasHeader = rows.length > 1;
    const headers = hasHeader ? rows[0] : null;
    const dataRows = hasHeader ? rows.slice(1) : rows;
    
    // 데이터 표시 방법 선택
    if (headers && headers.length > 1) {
        // 표 형식으로 표시
        displayAsTable(headers, dataRows);
    } else {
        // 카드 형식으로 표시
        displayAsCards(dataRows);
    }
    
    board.style.display = 'block';
    hideLoading();
}

// ===== 표 형식 표시 =====
function displayAsTable(headers, rows) {
    const table = document.createElement('table');
    table.className = 'data-table';
    
    // 헤더 생성
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // 데이터 생성
    const tbody = document.createElement('tbody');
    rows.forEach(row => {
        const tr = document.createElement('tr');
        headers.forEach((_, index) => {
            const td = document.createElement('td');
            td.textContent = row[index] || '-';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    
    elements.statusBoard.appendChild(table);
}

// ===== 카드 형식 표시 =====
function displayAsCards(rows) {
    rows.forEach((row, index) => {
        const card = document.createElement('div');
        card.className = 'status-item';
        
        // 카드 내용 생성
        if (row.length >= 2) {
            // 제목과 내용이 있는 경우
            const title = document.createElement('h3');
            title.textContent = row[0] || `항목 ${index + 1}`;
            card.appendChild(title);
            
            for (let i = 1; i < row.length; i++) {
                if (row[i]) {
                    const p = document.createElement('p');
                    p.textContent = row[i];
                    card.appendChild(p);
                }
            }
        } else {
            // 단순 텍스트만 있는 경우
            const p = document.createElement('p');
            p.textContent = row[0] || '-';
            card.appendChild(p);
        }
        
        elements.statusBoard.appendChild(card);
    });
}

// ===== 자동 새로고침 =====
function startAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
    
    refreshTimer = setInterval(() => {
        fetchData();
    }, CONFIG.REFRESH_INTERVAL);
}

function stopAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
    }
}

// ===== UI 헬퍼 함수 =====
function showLoading() {
    elements.loading.style.display = 'block';
    elements.statusBoard.style.display = 'none';
    elements.errorMessage.style.display = 'none';
}

function hideLoading() {
    elements.loading.style.display = 'none';
}

function showError(message) {
    elements.errorMessage.style.display = 'block';
    elements.errorMessage.querySelector('.error-detail').textContent = message;
    elements.statusBoard.style.display = 'none';
    hideLoading();
}

function hideError() {
    elements.errorMessage.style.display = 'none';
}

function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    elements.lastUpdate.textContent = `마지막 업데이트: ${timeString}`;
}

// ===== 페이지 로드 시 실행 =====
document.addEventListener('DOMContentLoaded', init);

// ===== 페이지를 떠날 때 타이머 정리 =====
window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
});

