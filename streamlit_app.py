import streamlit as st
import pycomcigan
from datetime import datetime, timedelta
from neis_meal import NeisAPI
import re

# 페이지 설정
st.set_page_config(
    page_title="학교 현황",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS - 검은 배경 깔끔한 디자인
st.markdown("""
<style>
    /* 메인 배경 */
    .main {
        background-color: #000000;
        padding: 15px 10px;
    }
    .stApp {
        background-color: #000000;
    }
    
    /* 타이틀 */
    .main-title {
        text-align: center;
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: bold;
        margin: 15px 0;
        letter-spacing: 2px;
    }
    
    /* 날짜 네비게이션 */
    .date-nav {
        background: #1a1a1a;
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.05);
    }
    
    .date-display {
        text-align: center;
        color: #ffffff;
        font-size: 1.3rem;
        font-weight: bold;
        margin: 8px 0;
    }
    
    .weekday {
        text-align: center;
        color: #888888;
        font-size: 0.95rem;
        margin-bottom: 10px;
    }
    
    /* 컨텐츠 카드 */
    .content-card {
        background: #1a1a1a;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.05);
        border: 1px solid #2a2a2a;
    }
    
    .card-title {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 15px;
        padding-bottom: 12px;
        border-bottom: 2px solid #333333;
    }
    
    /* 시간표 */
    .timetable-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin-top: 10px;
    }
    
    .class-card {
        background: #2a2a2a;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #3a3a3a;
        transition: all 0.3s;
    }
    
    .class-card:hover {
        background: #333333;
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .class-number {
        color: #667eea;
        font-size: 0.9rem;
        font-weight: bold;
        margin-bottom: 8px;
        text-align: center;
        padding-bottom: 6px;
        border-bottom: 2px solid #3a3a3a;
    }
    
    .schedule-table {
        width: 100%;
        font-size: 0.7rem;
    }
    
    .schedule-table tr {
        border-bottom: 1px solid #3a3a3a;
    }
    
    .schedule-table tr:last-child {
        border-bottom: none;
    }
    
    .schedule-table td {
        padding: 4px 2px;
        color: #cccccc;
    }
    
    .period-num {
        color: #667eea;
        font-weight: bold;
        width: 20px;
        text-align: center;
    }
    
    .subject-name {
        color: #ffffff;
        font-weight: 500;
    }
    
    .teacher-name {
        color: #888888;
        font-size: 0.65rem;
        text-align: right;
    }
    
    /* 급식 */
    .meal-card {
        background: #2a2a2a;
        padding: 15px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 3px solid #ff6b6b;
    }
    
    .meal-type {
        color: #ff6b6b;
        font-size: 1rem;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .meal-menu {
        color: #cccccc;
        font-size: 0.85rem;
        line-height: 1.6;
    }
    
    .meal-info {
        color: #888888;
        font-size: 0.75rem;
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid #3a3a3a;
    }
    
    /* 버튼 스타일 */
    .stButton button {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #3a3a3a;
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background-color: #667eea;
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* 입력 필드 */
    .stTextInput input, .stSelectbox select {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #3a3a3a;
        border-radius: 10px;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* 주말 표시 */
    .weekend-notice {
        text-align: center;
        color: #888888;
        font-size: 1.2rem;
        padding: 50px 20px;
    }
    
    /* 로딩 */
    .stSpinner > div {
        border-color: #667eea transparent transparent transparent;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'school_name' not in st.session_state:
    st.session_state.school_name = "고운고등학교"
if 'grade' not in st.session_state:
    st.session_state.grade = 1
if 'current_date' not in st.session_state:
    st.session_state.current_date = datetime.now()
if 'timetable' not in st.session_state:
    st.session_state.timetable = None
if 'meal_data' not in st.session_state:
    st.session_state.meal_data = None
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# 데이터 로딩 함수
@st.cache_data(ttl=600)
def load_timetable(school_name):
    try:
        return pycomcigan.TimeTable(school_name, week_num=0)
    except:
        return None

@st.cache_data(ttl=600)
def load_meals_monthly(school_name, year, month):
    try:
        neis_api = NeisAPI()
        clean_name = re.sub(r'\s*\([^)]*\)', '', school_name).strip()
        schools = neis_api.search_school(clean_name)
        if schools:
            school = schools[0]
            school_code = school.get("SD_SCHUL_CODE", "")
            atpt_code = school.get("ATPT_OFCDC_SC_CODE", "")
            return neis_api.get_meal(school_code, atpt_code, year, month)
        return None
    except:
        return None

# 타이틀
st.markdown("<h1 class='main-title'>학교 현황</h1>", unsafe_allow_html=True)

# 상단 설정
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    school = st.text_input("학교", value=st.session_state.school_name,
                          label_visibility="collapsed",
                          placeholder="학교명을 입력하세요")
    if school != st.session_state.school_name:
        st.session_state.school_name = school
        st.session_state.initialized = False

with col2:
    grade = st.selectbox("학년", [1, 2, 3],
                        index=st.session_state.grade - 1,
                        label_visibility="collapsed")
    if grade != st.session_state.grade:
        st.session_state.grade = grade

with col3:
    if st.button("🔄 새로고침", use_container_width=True):
        st.session_state.initialized = False
        st.cache_data.clear()
        st.rerun()

# 초기 데이터 로드
if not st.session_state.initialized and st.session_state.school_name:
    with st.spinner("데이터를 불러오는 중..."):
        st.session_state.timetable = load_timetable(st.session_state.school_name)
        current_date = st.session_state.current_date
        st.session_state.meal_data = load_meals_monthly(
            st.session_state.school_name,
            current_date.year,
            current_date.month
        )
        st.session_state.initialized = True

# 날짜 네비게이션
st.markdown("<div class='date-nav'>", unsafe_allow_html=True)

nav_cols = st.columns([1, 3, 1])

with nav_cols[0]:
    if st.button("◀", use_container_width=True, key="prev_day"):
        st.session_state.current_date -= timedelta(days=1)
        # 월이 바뀌면 급식 데이터 다시 로드
        if st.session_state.current_date.month != (st.session_state.current_date + timedelta(days=1)).month:
            st.session_state.meal_data = load_meals_monthly(
                st.session_state.school_name,
                st.session_state.current_date.year,
                st.session_state.current_date.month
            )
        st.rerun()

with nav_cols[1]:
    current_date = st.session_state.current_date
    weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    weekday = current_date.weekday()
    
    st.markdown(f"""
    <div class='weekday'>{weekday_names[weekday]}</div>
    <div class='date-display'>{current_date.strftime('%Y.%m.%d')}</div>
    """, unsafe_allow_html=True)

with nav_cols[2]:
    if st.button("▶", use_container_width=True, key="next_day"):
        st.session_state.current_date += timedelta(days=1)
        # 월이 바뀌면 급식 데이터 다시 로드
        if st.session_state.current_date.month != (st.session_state.current_date - timedelta(days=1)).month:
            st.session_state.meal_data = load_meals_monthly(
                st.session_state.school_name,
                st.session_state.current_date.year,
                st.session_state.current_date.month
            )
        st.rerun()

# 오늘로 돌아가기 버튼
if st.session_state.current_date.date() != datetime.now().date():
    if st.button("📍 오늘로 돌아가기", use_container_width=True):
        st.session_state.current_date = datetime.now()
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# 메인 컨텐츠
if st.session_state.timetable:
    current_date = st.session_state.current_date
    weekday = current_date.weekday()
    
    # 주말 체크
    if weekday >= 5:  # 토요일, 일요일
        st.markdown("""
        <div class='content-card'>
            <div class='weekend-notice'>
                📅<br><br>
                주말입니다
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 시간표 표시
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='card-title'>{st.session_state.grade}학년 시간표</div>", unsafe_allow_html=True)
        
        tt_day_idx = weekday + 1  # pycomcigan 인덱스 (1=월요일)
        
        try:
            grade_data = st.session_state.timetable.timetable[st.session_state.grade]
            max_classes = len(grade_data)
            
            # 전체 HTML을 하나로 합치기
            all_html = "<div class='timetable-grid'>"
            
            for class_num in range(1, max_classes):
                try:
                    class_data = grade_data[class_num]
                    if tt_day_idx < len(class_data):
                        day_schedule = class_data[tt_day_idx]
                        
                        if day_schedule and len(day_schedule) > 0:
                            all_html += "<div class='class-card'>"
                            all_html += f"<div class='class-number'>{class_num}반</div>"
                            all_html += "<table class='schedule-table'>"
                            
                            for period_data in day_schedule:
                                if period_data and hasattr(period_data, 'subject'):
                                    subject = period_data.subject
                                    teacher = period_data.teacher
                                    period_num = period_data.period
                                    
                                    # 7교시까지만 표시하고 빈 교시는 제외
                                    if period_num <= 7 and subject.strip():
                                        all_html += "<tr>"
                                        all_html += f"<td class='period-num'>{period_num}</td>"
                                        all_html += f"<td class='subject-name'>{subject}</td>"
                                        all_html += f"<td class='teacher-name'>{teacher}</td>"
                                        all_html += "</tr>"
                            
                            all_html += "</table></div>"
                except:
                    pass
            
            all_html += "</div>"
            st.markdown(all_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"시간표를 불러올 수 없습니다: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 급식 표시
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>급식</div>", unsafe_allow_html=True)
        
        # 날짜 키를 문자열로 변환하여 확인
        day_key = str(current_date.day)
        
        if st.session_state.meal_data and day_key in st.session_state.meal_data:
            meals = st.session_state.meal_data[day_key]
            
            meal_types = {
                "breakfast": ("조식", "#ffd93d"),
                "lunch": ("중식", "#ff6b6b"),
                "dinner": ("석식", "#6c5ce7")
            }
            
            meal_displayed = False
            for meal_type, (meal_label, meal_color) in meal_types.items():
                if meal_type in meals:
                    meal_info = meals[meal_type]
                    menu = meal_info.get("menu", "")
                    calories = meal_info.get("calories", "")
                    
                    if menu:
                        meal_displayed = True
                        st.markdown(f"""
                        <div class='meal-card'>
                            <div class='meal-type'>{meal_label}</div>
                            <div class='meal-menu'>{menu.replace(chr(10), '<br>')}</div>
                            {f"<div class='meal-info'>{calories}</div>" if calories else ""}
                        </div>
                        """, unsafe_allow_html=True)
            
            if not meal_displayed:
                st.markdown("<div class='meal-card'><div class='meal-menu'>급식 정보가 없습니다</div></div>", 
                           unsafe_allow_html=True)
        else:
            st.markdown("<div class='meal-card'><div class='meal-menu'>급식 정보가 없습니다</div></div>", 
                       unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("""
    <div class='content-card'>
        <div style='text-align: center; color: #888888; padding: 50px 20px;'>
            학교명을 입력하고<br>
            🔄 새로고침 버튼을 클릭하세요
        </div>
    </div>
    """, unsafe_allow_html=True)

# 푸터
st.markdown("""
<div style='text-align: center; color: #444444; padding: 30px 10px; font-size: 0.85rem;'>
    📚 학교 현황판 | pycomcigan & NEIS API
</div>
""", unsafe_allow_html=True)
