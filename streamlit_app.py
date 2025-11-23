import streamlit as st
import pycomcigan
from datetime import datetime, timedelta
import time
from neis_meal import NeisAPI
import re
import calendar

# 페이지 설정
st.set_page_config(
    page_title="학교 현황",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS - 9:16 모바일 최적화
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        max-width: 100%;
        padding: 10px;
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-title {
        text-align: center;
        color: white;
        font-size: clamp(1.3rem, 4vw, 2rem);
        font-weight: bold;
        margin: 10px 0;
        white-space: nowrap;
    }
    .mini-calendar {
        background: white;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    .mini-cal-header {
        text-align: center;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 8px;
        font-size: 0.9em;
    }
    .mini-cal-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 3px;
        font-size: 0.75em;
    }
    .mini-day {
        text-align: center;
        padding: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
        transition: all 0.2s;
    }
    .mini-day:hover {
        background: #e7f5ff;
    }
    .mini-day.today {
        background: #667eea;
        color: white;
        font-weight: bold;
    }
    .mini-day.selected {
        background: #ff6b6b;
        color: white;
    }
    .mini-day.weekend {
        color: #999;
    }
    .mini-day.other-month {
        opacity: 0.3;
    }
    .week-container {
        background: white;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .day-column {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        min-height: 200px;
    }
    .day-header {
        text-align: center;
        font-weight: bold;
        color: #667eea;
        font-size: 1em;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 2px solid #667eea;
    }
    .day-date {
        text-align: center;
        color: #999;
        font-size: 0.85em;
        margin-bottom: 10px;
    }
    .timetable-section {
        background: white;
        padding: 8px;
        border-radius: 8px;
        margin: 8px 0;
    }
    .section-title {
        color: #667eea;
        font-size: 0.9em;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .class-item {
        font-size: 0.8em;
        padding: 4px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    .class-item:last-child {
        border-bottom: none;
    }
    .meal-section {
        background: #fff5f5;
        padding: 8px;
        border-radius: 8px;
        margin: 8px 0;
    }
    .meal-title {
        color: #ff6b6b;
        font-size: 0.9em;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .meal-menu {
        font-size: 0.75em;
        line-height: 1.4;
        color: #333;
    }
    .compact-controls {
        background: white;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
    }
    /* 모바일 최적화 */
    @media (max-width: 768px) {
        .main {
            padding: 5px;
        }
        .day-column {
            padding: 8px;
        }
        .class-item {
            font-size: 0.75em;
        }
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'school_name' not in st.session_state:
    st.session_state.school_name = "고운고등학교"
if 'grade' not in st.session_state:
    st.session_state.grade = 1
if 'timetable' not in st.session_state:
    st.session_state.timetable = None
if 'meal_data' not in st.session_state:
    st.session_state.meal_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'selected_week_start' not in st.session_state:
    # 이번 주 월요일
    today = datetime.now()
    weekday = today.weekday()
    monday = today - timedelta(days=weekday)
    st.session_state.selected_week_start = monday
if 'current_month' not in st.session_state:
    st.session_state.current_month = datetime.now().month
if 'current_year' not in st.session_state:
    st.session_state.current_year = datetime.now().year

# 타이틀
st.markdown("<h1 class='main-title'>📚 학교 현황</h1>", unsafe_allow_html=True)

# 상단 컨트롤
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    school = st.text_input("학교", value=st.session_state.school_name, 
                          label_visibility="collapsed",
                          placeholder="학교명")
    if school:
        st.session_state.school_name = school

with col2:
    grade = st.selectbox("학년", [1, 2, 3], 
                        index=st.session_state.grade - 1,
                        label_visibility="collapsed")
    st.session_state.grade = grade

with col3:
    if st.button("🔄", use_container_width=True, type="primary", help="새로고침"):
        st.session_state.initialized = False
        st.cache_data.clear()
        st.rerun()

# 데이터 로딩
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

# 초기 로드
if not st.session_state.initialized and st.session_state.school_name:
    with st.spinner("로딩..."):
        st.session_state.timetable = load_timetable(st.session_state.school_name)
        st.session_state.meal_data = load_meals_monthly(
            st.session_state.school_name,
            st.session_state.current_year,
            st.session_state.current_month
        )
        st.session_state.last_update = datetime.now()
        st.session_state.initialized = True

# 미니 달력 + 주간 네비게이션
col_cal, col_nav = st.columns([1, 2])

with col_cal:
    # 미니 달력
    st.markdown("<div class='mini-calendar'>", unsafe_allow_html=True)
    
    # 월 선택
    cal_cols = st.columns([1, 2, 1])
    with cal_cols[0]:
        if st.button("◀", key="prev_month"):
            if st.session_state.current_month == 1:
                st.session_state.current_month = 12
                st.session_state.current_year -= 1
            else:
                st.session_state.current_month -= 1
            st.rerun()
    
    with cal_cols[1]:
        st.markdown(f"<div class='mini-cal-header'>{st.session_state.current_year}년 {st.session_state.current_month}월</div>", 
                   unsafe_allow_html=True)
    
    with cal_cols[2]:
        if st.button("▶", key="next_month"):
            if st.session_state.current_month == 12:
                st.session_state.current_month = 1
                st.session_state.current_year += 1
            else:
                st.session_state.current_month += 1
            st.rerun()
    
    # 달력 그리드
    weekdays = ['일', '월', '화', '수', '목', '금', '토']
    st.markdown("<div class='mini-cal-grid'>", unsafe_allow_html=True)
    
    # 요일 헤더
    for day in weekdays:
        st.markdown(f"<div style='text-align: center; font-weight: bold; color: #999;'>{day}</div>", 
                   unsafe_allow_html=True)
    
    # 날짜
    cal = calendar.monthcalendar(st.session_state.current_year, st.session_state.current_month)
    today = datetime.now()
    
    for week in cal:
        cols = st.columns(7)
        for idx, day in enumerate(week):
            with cols[idx]:
                if day == 0:
                    st.write("")
                else:
                    date = datetime(st.session_state.current_year, st.session_state.current_month, day)
                    is_today = date.date() == today.date()
                    
                    if st.button(str(day), key=f"cal_{st.session_state.current_year}_{st.session_state.current_month}_{day}",
                               type="primary" if is_today else "secondary",
                               use_container_width=True):
                        # 선택한 날짜의 주 월요일로 이동
                        weekday = date.weekday()
                        monday = date - timedelta(days=weekday)
                        st.session_state.selected_week_start = monday
                        st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

with col_nav:
    # 주간 네비게이션
    nav_cols = st.columns([1, 3, 1])
    
    with nav_cols[0]:
        if st.button("◀ 이전주", use_container_width=True):
            st.session_state.selected_week_start -= timedelta(days=7)
            st.rerun()
    
    with nav_cols[1]:
        week_start = st.session_state.selected_week_start
        week_end = week_start + timedelta(days=4)
        st.markdown(f"<div style='text-align: center; color: white; font-weight: bold; padding: 10px;'>"
                   f"{week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d')}</div>", 
                   unsafe_allow_html=True)
    
    with nav_cols[2]:
        if st.button("다음주 ▶", use_container_width=True):
            st.session_state.selected_week_start += timedelta(days=7)
            st.rerun()

# 주간 뷰
if st.session_state.timetable:
    st.markdown("<div class='week-container'>", unsafe_allow_html=True)
    
    days = ["월", "화", "수", "목", "금"]
    cols = st.columns(5)
    
    week_start = st.session_state.selected_week_start
    
    for day_idx, (col, day_name) in enumerate(zip(cols, days)):
        with col:
            date = week_start + timedelta(days=day_idx)
            tt_day_idx = day_idx + 1  # pycomcigan 인덱스
            
            st.markdown(f"""
            <div class='day-column'>
                <div class='day-header'>{day_name}</div>
                <div class='day-date'>{date.strftime('%m/%d')}</div>
            """, unsafe_allow_html=True)
            
            # 시간표 (1반만 대표로 간단하게)
            try:
                grade_data = st.session_state.timetable.timetable[st.session_state.grade]
                if grade_data and len(grade_data) > 1:
                    class_data = grade_data[1]
                    if tt_day_idx < len(class_data):
                        day_schedule = class_data[tt_day_idx]
                        
                        if day_schedule and len(day_schedule) > 0:
                            st.markdown("<div class='timetable-section'><div class='section-title'>📚 시간표 (1반)</div>", 
                                      unsafe_allow_html=True)
                            
                            # 처음 5교시만 표시
                            for period_data in day_schedule[:5]:
                                if period_data and hasattr(period_data, 'subject'):
                                    subject = period_data.subject[:6]
                                    teacher = period_data.teacher[:4]
                                    st.markdown(f"<div class='class-item'>{period_data.period}. {subject} ({teacher})</div>", 
                                              unsafe_allow_html=True)
                            
                            st.markdown("</div>", unsafe_allow_html=True)
            except:
                pass
            
            # 급식
            if st.session_state.meal_data and date.day in st.session_state.meal_data:
                meals = st.session_state.meal_data[date.day]
                
                if 'lunch' in meals:
                    lunch = meals['lunch']
                    menu = lunch.get('menu', '')
                    # 첫 3개 메뉴만
                    menu_items = menu.split('\n')[:3]
                    short_menu = '<br>'.join(menu_items)
                    
                    st.markdown(f"""
                    <div class='meal-section'>
                        <div class='meal-title'>🍽️ 중식</div>
                        <div class='meal-menu'>{short_menu}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 전체 학년 버튼
    if st.button("📋 전체 학년 시간표 보기", use_container_width=True):
        with st.expander("전체 학년 시간표", expanded=True):
            for day_idx, day_name in enumerate(days):
                date = week_start + timedelta(days=day_idx)
                tt_day_idx = day_idx + 1
                
                st.markdown(f"### {day_name}요일 ({date.strftime('%m/%d')})")
                
                try:
                    grade_data = st.session_state.timetable.timetable[st.session_state.grade]
                    max_classes = len(grade_data)
                    
                    cols = st.columns(min(4, max_classes - 1))
                    
                    for col_idx, col in enumerate(cols):
                        class_num = col_idx + 1
                        if class_num < max_classes:
                            with col:
                                st.markdown(f"**{class_num}반**")
                                
                                try:
                                    class_data = grade_data[class_num]
                                    if tt_day_idx < len(class_data):
                                        day_schedule = class_data[tt_day_idx]
                                        
                                        if day_schedule:
                                            for period_data in day_schedule[:6]:
                                                if period_data and hasattr(period_data, 'subject'):
                                                    st.text(f"{period_data.period}. {period_data.subject}")
                                except:
                                    st.text("데이터 없음")
                except:
                    st.error("시간표를 불러올 수 없습니다")
                
                st.divider()

else:
    st.info("학교명을 입력하고 🔄 버튼을 클릭하세요")

# 푸터
st.markdown("<div style='text-align: center; color: white; padding: 10px; font-size: 0.8em;'>📚 학교 현황판</div>", 
           unsafe_allow_html=True)
