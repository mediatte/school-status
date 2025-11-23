import streamlit as st
import pycomcigan
from datetime import datetime, timedelta
import time
from neis_meal import NeisAPI
import re
import calendar

# 페이지 설정
st.set_page_config(
    page_title="고운고등학교 현황",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-title {
        text-align: center;
        color: white;
        font-size: clamp(1.5rem, 5vw, 3rem);
        font-weight: bold;
        margin: 20px 0;
        white-space: nowrap;
    }
    .calendar-container {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .calendar-header {
        text-align: center;
        color: #667eea;
        font-size: 1.8em;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 10px;
        margin-top: 10px;
    }
    .day-header {
        text-align: center;
        font-weight: bold;
        color: #667eea;
        padding: 10px;
        background: #f0f2f6;
        border-radius: 8px;
    }
    .day-header.sunday {
        color: #ff6b6b;
    }
    .day-header.saturday {
        color: #4dabf7;
    }
    .day-cell {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 10px;
        min-height: 120px;
        border: 2px solid #e9ecef;
        cursor: pointer;
        transition: all 0.3s;
    }
    .day-cell:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-color: #667eea;
    }
    .day-cell.today {
        border-color: #667eea;
        background: #e7f5ff;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    .day-cell.weekend {
        background: #f1f3f5;
    }
    .day-cell.other-month {
        opacity: 0.3;
    }
    .day-number {
        font-weight: bold;
        font-size: 1.1em;
        color: #495057;
        margin-bottom: 5px;
    }
    .day-cell.today .day-number {
        color: #667eea;
    }
    .day-content {
        font-size: 0.85em;
        color: #666;
        line-height: 1.4;
    }
    .meal-indicator {
        background: #ffe3e3;
        color: #ff6b6b;
        padding: 3px 6px;
        border-radius: 4px;
        font-size: 0.75em;
        display: inline-block;
        margin: 2px 0;
    }
    .class-indicator {
        background: #e3f2ff;
        color: #667eea;
        padding: 3px 6px;
        border-radius: 4px;
        font-size: 0.75em;
        display: inline-block;
        margin: 2px 0;
    }
    .detail-box {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .detail-title {
        color: #667eea;
        font-size: 1.5em;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .class-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    .meal-box {
        background: #fff5f5;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #ff6b6b;
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
if 'current_month' not in st.session_state:
    st.session_state.current_month = datetime.now().month
if 'current_year' not in st.session_state:
    st.session_state.current_year = datetime.now().year
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = None

# 타이틀
st.markdown("<h1 class='main-title'>📚 학교 현황</h1>", unsafe_allow_html=True)

# 상단 설정 바
col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
with col1:
    school_name = st.text_input("🏫 학교명", value=st.session_state.school_name, 
                                key="school_input",
                                placeholder="학교명을 입력하세요",
                                label_visibility="collapsed")
    if school_name:
        st.session_state.school_name = school_name

with col2:
    grade = st.selectbox("📖 학년", [1, 2, 3], 
                        index=st.session_state.grade - 1,
                        key="grade_select",
                        label_visibility="collapsed")
    st.session_state.grade = grade

with col3:
    # 월 선택
    month = st.selectbox("📅 월", list(range(1, 13)),
                        index=st.session_state.current_month - 1,
                        format_func=lambda x: f"{x}월",
                        label_visibility="collapsed")
    st.session_state.current_month = month

with col4:
    if st.button("🔄 새로고침", use_container_width=True, type="primary"):
        st.session_state.initialized = False
        st.cache_data.clear()
        st.rerun()

# 데이터 로딩 함수
@st.cache_data(ttl=600)
def load_timetable(school_name, week_num=0):
    """시간표 로드"""
    try:
        return pycomcigan.TimeTable(school_name, week_num=week_num)
    except Exception as e:
        return None

@st.cache_data(ttl=600)
def load_meals_monthly(school_name, year, month):
    """월간 급식 로드"""
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
    except Exception as e:
        return None

# 초기 데이터 로드
if not st.session_state.initialized and st.session_state.school_name:
    with st.spinner("데이터를 불러오는 중..."):
        st.session_state.timetable = load_timetable(st.session_state.school_name)
        st.session_state.meal_data = load_meals_monthly(
            st.session_state.school_name, 
            st.session_state.current_year, 
            st.session_state.current_month
        )
        st.session_state.last_update = datetime.now()
        st.session_state.initialized = True

# 달력 생성 함수
def create_calendar_view(year, month, timetable, meal_data, grade):
    """달력 형태의 UI 생성"""
    
    # 달력 헤더
    st.markdown(f"""
    <div class='calendar-container'>
        <div class='calendar-header'>{year}년 {month}월</div>
    """, unsafe_allow_html=True)
    
    # 요일 헤더
    weekdays = ['일', '월', '화', '수', '목', '금', '토']
    cols = st.columns(7)
    for idx, day in enumerate(weekdays):
        with cols[idx]:
            if idx == 0:  # 일요일
                st.markdown(f"<div class='day-header sunday'>{day}</div>", unsafe_allow_html=True)
            elif idx == 6:  # 토요일
                st.markdown(f"<div class='day-header saturday'>{day}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='day-header'>{day}</div>", unsafe_allow_html=True)
    
    # 달력 날짜 계산
    cal = calendar.monthcalendar(year, month)
    today = datetime.now()
    
    for week in cal:
        cols = st.columns(7)
        for idx, day in enumerate(week):
            with cols[idx]:
                if day == 0:
                    # 빈 날짜
                    st.markdown("<div class='day-cell other-month'></div>", unsafe_allow_html=True)
                else:
                    # 날짜 객체 생성
                    date = datetime(year, month, day)
                    weekday = date.weekday()  # 0=월요일
                    
                    # 클래스 결정
                    classes = ['day-cell']
                    if date.date() == today.date():
                        classes.append('today')
                    if weekday >= 5:  # 토요일, 일요일
                        classes.append('weekend')
                    
                    # 요일 인덱스 (pycomcigan: 1=월, 2=화, ...)
                    tt_day_idx = weekday + 1 if weekday < 5 else None
                    
                    # 시간표 정보
                    has_timetable = False
                    first_class = ""
                    if timetable and tt_day_idx and weekday < 5:  # 평일만
                        try:
                            grade_data = timetable.timetable[grade]
                            if grade_data and len(grade_data) > 1:
                                class_data = grade_data[1]  # 1반 대표로
                                if tt_day_idx < len(class_data):
                                    day_schedule = class_data[tt_day_idx]
                                    if day_schedule and len(day_schedule) > 0:
                                        has_timetable = True
                                        first_period = day_schedule[0]
                                        if hasattr(first_period, 'subject'):
                                            first_class = first_period.subject[:4]
                        except:
                            pass
                    
                    # 급식 정보
                    has_meal = False
                    if meal_data and day in meal_data:
                        day_meals = meal_data[day]
                        if day_meals and 'lunch' in day_meals:
                            has_meal = True
                    
                    # 버튼으로 날짜 표시
                    button_label = f"{day}일"
                    if has_timetable:
                        button_label += f"\n📚 {first_class}"
                    if has_meal:
                        button_label += "\n🍽️"
                    
                    if st.button(button_label, key=f"day_{year}_{month}_{day}", 
                               use_container_width=True, 
                               type="primary" if date.date() == today.date() else "secondary"):
                        st.session_state.selected_date = date
                        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# 선택된 날짜의 상세 정보 표시
def show_date_details(date, timetable, meal_data, grade):
    """선택된 날짜의 상세 시간표와 급식 표시"""
    
    weekday = date.weekday()
    weekday_name = ['월', '화', '수', '목', '금', '토', '일'][weekday]
    
    st.markdown(f"""
    <div class='detail-box'>
        <div class='detail-title'>{date.strftime('%Y년 %m월 %d일')} ({weekday_name}요일)</div>
    </div>
    """, unsafe_allow_html=True)
    
    if weekday >= 5:  # 주말
        st.info("📅 주말입니다.")
        return
    
    col1, col2 = st.columns([3, 1])
    
    # 시간표
    with col1:
        st.markdown("<div class='detail-box'><h3 style='color: #667eea;'>📚 시간표</h3></div>", 
                   unsafe_allow_html=True)
        
        tt_day_idx = weekday + 1  # pycomcigan 인덱스
        
        try:
            grade_data = timetable.timetable[grade]
            max_classes = len(grade_data)
            
            # 4개씩 열로 표시
            for row_start in range(1, max_classes + 1, 4):
                cols = st.columns(min(4, max_classes - row_start + 1))
                
                for col_idx, col in enumerate(cols):
                    class_num = row_start + col_idx
                    if class_num <= max_classes:
                        with col:
                            st.markdown(f"<div class='class-box'><strong>{class_num}반</strong><br>", 
                                      unsafe_allow_html=True)
                            
                            try:
                                class_data = grade_data[class_num]
                                if tt_day_idx < len(class_data):
                                    day_schedule = class_data[tt_day_idx]
                                    
                                    if day_schedule:
                                        schedule_html = ""
                                        for period_data in day_schedule:
                                            if period_data and hasattr(period_data, 'subject'):
                                                subject = period_data.subject
                                                teacher = period_data.teacher
                                                period_num = period_data.period
                                                schedule_html += f"{period_num}. {subject} ({teacher})<br>"
                                        
                                        st.markdown(schedule_html + "</div>", unsafe_allow_html=True)
                                    else:
                                        st.markdown("시간표 없음</div>", unsafe_allow_html=True)
                            except:
                                st.markdown("데이터 없음</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"시간표를 불러올 수 없습니다: {str(e)}")
    
    # 급식
    with col2:
        st.markdown("<div class='detail-box'><h3 style='color: #ff6b6b;'>🍽️ 급식</h3></div>", 
                   unsafe_allow_html=True)
        
        if meal_data and date.day in meal_data:
            day_meals = meal_data[date.day]
            
            meal_types = {
                "breakfast": ("🌅 조식", "#ffd93d"),
                "lunch": ("☀️ 중식", "#ff6b6b"),
                "dinner": ("🌙 석식", "#6c5ce7")
            }
            
            for meal_type, (meal_label, meal_color) in meal_types.items():
                if meal_type in day_meals:
                    meal_info = day_meals[meal_type]
                    menu = meal_info.get("menu", "")
                    calories = meal_info.get("calories", "")
                    
                    st.markdown(f"""
                    <div class="meal-box">
                        <strong style="color: {meal_color};">{meal_label}</strong><br>
                        {menu.replace(chr(10), '<br>')}<br>
                        {f'<small>🔥 {calories}</small>' if calories else ''}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("급식 정보가 없습니다.")

# 메인 컨텐츠
if st.session_state.timetable:
    # 마지막 업데이트
    if st.session_state.last_update:
        st.markdown(f"<p style='text-align: center; color: white; font-size: 0.9em;'>마지막 업데이트: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}</p>", 
                   unsafe_allow_html=True)
    
    # 달력 표시
    create_calendar_view(
        st.session_state.current_year,
        st.session_state.current_month,
        st.session_state.timetable,
        st.session_state.meal_data,
        st.session_state.grade
    )
    
    # 선택된 날짜의 상세 정보
    if st.session_state.selected_date:
        show_date_details(
            st.session_state.selected_date,
            st.session_state.timetable,
            st.session_state.meal_data,
            st.session_state.grade
        )

else:
    # 초기 로딩 안내
    st.markdown("""
    <div style='text-align: center; padding: 100px 20px; background: white; border-radius: 20px; margin: 50px auto; max-width: 600px;'>
        <h2 style='color: #667eea;'>👋 환영합니다!</h2>
        <p style='font-size: 1.2em; color: #666; margin: 20px 0;'>
            위에서 학교명과 학년을 선택하고<br>
            <strong>"🔄 새로고침"</strong> 버튼을 클릭하세요.
        </p>
        <p style='color: #999;'>
            💡 달력에서 시간표와 급식을 확인할 수 있습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 20px;'>
    <p>📚 <strong>학교 현황판</strong> | Powered by pycomcigan & NEIS API</p>
</div>
""", unsafe_allow_html=True)
