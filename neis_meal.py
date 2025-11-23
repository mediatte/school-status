"""
NEIS(나이스) 오픈API를 활용한 학교 급식 조회 모듈

참고: https://github.com/alvin0319/NeisAPI
나이스 오픈API: https://open.neis.go.kr/portal/data/service/selectServicePage.do?page=1&rows=10&sortColumn=&sortDirection=&infId=OPEN17320190722180924242823&infSeq=2
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import urllib.parse


class NeisSchoolType:
    """학교 유형"""
    ELEMENTARY = "1"  # 초등학교
    MIDDLE = "2"      # 중학교
    HIGH = "3"        # 고등학교
    SPECIAL = "4"     # 특수학교


class NeisAPI:
    """NEIS 오픈 API 클래스"""
    
    BASE_URL = "https://open.neis.go.kr/hub"
    
    def __init__(self, api_key: str = ""):
        """
        NEIS API 초기화
        
        Args:
            api_key: NEIS 오픈API 인증키 (선택사항, 없으면 샘플키 사용)
        """
        self.api_key = api_key if api_key else ""
    
    def search_school(self, school_name: str, school_type: Optional[str] = None) -> List[Dict]:
        """
        학교 검색
        
        Args:
            school_name: 학교명
            school_type: 학교 유형 (초/중/고/특수)
        
        Returns:
            학교 정보 리스트
        """
        url = f"{self.BASE_URL}/schoolInfo"
        
        params = {
            "KEY": self.api_key,
            "Type": "json",
            "pIndex": 1,
            "pSize": 100,
            "SCHUL_NM": school_name
        }
        
        if school_type:
            params["SCHUL_KND_SC_NM"] = school_type
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # API 응답 처리
            if "schoolInfo" in data:
                schools = data["schoolInfo"][1]["row"]
                return schools
            else:
                return []
                
        except Exception as e:
            print(f"학교 검색 오류: {e}")
            return []
    
    def get_meal(self, school_code: str, atpt_ofcdc_sc_code: str, 
                 year: int, month: int, day: Optional[int] = None) -> Dict[int, Dict]:
        """
        급식 정보 조회
        
        Args:
            school_code: 표준학교코드 (SD_SCHUL_CODE)
            atpt_ofcdc_sc_code: 시도교육청코드 (ATPT_OFCDC_SC_CODE)
            year: 년도
            month: 월
            day: 일 (선택사항, 없으면 한 달 전체)
        
        Returns:
            날짜별 급식 정보 딕셔너리
        """
        url = f"{self.BASE_URL}/mealServiceDietInfo"
        
        # 날짜 형식: YYYYMMDD
        if day:
            mlsv_ymd = f"{year}{month:02d}{day:02d}"
        else:
            # 해당 월의 시작일과 마지막일
            mlsv_from_ymd = f"{year}{month:02d}01"
            
            # 마지막 날 계산
            if month == 12:
                next_month = datetime(year + 1, 1, 1)
            else:
                next_month = datetime(year, month + 1, 1)
            last_day = (next_month - timedelta(days=1)).day
            mlsv_to_ymd = f"{year}{month:02d}{last_day:02d}"
        
        params = {
            "KEY": self.api_key,
            "Type": "json",
            "pIndex": 1,
            "pSize": 100,
            "ATPT_OFCDC_SC_CODE": atpt_ofcdc_sc_code,
            "SD_SCHUL_CODE": school_code,
        }
        
        if day:
            params["MLSV_YMD"] = mlsv_ymd
        else:
            params["MLSV_FROM_YMD"] = mlsv_from_ymd
            params["MLSV_TO_YMD"] = mlsv_to_ymd
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            meal_dict = {}
            
            # API 응답 처리
            if "mealServiceDietInfo" in data:
                meals = data["mealServiceDietInfo"][1]["row"]
                
                for meal in meals:
                    meal_date = meal.get("MLSV_YMD", "")
                    meal_day = int(meal_date[6:8]) if len(meal_date) == 8 else 0
                    
                    if meal_day not in meal_dict:
                        meal_dict[meal_day] = {}
                    
                    # 급식 종류: 1=조식, 2=중식, 3=석식
                    meal_sc_code = meal.get("MMEAL_SC_CODE", "2")
                    meal_type = {
                        "1": "breakfast",
                        "2": "lunch",
                        "3": "dinner"
                    }.get(meal_sc_code, "lunch")
                    
                    # 급식 메뉴
                    dish_name = meal.get("DDISH_NM", "")
                    # <br/> 태그를 줄바꿈으로 변환
                    dish_name = dish_name.replace("<br/>", "\n")
                    # 알레르기 정보 (숫자) 제거
                    import re
                    dish_name = re.sub(r'\d+\.', '', dish_name)
                    dish_name = re.sub(r'\(\d+\)', '', dish_name)
                    
                    # 칼로리 정보
                    cal_info = meal.get("CAL_INFO", "")
                    
                    # 영양 정보
                    ntr_info = meal.get("NTR_INFO", "")
                    
                    # 원산지 정보
                    orplc_info = meal.get("ORPLC_INFO", "")
                    orplc_info = orplc_info.replace("<br/>", "\n") if orplc_info else ""
                    
                    meal_dict[meal_day][meal_type] = {
                        "menu": dish_name.strip(),
                        "calories": cal_info,
                        "nutrition": ntr_info,
                        "origin": orplc_info.strip()
                    }
            
            return meal_dict
            
        except Exception as e:
            print(f"급식 조회 오류: {e}")
            return {}
    
    def get_today_meal(self, school_code: str, atpt_ofcdc_sc_code: str) -> Dict[str, Dict]:
        """
        오늘의 급식 정보 조회
        
        Args:
            school_code: 표준학교코드
            atpt_ofcdc_sc_code: 시도교육청코드
        
        Returns:
            오늘의 급식 정보 (조식, 중식, 석식)
        """
        today = datetime.now()
        meal_dict = self.get_meal(
            school_code, 
            atpt_ofcdc_sc_code, 
            today.year, 
            today.month, 
            today.day
        )
        
        return meal_dict.get(today.day, {})
    
    def get_week_meal(self, school_code: str, atpt_ofcdc_sc_code: str) -> Dict[str, Dict]:
        """
        이번 주 급식 정보 조회
        
        Args:
            school_code: 표준학교코드
            atpt_ofcdc_sc_code: 시도교육청코드
        
        Returns:
            이번 주 급식 정보
        """
        today = datetime.now()
        
        # 이번 주 월요일부터 금요일까지
        weekday = today.weekday()  # 0=월요일, 6=일요일
        monday = today - timedelta(days=weekday)
        
        week_meals = {}
        
        for i in range(5):  # 월~금
            day = monday + timedelta(days=i)
            day_name = ["월", "화", "수", "목", "금"][i]
            
            meal_dict = self.get_meal(
                school_code,
                atpt_ofcdc_sc_code,
                day.year,
                day.month,
                day.day
            )
            
            week_meals[day_name] = {
                "date": day.strftime("%Y-%m-%d"),
                "meals": meal_dict.get(day.day, {})
            }
        
        return week_meals


# 편의 함수들

def search_school_by_name(school_name: str, api_key: str = "") -> List[Dict]:
    """
    학교명으로 학교 검색
    
    Args:
        school_name: 학교명
        api_key: NEIS API 키 (선택)
    
    Returns:
        학교 정보 리스트
    """
    neis = NeisAPI(api_key)
    return neis.search_school(school_name)


def get_school_meal_info(school_name: str, year: int, month: int, api_key: str = "") -> Dict:
    """
    학교명으로 급식 정보 조회
    
    Args:
        school_name: 학교명
        year: 년도
        month: 월
        api_key: NEIS API 키 (선택)
    
    Returns:
        급식 정보 딕셔너리
    """
    neis = NeisAPI(api_key)
    
    # 학교 검색
    schools = neis.search_school(school_name)
    
    if not schools:
        return {"error": "학교를 찾을 수 없습니다."}
    
    # 첫 번째 학교 선택
    school = schools[0]
    school_code = school.get("SD_SCHUL_CODE", "")
    atpt_code = school.get("ATPT_OFCDC_SC_CODE", "")
    
    if not school_code or not atpt_code:
        return {"error": "학교 코드를 찾을 수 없습니다."}
    
    # 급식 정보 조회
    meals = neis.get_meal(school_code, atpt_code, year, month)
    
    return {
        "school": school,
        "meals": meals
    }


def get_today_meal_simple(school_name: str, api_key: str = "") -> Dict:
    """
    오늘의 급식 간단 조회
    
    Args:
        school_name: 학교명
        api_key: NEIS API 키 (선택)
    
    Returns:
        오늘의 급식 정보
    """
    today = datetime.now()
    result = get_school_meal_info(school_name, today.year, today.month, api_key)
    
    if "error" in result:
        return result
    
    meals = result.get("meals", {})
    today_meal = meals.get(today.day, {})
    
    return {
        "school": result["school"],
        "date": today.strftime("%Y-%m-%d"),
        "meals": today_meal
    }


# 테스트 코드
if __name__ == "__main__":
    # 학교 검색 테스트
    print("=== 학교 검색 ===")
    schools = search_school_by_name("고운고등학교")
    
    if schools:
        for school in schools:
            print(f"학교명: {school.get('SCHUL_NM', '')}")
            print(f"주소: {school.get('ORG_RDNMA', '')}")
            print(f"학교코드: {school.get('SD_SCHUL_CODE', '')}")
            print(f"교육청코드: {school.get('ATPT_OFCDC_SC_CODE', '')}")
            print("-" * 50)
    
    # 오늘의 급식 테스트
    print("\n=== 오늘의 급식 ===")
    today_meal = get_today_meal_simple("고운고등학교")
    
    if "error" not in today_meal:
        print(f"학교: {today_meal['school'].get('SCHUL_NM', '')}")
        print(f"날짜: {today_meal['date']}")
        
        meals = today_meal.get("meals", {})
        for meal_type, meal_info in meals.items():
            meal_name = {"breakfast": "조식", "lunch": "중식", "dinner": "석식"}.get(meal_type, meal_type)
            print(f"\n[{meal_name}]")
            print(meal_info.get("menu", "급식 정보 없음"))
            if meal_info.get("calories"):
                print(f"칼로리: {meal_info.get('calories')}")
    else:
        print(today_meal["error"])

