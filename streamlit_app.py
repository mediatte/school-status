import streamlit as st
import pycomcigan
from datetime import datetime
import time
from neis_meal import NeisAPI
import re

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
    .content-box {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .class-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    .class-header {
        color: #667eea;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 10px;
    }
    .period-item {
        padding: 5px 0;
        border-bottom: 1px solid #eee;
    }
    .period-item:last-child {
        border-bottom: none;
    }
    .meal-box {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 5px solid #ff6b6b;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .meal-header {
        color: #ff6b6b;
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 10px;
    }
    .meal-menu {
        line-height: 1.8;
        color: #333;
    }
    h1, h2, h3 {
        color: white;
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

# 타이틀
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    st.markdown("# 📚 학교 현황")

# 상단 설정 바
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    school_name = st.text_input("🏫 학교명", value=st.session_state.school_name, 
                                key="school_input",
                                placeholder="학교명을 입력하세요")
    if school_name:
        st.session_state.school_name = school_name

with col2:
    grade = st.selectbox("📖 학년", [1, 2, 3], 
                        index=st.session_state.grade - 1,
                        key="grade_select")
    st.session_state.grade = grade

with col3:
    st.write("")
    st.write("")
    if st.button("🔄 새로고침", use_container_width=True, type="primary"):
        st.session_state.initialized = False
        st.rerun()

st.markdown("---")

# 데이터 로딩 함수
@st.cache_data(ttl=600)
def load_timetable(school_name, week_num=0):
    """시간표 로드"""
    try:
        return pycomcigan.TimeTable(school_name, week_num=week_num)
    except Exception as e:
        st.error(f"시간표 로드 실패: {str(e)}")
        return None

@st.cache_data(ttl=600)
def load_meals(school_name):
    """급식 로드"""
    try:
        neis_api = NeisAPI()
        clean_name = re.sub(r'\s*\([^)]*\)', '', school_name).strip()
        schools = neis_api.search_school(clean_name)
        
        if schools:
            school = schools[0]
            school_code = school.get("SD_SCHUL_CODE", "")
            atpt_code = school.get("ATPT_OFCDC_SC_CODE", "")
            return neis_api.get_week_meal(school_code, atpt_code)
        return None
    except Exception as e:
        st.error(f"급식 로드 실패: {str(e)}")
        return None

# 초기 데이터 로드
if not st.session_state.initialized and st.session_state.school_name:
    with st.spinner("데이터를 불러오는 중..."):
        st.session_state.timetable = load_timetable(st.session_state.school_name)
        st.session_state.meal_data = load_meals(st.session_state.school_name)
        st.session_state.last_update = datetime.now()
        st.session_state.initialized = True

# 메인 컨텐츠
if st.session_state.timetable and st.session_state.meal_data:
    # 마지막 업데이트 시간
    if st.session_state.last_update:
        st.markdown(f"<p style='text-align: center; color: white;'>마지막 업데이트: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}</p>", 
                   unsafe_allow_html=True)
    
    # 요일 탭 (월~금)
    days = ["월요일", "화요일", "수요일", "목요일", "금요일"]
    day_keys = ["월", "화", "수", "목", "금"]
    
    tabs = st.tabs(days)
    
    timetable = st.session_state.timetable
    meal_data = st.session_state.meal_data
    
    for day_idx, (tab, day_key) in enumerate(zip(tabs, day_keys)):
        with tab:
            # 2열 레이아웃: 시간표 | 급식
            col_timetable, col_meal = st.columns([3, 1])
            
            # 시간표 영역
            with col_timetable:
                st.markdown(f"<div class='content-box'><h2 style='color: #667eea;'>{days[day_idx]} 시간표</h2></div>", 
                           unsafe_allow_html=True)
                
                try:
                    grade_timetable = timetable.timetable[st.session_state.grade]
                    
                    # 모든 반의 시간표를 4개씩 열로 표시
                    max_classes = len(grade_timetable)
                    
                    for row_start in range(1, max_classes + 1, 4):
                        cols = st.columns(min(4, max_classes - row_start + 1))
                        
                        for col_idx, col in enumerate(cols):
                            class_num = row_start + col_idx
                            if class_num <= max_classes:
                                with col:
                                    st.markdown(f"<div class='class-box'><div class='class-header'>{class_num}반</div>", 
                                              unsafe_allow_html=True)
                                    
                                    try:
                                        class_schedule = grade_timetable[class_num]
                                        if day_idx < len(class_schedule):
                                            day_schedule = class_schedule[day_idx]
                                            
                                            if day_schedule:
                                                schedule_html = ""
                                                for period_idx, subject in enumerate(day_schedule, start=1):
                                                    subject_str = str(subject) if subject else "-"
                                                    if '\n' in subject_str:
                                                        subject_str = subject_str.split('\n')[0]
                                                    
                                                    schedule_html += f"<div class='period-item'><strong>{period_idx}교시:</strong> {subject_str}</div>"
                                                
                                                st.markdown(schedule_html, unsafe_allow_html=True)
                                            else:
                                                st.info("시간표 없음")
                                        else:
                                            st.info("시간표 없음")
                                    except Exception as e:
                                        st.warning(f"데이터 오류")
                                    
                                    st.markdown("</div>", unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"시간표 표시 오류: {str(e)}")
            
            # 급식 영역
            with col_meal:
                st.markdown(f"<div class='content-box'><h2 style='color: #ff6b6b;'>{days[day_idx]} 급식</h2></div>", 
                           unsafe_allow_html=True)
                
                day_info = meal_data.get(day_key, {})
                meals = day_info.get("meals", {})
                date_str = day_info.get("date", "")
                
                if date_str:
                    st.markdown(f"<p style='text-align: center; color: #999; font-size: 0.9em;'>{date_str}</p>", 
                              unsafe_allow_html=True)
                
                if meals:
                    meal_types = {
                        "breakfast": ("🌅 조식", "#ffd93d"),
                        "lunch": ("☀️ 중식", "#ff6b6b"),
                        "dinner": ("🌙 석식", "#6c5ce7")
                    }
                    
                    for meal_type, (meal_label, meal_color) in meal_types.items():
                        if meal_type in meals:
                            meal_info = meals[meal_type]
                            menu = meal_info.get("menu", "")
                            calories = meal_info.get("calories", "")
                            
                            st.markdown(f"""
                            <div class="meal-box" style="border-left-color: {meal_color};">
                                <div class="meal-header" style="color: {meal_color};">{meal_label}</div>
                                <div class="meal-menu">{menu}</div>
                                {f'<p style="color: #888; margin-top: 10px;">🔥 {calories}</p>' if calories else ''}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("급식 정보 없음")

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
            💡 시간표와 급식 정보가 자동으로 표시됩니다.
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

# 자동 새로고침 (10분마다)
time.sleep(0.1)
