# ✅ 설치 라이브러리 및 환경 정보

## 1. 실행 환경
- OS: Windows 10  
- Python 버전: 3.11.9  
- 가상환경: venv (.venv)  
- 테스트 프레임워크: pytest  
- 자동화 도구: Playwright (Web + Mobile Web)  

## 2. 주요 설치 라이브러리 목록 (테스트 관련)
playwright==1.56.0  
pytest==8.3.5  
pytest-check==2.6.0  
pytest-html==4.1.1  
pytest-metadata==3.1.1  
pytest-order==1.3.0  
pytest-rerunfailures==15.1  
allure-pytest==2.13.2  
loguru==0.7.3  
python-dotenv==1.1.0  
requests==2.32.3  
pandas==2.3.3  
selenium==4.32.0 (UI 테스트 대비용)
webdriver-manager==4.0.2 (UI 테스트 대비용)
selenium-page-factory==2.7 (UI 테스트 대비용) 

## 3. 테스트 실행 방식
✅ Desktop Web 실행
- pytest -m desktop -s

✅ Mobile Web 실행 (iPhone 13 Pro, Pixel 5)
- pytest -m mobile -s

✅ 전체 테스트 실행
- pytest -s

✅ 특정 테스트 실행 예시
- pytest -k "nav_list" -m mobile -s

## 4. 보고서 생성 정보

HTML Report
- reports/report.html

JUnit XML
- reports/result.xml

실패 스크린샷 저장 위치
- reports/defects/

요약 CSV 저장 위치
- reports/test_summary_YYYYMMDD_HHMMSS.csv
