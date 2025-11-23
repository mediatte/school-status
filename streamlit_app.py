import streamlit as st
import pycomcigan
from datetime import datetime
import time
from neis_meal import NeisAPI, search_school_by_name, get_today_meal_simple

# 페이지 설정
st.set_page_config(
    page_title="실시간 학교 시간표",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
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
    div[data-testid="stMetricValue"] {
        font-size: 20px;
    }
    .timetable-header {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .subject-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .teacher-info {
        color: #666;
        font-size: 0.9em;
        margin-top: 5px;
    }
    .homeroom-teacher {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .meal-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #ff6b6b;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    .meal-type {
        color: #ff6b6b;
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 10px;
    }
    .meal-menu {
        line-height: 1.8;
        color: #333;
        white-space: pre-line;
    }
    .meal-info {
        color: #888;
        font-size: 0.9em;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'timetable' not in st.session_state:
    st.session_state.timetable = None
if 'school_name' not in st.session_state:
    st.session_state.school_name = ""
if 'grade' not in st.session_state:
    st.session_state.grade = 1
if 'class_num' not in st.session_state:
    st.session_state.class_num = 1
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'meal_data' not in st.session_state:
    st.session_state.meal_data = None
if 'show_meal' not in st.session_state:
    st.session_state.show_meal = False
if 'neis_school_info' not in st.session_state:
    st.session_state.neis_school_info = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "개별 반"

# 타이틀
st.markdown("<h1 style='text-align: center; color: white;'>📚 실시간 학교 시간표</h1>", unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 학교 검색
    school_search = st.text_input("🏫 학교명 검색", 
                                  placeholder="예: 고운고등학교")
    
    if school_search:
        try:
            schools = pycomcigan.get_school_code(school_search)
            
            if schools:
                st.success(f"✅ {len(schools)}개 학교 검색됨")
                
                # 학교 선택
                # pycomcigan 데이터 구조: [학교코드, 지역명, 학교명, 지역코드]
                school_options = [f"{school[2]} ({school[1]})" for school in schools]
                selected_school_idx = st.selectbox(
                    "학교 선택",
                    range(len(school_options)),
                    format_func=lambda x: school_options[x]
                )
                
                selected_school = schools[selected_school_idx]
                # 학교명을 문자열로 확실하게 저장 (인덱스 2가 학교명)
                st.session_state.school_name = str(selected_school[2])
                
                st.info(f"📍 **선택된 학교**: {selected_school[2]}\n\n**지역**: {selected_school[1]}")
            else:
                st.warning("⚠️ 검색 결과가 없습니다.")
        except Exception as e:
            st.error(f"❌ 검색 오류: {str(e)}")
    
    st.divider()
    
    # 학년/반 선택
    st.session_state.view_mode = st.radio("📊 보기 모드", ["개별 반", "전체 학년"], horizontal=True, index=0 if st.session_state.view_mode == "개별 반" else 1)
    
    col1, col2 = st.columns(2)
    with col1:
        grade = st.number_input("📖 학년", min_value=1, max_value=3, value=st.session_state.grade)
        st.session_state.grade = grade
    
    with col2:
        if st.session_state.view_mode == "개별 반":
            class_num = st.number_input("🏛️ 반", min_value=1, max_value=20, value=st.session_state.class_num)
            st.session_state.class_num = class_num
        else:
            st.info("전체 학년 모드")
            st.session_state.class_num = 1  # 기본값
    
    st.divider()
    
    # 주차 선택
    week_num = st.radio("📅 주차 선택", [0, 1], format_func=lambda x: "이번 주" if x == 0 else "다음 주")
    
    st.divider()
    
    # 자동 새로고침 설정
    auto_refresh = st.checkbox("🔄 자동 새로고침", value=True)
    if auto_refresh:
        refresh_interval = st.slider("새로고침 간격 (초)", 10, 300, 60)
    
    st.divider()
    
    # 시간표 불러오기 버튼
    if st.button("📥 시간표 불러오기", type="primary", use_container_width=True):
        if st.session_state.school_name:
            with st.spinner("시간표를 불러오는 중..."):
                try:
                    timetable = pycomcigan.TimeTable(st.session_state.school_name, week_num=week_num)
                    st.session_state.timetable = timetable
                    st.session_state.last_update = datetime.now()
                    st.success("✅ 시간표를 성공적으로 불러왔습니다!")
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")
        else:
            st.warning("⚠️ 학교를 먼저 선택해주세요!")
    
    # 급식 불러오기 버튼
    if st.button("🍽️ 급식 불러오기", use_container_width=True):
        if st.session_state.school_name:
            with st.spinner("급식 정보를 불러오는 중..."):
                try:
                    neis_api = NeisAPI()
                    
                    # 학교명을 문자열로 변환 및 정제 (괄호 제거)
                    import re
                    school_name_str = str(st.session_state.school_name)
                    clean_school_name = re.sub(r'\s*\([^)]*\)', '', school_name_str).strip()
                    
                    # NEIS에서 학교 검색
                    neis_schools = neis_api.search_school(clean_school_name)
                    
                    if neis_schools:
                        neis_school = neis_schools[0]
                        st.session_state.neis_school_info = neis_school
                        
                        school_code = neis_school.get("SD_SCHUL_CODE", "")
                        atpt_code = neis_school.get("ATPT_OFCDC_SC_CODE", "")
                        
                        # 이번 주 급식 정보 가져오기
                        meal_data = neis_api.get_week_meal(school_code, atpt_code)
                        st.session_state.meal_data = meal_data
                        st.session_state.show_meal = True
                        st.success(f"✅ 급식 정보를 성공적으로 불러왔습니다! ({neis_school.get('SCHUL_NM', '')})")
                    else:
                        st.error(f"❌ NEIS에서 '{clean_school_name}' 학교를 찾을 수 없습니다.")
                        st.info("💡 학교명을 정확히 입력했는지 확인해주세요. 예: '고운고등학교'")
                except Exception as e:
                    st.error(f"❌ 급식 정보 오류: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
        else:
            st.warning("⚠️ 학교를 먼저 선택해주세요!")

# 메인 영역
if st.session_state.timetable is not None:
    timetable = st.session_state.timetable
    
    # 헤더 정보
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="timetable-header">
            <h3 style='color: #667eea; margin: 0;'>🏫 학교</h3>
            <p style='font-size: 1.2em; margin: 5px 0;'>{}</p>
        </div>
        """.format(st.session_state.school_name), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="timetable-header">
            <h3 style='color: #667eea; margin: 0;'>👥 학년/반</h3>
            <p style='font-size: 1.2em; margin: 5px 0;'>{}학년 {}반</p>
        </div>
        """.format(st.session_state.grade, st.session_state.class_num), unsafe_allow_html=True)
    
    with col3:
        if st.session_state.last_update:
            update_time = st.session_state.last_update.strftime("%Y-%m-%d %H:%M:%S")
        else:
            update_time = "-"
        
        st.markdown("""
        <div class="timetable-header">
            <h3 style='color: #667eea; margin: 0;'>🕐 마지막 업데이트</h3>
            <p style='font-size: 0.9em; margin: 5px 0;'>{}</p>
        </div>
        """.format(update_time), unsafe_allow_html=True)
    
    # 담임 선생님 정보
    try:
        homeroom_teacher = timetable.homeroom(st.session_state.grade, st.session_state.class_num)
        if homeroom_teacher:
            st.markdown("""
            <div class="homeroom-teacher">
                <h4 style='color: #667eea; margin: 0 0 10px 0;'>👨‍🏫 담임 선생님</h4>
                <p style='font-size: 1.1em; margin: 0;'>{}</p>
            </div>
            """.format(homeroom_teacher), unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"담임 정보를 불러올 수 없습니다: {str(e)}")
    
    st.divider()
    
    # 시간표/급식 탭
    main_tabs = st.tabs(["📅 시간표", "🍽️ 급식"])
    
    # 시간표 탭
    with main_tabs[0]:
        st.markdown("<h2 style='color: white; text-align: center;'>📅 주간 시간표</h2>", unsafe_allow_html=True)
        
        try:
            # 요일 정보
            days = ["월요일", "화요일", "수요일", "목요일", "금요일"]
            
            # 보기 모드 확인 (세션에서 가져오기)
            if st.session_state.view_mode == "전체 학년":
                # 전체 학년 모드
                st.markdown(f"<h3 style='color: white; text-align: center;'>{st.session_state.grade}학년 전체 시간표</h3>", unsafe_allow_html=True)
                
                # 반별로 표시
                grade_timetable = timetable.timetable[st.session_state.grade]
                
                # 탭으로 요일별 표시
                tabs = st.tabs(days)
                
                for day_idx, tab in enumerate(tabs):
                    with tab:
                        # 모든 반을 열로 표시
                        max_classes = len(grade_timetable)
                        
                        if max_classes > 0:
                            # 최대 4개 반씩 한 행에 표시
                            for row_start in range(1, max_classes + 1, 4):
                                cols = st.columns(min(4, max_classes - row_start + 1))
                                
                                for col_idx, col in enumerate(cols):
                                    class_num = row_start + col_idx
                                    if class_num <= max_classes:
                                        with col:
                                            st.markdown(f"### {class_num}반")
                                            
                                            try:
                                                class_schedule = grade_timetable[class_num]
                                                if day_idx < len(class_schedule):
                                                    day_schedule = class_schedule[day_idx]
                                                    
                                                    if day_schedule:
                                                        for period_idx, subject in enumerate(day_schedule, start=1):
                                                            subject_str = str(subject) if subject else ""
                                                            
                                                            if subject and subject_str.strip():
                                                                subject_name = subject_str.split('\n')[0] if '\n' in subject_str else subject_str
                                                                st.markdown(f"**{period_idx}.** {subject_name}")
                                                            else:
                                                                st.markdown(f"**{period_idx}.** -")
                                                    else:
                                                        st.info("시간표 없음")
                                            except Exception as e:
                                                st.warning(f"데이터 없음")
            else:
                # 개별 반 모드
                class_timetable = timetable.timetable[st.session_state.grade][st.session_state.class_num]
                
                # 탭으로 요일별 표시
                tabs = st.tabs(days)
                
                for day_idx, tab in enumerate(tabs):
                    with tab:
                        if day_idx < len(class_timetable):
                            day_schedule = class_timetable[day_idx]
                            
                            if day_schedule:
                                # 교시별로 표시
                                for period_idx, subject in enumerate(day_schedule, start=1):
                                    # subject를 문자열로 변환
                                    subject_str = str(subject) if subject else ""
                                    
                                    if subject and subject_str.strip():
                                        # 과목명과 교사명 분리 (있는 경우)
                                        subject_info = subject_str.split('\n') if '\n' in subject_str else [subject_str]
                                        subject_name = subject_info[0]
                                        teacher_name = subject_info[1] if len(subject_info) > 1 else ""
                                        
                                        st.markdown(f"""
                                        <div class="subject-card">
                                            <strong>{period_idx}교시</strong>
                                            <h4 style='color: #667eea; margin: 5px 0;'>{subject_name}</h4>
                                            {f'<p class="teacher-info">👨‍🏫 {teacher_name}</p>' if teacher_name else ''}
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"""
                                        <div class="subject-card" style="background: #f8f9fa; opacity: 0.6;">
                                            <strong>{period_idx}교시</strong>
                                            <p style='color: #999; margin: 5px 0;'>수업 없음</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                            else:
                                st.info("📭 이 날은 시간표가 없습니다.")
                        else:
                            st.warning("⚠️ 시간표 정보를 불러올 수 없습니다.")
                        
        except Exception as e:
            st.error(f"❌ 시간표 표시 오류: {str(e)}")
            st.info("💡 학년/반 정보를 확인하거나 시간표를 다시 불러와주세요.")
            import traceback
            st.code(traceback.format_exc())
    
    # 급식 탭
    with main_tabs[1]:
        st.markdown("<h2 style='color: white; text-align: center;'>🍽️ 주간 급식</h2>", unsafe_allow_html=True)
        
        if st.session_state.meal_data:
            meal_data = st.session_state.meal_data
            
            # 요일별 탭
            meal_days = ["월", "화", "수", "목", "금"]
            meal_tabs = st.tabs(meal_days)
            
            for day_idx, (day_name, meal_tab) in enumerate(zip(meal_days, meal_tabs)):
                with meal_tab:
                    day_info = meal_data.get(day_name, {})
                    date_str = day_info.get("date", "")
                    meals = day_info.get("meals", {})
                    
                    if date_str:
                        st.markdown(f"<p style='color: white; text-align: center;'>📅 {date_str}</p>", unsafe_allow_html=True)
                    
                    if meals:
                        # 조식, 중식, 석식
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
                                origin = meal_info.get("origin", "")
                                
                                st.markdown(f"""
                                <div class="meal-card" style="border-left-color: {meal_color};">
                                    <div class="meal-type" style="color: {meal_color};">{meal_label}</div>
                                    <div class="meal-menu">{menu}</div>
                                    {f'<div class="meal-info">🔥 {calories}</div>' if calories else ''}
                                    {f'<div class="meal-info">📍 원산지<br>{origin}</div>' if origin else ''}
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if not any(meal_type in meals for meal_type in meal_types.keys()):
                            st.info("📭 이 날은 급식 정보가 없습니다.")
                    else:
                        st.info("📭 이 날은 급식 정보가 없습니다.")
        else:
            st.markdown("""
            <div style='text-align: center; padding: 40px; background: white; border-radius: 15px; margin: 20px 0;'>
                <h3 style='color: #667eea;'>🍽️ 급식 정보</h3>
                <p style='color: #666; margin: 20px 0;'>
                    사이드바에서 <strong>"급식 불러오기"</strong> 버튼을 클릭하여<br>
                    이번 주 급식 정보를 확인하세요.
                </p>
                <p style='color: #999; font-size: 0.9em;'>
                    💡 NEIS(나이스) 오픈API를 활용합니다.
                </p>
            </div>
            """, unsafe_allow_html=True)

else:
    # 시간표가 없을 때 안내 메시지
    st.markdown("""
    <div style='text-align: center; padding: 50px; background: white; border-radius: 20px; margin: 50px auto; max-width: 600px;'>
        <h2 style='color: #667eea;'>👋 환영합니다!</h2>
        <p style='font-size: 1.1em; color: #666; margin: 20px 0;'>
            왼쪽 사이드바에서 학교를 검색하고<br>
            학년과 반을 선택한 후<br>
            <strong>"시간표 불러오기"</strong> 버튼을 클릭하세요.
        </p>
        <p style='color: #999;'>
            💡 컴시간알리미에 등록된 학교만 검색 가능합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

# 자동 새로고침 기능
if auto_refresh and st.session_state.timetable is not None:
    time.sleep(refresh_interval)
    st.rerun()

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 20px;'>
    <p>📚 <strong>실시간 학교 시간표 & 급식</strong> | Powered by <a href='https://github.com/hegelty/pycomcigan' style='color: white;'>pycomcigan</a> & <a href='https://github.com/alvin0319/NeisAPI' style='color: white;'>NEIS API</a> & Streamlit</p>
    <p style='font-size: 0.9em; opacity: 0.8;'>컴시간알리미 & 나이스 오픈API 데이터를 기반으로 합니다</p>
</div>
""", unsafe_allow_html=True)

