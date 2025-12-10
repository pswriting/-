import streamlit as st
import google.generativeai as genai
import re
import json
from datetime import datetime

# ==========================================
# API 키는 사용자가 직접 입력
# ==========================================

# --- 페이지 설정 ---
st.set_page_config(
    page_title="전자책 작성 프로그램", 
    layout="wide", 
    page_icon="◆"
)

# --- 지구인사이트 스타일 CSS ---
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    * { 
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif; 
    }
    
    /* 기본 요소 숨김 */
    header {visibility: hidden;} 
    .stDeployButton {display:none;} 
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* 메인 배경 - 순수 화이트 */
    .stApp {
        background: #ffffff;
    }
    
    /* 메인 영역 */
    .main .block-container {
        background: #ffffff;
        padding: 2rem 3rem;
        max-width: 1200px;
    }
    
    /* 사이드바 */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #eeeeee;
    }
    
    [data-testid="stSidebar"] * {
        color: #222222 !important;
    }
    
    [data-testid="stSidebar"] .stProgress > div > div > div > div {
        background: #222222;
        border-radius: 10px;
    }
    
    /* 모든 텍스트 - 진한 검정 */
    .stMarkdown, .stText, p, span, label, .stMarkdown p {
        color: #222222 !important;
        line-height: 1.7;
    }
    
    /* 제목 스타일링 */
    h1 { 
        color: #111111 !important; 
        font-weight: 700 !important; 
        font-size: 2rem !important;
        letter-spacing: -0.5px;
        margin-bottom: 1rem !important;
    }
    
    h2 { 
        color: #111111 !important; 
        font-weight: 700 !important;
        font-size: 1.4rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 { 
        color: #222222 !important; 
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* 탭 스타일 - 미니멀 라인 */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        gap: 0;
        border-bottom: 2px solid #eeeeee;
        padding: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #888888 !important;
        border-radius: 0;
        font-weight: 500;
        padding: 16px 24px;
        font-size: 15px;
        border-bottom: 2px solid transparent;
        margin-bottom: -2px;
        transition: all 0.2s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #222222 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #111111 !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #111111 !important;
    }
    
    /* 버튼 스타일 - 검정 배경 + 흰색 글씨 */
    .stButton > button { 
        width: 100%; 
        border-radius: 30px; 
        font-weight: 600; 
        background: #111111 !important;
        color: #ffffff !important;
        border: none !important;
        padding: 14px 32px;
        font-size: 15px;
        transition: all 0.2s;
        box-shadow: none;
    }
    
    .stButton > button:hover { 
        background: #333333 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* 버튼 내부 텍스트 강제 흰색 */
    .stButton > button p,
    .stButton > button span,
    .stButton > button div,
    .stButton > button * {
        color: #ffffff !important;
    }
    
    /* 다운로드 버튼 */
    .stDownloadButton > button {
        background: #2d5a27 !important;
        color: #ffffff !important;
        border-radius: 30px;
    }
    
    .stDownloadButton > button:hover {
        background: #3d7a37 !important;
    }
    
    .stDownloadButton > button p,
    .stDownloadButton > button span,
    .stDownloadButton > button * {
        color: #ffffff !important;
    }
    
    /* 입력 필드 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #ffffff !important;
        border: 1px solid #dddddd !important;
        border-radius: 8px !important;
        color: #222222 !important;
        padding: 14px 16px !important;
        font-size: 15px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #111111 !important;
        box-shadow: none !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #aaaaaa !important;
    }
    
    /* 셀렉트박스 */
    .stSelectbox > div > div {
        background: #ffffff !important;
        border: 1px solid #dddddd !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox > div > div > div {
        color: #222222 !important;
    }
    
    /* 메트릭 */
    [data-testid="stMetricValue"] {
        color: #111111 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #666666 !important;
    }
    
    /* 알림 메시지 */
    .stSuccess {
        background: #f0f9f0 !important;
        border: 1px solid #c8e6c9 !important;
        border-radius: 8px !important;
    }
    .stSuccess p { color: #2e7d32 !important; }
    
    .stWarning {
        background: #fff8e1 !important;
        border: 1px solid #ffecb3 !important;
        border-radius: 8px !important;
    }
    .stWarning p { color: #f57c00 !important; }
    
    .stError {
        background: #ffebee !important;
        border: 1px solid #ffcdd2 !important;
        border-radius: 8px !important;
    }
    .stError p { color: #c62828 !important; }
    
    .stInfo {
        background: #e3f2fd !important;
        border: 1px solid #bbdefb !important;
        border-radius: 8px !important;
    }
    .stInfo p { color: #1565c0 !important; }
    
    /* 구분선 */
    hr {
        border: none !important;
        border-top: 1px solid #eeeeee !important;
        margin: 2rem 0 !important;
    }
    
    /* 프로그레스 바 */
    .stProgress > div > div > div > div {
        background: #222222;
        border-radius: 10px;
    }
    
    /* ===== 커스텀 컴포넌트 ===== */
    
    /* 로그인 화면 */
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: #ffffff;
        border: 1px solid #eeeeee;
        border-radius: 20px;
        text-align: center;
    }
    
    .login-title {
        font-size: 28px;
        font-weight: 700;
        color: #111111;
        margin-bottom: 8px;
    }
    
    .login-subtitle {
        font-size: 15px;
        color: #888888;
        margin-bottom: 30px;
    }
    
    /* 히어로 섹션 */
    .hero-section {
        text-align: center;
        padding: 60px 20px;
        margin-bottom: 40px;
    }
    
    .hero-label {
        font-size: 13px;
        font-weight: 600;
        color: #666666;
        letter-spacing: 3px;
        margin-bottom: 16px;
        text-transform: uppercase;
    }
    
    .hero-title {
        font-size: 42px;
        font-weight: 800;
        color: #111111;
        margin-bottom: 16px;
        letter-spacing: -1px;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 18px;
        color: #666666;
        font-weight: 400;
    }
    
    /* 섹션 라벨 */
    .section-label {
        font-size: 12px;
        font-weight: 600;
        color: #888888;
        letter-spacing: 2px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    
    /* 점수 카드 */
    .score-card {
        background: #f8f8f8;
        border-radius: 20px;
        padding: 50px 40px;
        text-align: center;
    }
    
    .score-number {
        font-size: 80px;
        font-weight: 800;
        color: #111111;
        line-height: 1;
        margin-bottom: 8px;
    }
    
    .score-label {
        color: #888888;
        font-size: 14px;
        font-weight: 500;
    }
    
    /* 상태 배지 */
    .status-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 13px;
        margin-top: 20px;
    }
    
    .status-excellent {
        background: #111111;
        color: #ffffff;
    }
    
    .status-good {
        background: #f0f0f0;
        color: #333333;
    }
    
    .status-warning {
        background: #fff3e0;
        color: #e65100;
    }
    
    /* 정보 카드 */
    .info-card {
        background: #f8f8f8;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
    }
    
    .info-card-title {
        font-size: 12px;
        font-weight: 700;
        color: #888888;
        letter-spacing: 1px;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    
    .info-card p {
        color: #333333 !important;
        font-size: 15px;
        line-height: 1.8;
        margin: 8px 0;
    }
    
    /* 제목 카드 */
    .title-card {
        background: #ffffff;
        border: 1px solid #eeeeee;
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        transition: all 0.2s;
    }
    
    .title-card:hover {
        border-color: #cccccc;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    
    .title-card .card-number {
        font-size: 12px;
        font-weight: 600;
        color: #aaaaaa;
        margin-bottom: 8px;
    }
    
    .title-card .main-title {
        color: #111111;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    
    .title-card .sub-title {
        color: #666666;
        font-size: 14px;
        margin-bottom: 16px;
    }
    
    .title-card .reason {
        color: #444444;
        font-size: 14px;
        padding: 14px 16px;
        background: #f8f8f8;
        border-radius: 10px;
        line-height: 1.6;
    }
    
    /* 점수 아이템 */
    .score-item {
        background: #ffffff;
        border: 1px solid #eeeeee;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 10px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .score-item-label {
        color: #333333;
        font-weight: 500;
        font-size: 15px;
    }
    
    .score-item-value {
        color: #111111;
        font-weight: 700;
        font-size: 20px;
    }
    
    .score-item-reason {
        color: #666666;
        font-size: 14px;
        margin-top: 4px;
        line-height: 1.5;
    }
    
    /* 요약 박스 */
    .summary-box {
        background: #f8f8f8;
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
    }
    
    .summary-box p {
        color: #333333 !important;
        font-size: 15px;
        line-height: 1.7;
    }
    
    /* 푸터 */
    .premium-footer {
        text-align: center;
        padding: 40px 20px;
        margin-top: 60px;
        border-top: 1px solid #eeeeee;
    }
    
    .premium-footer-text {
        color: #888888;
        font-size: 14px;
    }
    
    .premium-footer-author {
        color: #222222;
        font-weight: 600;
    }
    
    /* 빈 상태 */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        background: #f8f8f8;
        border-radius: 16px;
    }
    
    .empty-state p {
        color: #888888 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 비밀번호 설정 (여기서 변경 가능)
# ==========================================
CORRECT_PASSWORD = "cashmaker2024"
# ==========================================

# --- 비밀번호 확인 ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("""
    <div class="login-container">
        <div class="login-title">CASHMAKER</div>
        <div class="login-subtitle">전자책 작성 프로그램</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        password_input = st.text_input("비밀번호를 입력하세요", type="password", placeholder="비밀번호")
        
        if st.button("입장하기"):
            if password_input == CORRECT_PASSWORD:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다")
    
    st.stop()

# --- 세션 초기화 ---
default_states = {
    'topic': '',
    'target_persona': '',
    'pain_points': '',
    'one_line_concept': '',
    'outline': [],
    'chapters': {},
    'current_step': 1,
    'market_analysis': '',
    'book_title': '',
    'subtitle': '',
    'topic_score': None,
    'topic_verdict': None,
    'score_details': None,
    'generated_titles': None,
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- Gemini 모델은 사이드바에서 설정됨 ---

# --- 사이드바 ---
with st.sidebar:
    st.markdown("### Progress")
    
    progress_items = [
        bool(st.session_state['topic']),
        bool(st.session_state['target_persona']),
        bool(st.session_state['outline']),
        len(st.session_state['chapters']) > 0,
        any(ch.get('content') for ch in st.session_state['chapters'].values()) if st.session_state['chapters'] else False
    ]
    progress = sum(progress_items) / len(progress_items) * 100
    
    st.progress(progress / 100)
    st.caption(f"{progress:.0f}% 완료")
    
    st.markdown("---")
    st.markdown("### Info")
    if st.session_state['topic']:
        st.caption(f"주제: {st.session_state['topic']}")
    if st.session_state['book_title']:
        st.caption(f"제목: {st.session_state['book_title']}")
    if st.session_state['outline']:
        st.caption(f"목차: {len(st.session_state['outline'])}개")
    
    completed_chapters = sum(1 for ch in st.session_state['chapters'].values() if ch.get('content'))
    if completed_chapters:
        st.caption(f"완성: {completed_chapters}개")
    
    st.markdown("---")
    st.markdown("### API 설정")
    
    # API 키 입력
    api_key_input = st.text_input(
        "Gemini API 키",
        type="password",
        placeholder="AIza...",
        help="Google AI Studio에서 발급받은 API 키를 입력하세요"
    )
    
    # API 키 발급 안내
    with st.expander("API 키 발급 방법 (무료)"):
        st.markdown("""
        **2분이면 끝!**
        
        1. [Google AI Studio](https://aistudio.google.com/apikey) 접속
        2. Google 계정으로 로그인
        3. **"API 키 만들기"** 클릭
        4. 생성된 키 복사
        5. 위 입력창에 붙여넣기
        
        ✅ 완전 무료  
        ✅ 신용카드 불필요  
        ✅ 분당 15회 요청 가능
        """)
    
    # API 연결 상태 (간소화)
    if not api_key_input:
        st.caption("⚠️ API 키를 입력하세요")

# --- AI 함수 ---
def ask_ai(system_role, prompt, temperature=0.7):
    if not api_key_input:
        return "⚠️ API 키를 먼저 입력해주세요."
    
    try:
        genai.configure(api_key=api_key_input)
        ai_model = genai.GenerativeModel('models/gemini-2.0-flash')
        generation_config = genai.types.GenerationConfig(temperature=temperature)
        full_prompt = f"""당신은 {system_role}입니다.

{prompt}

한국어로 답변해주세요."""
        response = ai_model.generate_content(full_prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        return f"오류 발생: {str(e)}"

def analyze_topic_score(topic):
    prompt = f"""'{topic}' 주제의 전자책 적합도를 분석해주세요.

다음 5가지 항목을 각각 0~100점으로 채점하고, 종합 점수와 판정을 내려주세요.

채점 항목:
1. 시장성 (수요가 있는가?)
2. 수익성 (돈을 지불할 의향이 있는 주제인가?)
3. 차별화 가능성 (경쟁에서 이길 수 있는가?)
4. 작성 난이도 (전자책으로 만들기 쉬운가?)
5. 지속성 (오래 팔릴 수 있는가?)

반드시 아래 JSON 형식으로만 답변하세요. 다른 텍스트 없이 JSON만:
{{
    "market": {{"score": 85, "reason": "이유"}},
    "profit": {{"score": 80, "reason": "이유"}},
    "differentiation": {{"score": 75, "reason": "이유"}},
    "difficulty": {{"score": 90, "reason": "이유"}},
    "sustainability": {{"score": 70, "reason": "이유"}},
    "total_score": 80,
    "verdict": "적합" 또는 "보통" 또는 "부적합",
    "summary": "종합 의견 2~3문장"
}}"""
    return ask_ai("전자책 시장 분석가", prompt, temperature=0.3)

def generate_titles_advanced(topic, persona, pain_points):
    prompt = f"""당신은 자청(역행자), 엠제이 드마코(부의 추월차선), 김승호(돈의 속성)급 베스트셀러 작가입니다.
당신이 쓴 책들은 수십만 부가 팔렸고, 제목만으로 서점에서 손이 가게 만드는 마법을 부립니다.

[분석 대상]
주제: {topic}
타겟: {persona}  
타겟의 속마음: {pain_points}

[베스트셀러 제목의 핵심 원칙]

1. "읽는 순간 뒤통수를 맞은 느낌" - 기존 상식을 정면으로 뒤집어라
   - "역행자" → 남들과 반대로 가야 성공한다는 역설
   - "부의 추월차선" → 느린 차선(직장)에서 빠른 차선으로 갈아타라
   
2. "이건 나만 몰랐던 거 아냐?" - 소외감과 긴급함을 동시에 자극
   - 읽지 않으면 뒤처질 것 같은 불안감
   - 남들은 이미 알고 있다는 느낌
   
3. "구체적 숫자는 신뢰를 만든다" - 모호함 제거
   - "나는 4시간만 일한다" - 구체적이라 믿음이 감
   - "31개월 만에 10억" - 실제 숫자가 주는 힘
   
4. "짧을수록 강하다" - 7자 이내 메인 타이틀
   - "역행자" (3자), "돈의 속성" (4자), "부의 추월차선" (5자)

[실제 베스트셀러 제목 레퍼런스]
- "역행자" - 한 단어로 정체성 규정 (자청)
- "부의 추월차선" - 메타포로 욕망 자극
- "돈, 뜨겁게 사랑하고 차갑게 다루어라" - 대비와 긴장감
- "나는 4시간만 일한다" - 상식 파괴 + 구체적 숫자
- "언스크립티드" - 낯선 단어로 호기심 유발
- "망할 용기" - 역설적 표현으로 충격

[절대 금지 - 이런 제목은 절대 쓰지 마세요]
- "비법", "노하우", "성공", "시작하세요", "방법", "전략", "가이드"
- "~하는 법", "~하기", "완벽한", "쉬운", "단계별"
- 물음표로 끝나는 평범한 질문형
- "데이터 기반", "체계적", "효율적" 같은 교과서 표현
- "입문", "기초", "초보자를 위한"

[미션]
위 원칙으로 {topic} 주제의 전자책 제목 5개를 만들어주세요.
평범하면 실패입니다. 서점에서 이 제목을 본 사람이 "뭐지?" 하고 멈춰서서 집어들게 만드세요.
자청의 "역행자"처럼 단 한 단어로 사람의 정체성을 흔들 수 있다면 최고입니다.

형식 (JSON만 출력):
{{
    "titles": [
        {{
            "title": "7자 이내 임팩트 제목",
            "subtitle": "15자 이내 보조 설명",
            "concept": "이 제목의 핵심 컨셉",
            "why_works": "왜 사람들이 이 제목에 끌리는지 심리학적 이유"
        }}
    ]
}}"""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.9)

def generate_concept(topic, persona, pain_points):
    prompt = f"""주제: {topic}
타겟: {persona}
타겟의 고민: {pain_points}

위 주제에 대해 "이 책 안 읽으면 손해"라는 느낌을 주는 한 줄 컨셉 5개를 만들어주세요.

좋은 컨셉의 조건:
- 상식을 정면으로 부정 ("~한다고? 틀렸다")
- 호기심 자극 ("진짜 이유는 따로 있다")
- 구체적 숫자 포함 ("3개월 만에", "상위 1%")

출력 형식 (이 형식만 출력하세요):

1. [한 줄 컨셉]
   → 왜 끌리는가

2. [한 줄 컨셉]
   → 왜 끌리는가

3. [한 줄 컨셉]
   → 왜 끌리는가

4. [한 줄 컨셉]
   → 왜 끌리는가

5. [한 줄 컨셉]
   → 왜 끌리는가"""
    return ask_ai("카피라이터", prompt, temperature=0.9)

def generate_outline(topic, persona, pain_points):
    prompt = f"""주제: {topic}
타겟: {persona}
타겟의 고민: {pain_points}

위 주제로 6~7개 챕터 목차를 설계해주세요.

[챕터 제목 규칙]
- 질문형: "왜 ~할까?"
- 도발형: "~는 거짓말이다"
- 비밀형: "아무도 말 안 하는 ~"
- 숫자형: "3개월 만에 일어난 일"

[소제목 규칙 - 중요!]
소제목도 챕터 제목처럼 매력적이어야 합니다.
- BAD: "기본 개념", "실전 적용", "정리"
- GOOD: "그날 통장 잔고 47만원", "첫 수익이 찍힌 날", "모두가 틀렸다고 했다"

소제목은 구체적 장면, 숫자, 스토리가 느껴져야 읽고 싶어집니다.

[감정선 흐름]
챕터1: 공감 (나도 그랬어)
챕터2: 문제 제기 (근데 이게 문제야)
챕터3: 반전 (사실은 이거였어)
챕터4: 깨달음 (이걸 알면 달라져)
챕터5: 실전 (이렇게 해)
챕터6: 마인드셋 (이게 제일 중요해)
챕터7: 비전 (이렇게 되면 인생 바뀜)

출력 형식 (이 형식만 출력):

## 챕터1: [호기심 유발 제목]
- [매력적인 소제목1]
- [매력적인 소제목2]
- [매력적인 소제목3]

## 챕터2: [도발적 제목]
- [매력적인 소제목1]
- [매력적인 소제목2]
- [매력적인 소제목3]

(6~7개 챕터까지)"""
    return ask_ai("출판기획자", prompt, temperature=0.85)

def generate_subtopics(chapter_title, topic, persona):
    prompt = f"""주제: {topic}
챕터: {chapter_title}
타겟: {persona}

이 챕터의 소제목 3개를 만들어주세요.

[소제목 규칙]
소제목만 봐도 "이건 뭐지?" 하고 읽고 싶어야 합니다.

나쁜 예시 (절대 금지):
- "기본 개념 이해하기"
- "실전 적용 방법"
- "핵심 정리"
- "~의 중요성"
- "~란 무엇인가"

좋은 예시:
- "그날 통장 잔고 47만원"
- "새벽 4시, 첫 수익 알림이 울렸다"
- "모두가 틀렸다고 했다"
- "3개월 후 월급을 넘어섰다"
- "아무도 알려주지 않는 진짜 비밀"
- "나는 왜 매번 실패했을까"
- "그 한마디가 모든 걸 바꿨다"

[규칙]
1. 구체적 숫자 포함 (날짜, 금액, 기간)
2. 스토리/장면이 느껴지게
3. 호기심 자극 (뒷이야기가 궁금하게)
4. 감정을 건드리게

출력 형식 (이것만 출력):
1. [소제목]
2. [소제목]
3. [소제목]"""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.9)

def generate_interview_questions(subtopic_title, chapter_title, topic):
    prompt = f"""당신은 베스트셀러 작가의 고스트라이터입니다.
'{topic}' 전자책의 '{chapter_title}' 챕터 중 '{subtopic_title}' 소제목 부분을 쓰기 위해 작가를 인터뷰합니다.

[인터뷰 목적]
'{subtopic_title}'에 대한 작가의 진짜 경험과 통찰을 끌어내서, 독자가 "와, 이건 진짜 경험한 사람만 알 수 있는 거다"라고 느끼게 만들 콘텐츠를 확보하는 것.

[좋은 질문의 특징]
1. 구체적 상황을 묻는다: "언제, 어디서, 어떻게"
2. 감정을 묻는다: "그때 기분이 어땠나요?"
3. 실패를 묻는다: "처음에 뭘 잘못했나요?"
4. 반전을 묻는다: "뭘 깨닫고 달라졌나요?"
5. 디테일을 묻는다: "구체적으로 어떻게 했나요?"

[나쁜 질문 예시 - 이런 질문은 피하세요]
- "이것의 중요성에 대해 말씀해주세요" (추상적)
- "팁이 있다면?" (뻔한 답변 유도)
- "어떻게 생각하세요?" (의견만 나옴)

[좋은 질문 예시]
- "처음 이걸 시작했을 때 가장 크게 실패한 경험은 뭔가요? 그때 뭘 잘못 생각했던 건가요?"
- "이걸 깨닫기 전과 후, 구체적으로 뭐가 달라졌나요? 숫자로 말해주실 수 있나요?"
- "주변에서 반대했을 때 어떻게 대응했나요? 실제로 뭐라고 말했나요?"
- "이 방법을 처음 시도한 날, 그 상황을 자세히 묘사해주실 수 있나요?"
- "독자들이 가장 많이 하는 실수는 뭔가요? 왜 그 실수를 하게 되나요?"

[미션]
'{subtopic_title}' 소제목의 핵심 내용을 끌어낼 수 있는 인터뷰 질문 3개를 만들어주세요.
이 질문에 답하면 자연스럽게 이 소제목에 대한 몰입감 있는 내용이 완성될 수 있어야 합니다.

형식:
Q1: [구체적이고 깊이 있는 질문]
Q2: [구체적이고 깊이 있는 질문]
Q3: [구체적이고 깊이 있는 질문]"""
    return ask_ai("베스트셀러 고스트라이터", prompt, temperature=0.7)

def generate_subtopic_content(subtopic_title, chapter_title, questions, answers, topic, persona):
    qa_pairs = ""
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        if a.strip():
            qa_pairs += f"\n질문{i}: {q}\n답변{i}: {a}\n"
    
    prompt = f"""당신은 자청(역행자), 엠제이 드마코(부의 추월차선), 김승호(돈의 속성)의 문체를 완벽히 체화한 고스트라이터입니다.
당신이 쓴 글은 독자가 "이건 내 얘기잖아"라고 느끼며 단숨에 읽게 만듭니다.

[집필 정보]
전자책 주제: {topic}
챕터 제목: {chapter_title}
소제목: {subtopic_title}
타겟 독자: {persona}

[작가 인터뷰 내용 - 이것을 바탕으로 글을 작성하세요]
{qa_pairs}

[베스트셀러 글쓰기 원칙 - 자청/드마코 스타일]

1. 문장 호흡 (리듬)
   짧게. 끊어서. 리듬감 있게.
   - 한 문장 최대 20자
   - 3문장 짧게 → 1문장 약간 길게 → 다시 짧게

2. 스토리텔링 (Show, Don't Tell)
   추상적 조언은 죽은 글이다. 구체적 장면으로 보여줘라.
   - BAD: "열심히 노력했다" 
   - GOOD: "새벽 4시에 일어나 2시간 동안 글을 썼다."

3. 자청 스타일 문체 특징
   - "솔직히 말할게" - 친밀감
   - "이건 아무도 안 알려줘" - 비밀 공유
   - "나도 처음엔 몰랐어" - 동질감

[절대 금지 - AI 티 나는 표현]
- "~입니다", "~하겠습니다" 반복
- "중요합니다", "필요합니다"
- "첫째, 둘째, 셋째" 나열식
- "따라서", "그러므로"

[미션]
위 인터뷰 내용을 바탕으로 '{subtopic_title}' 소제목에 대한 본문을 1000~1500자 분량으로 작성하세요.

조건:
1. 소제목 내용에 집중해서 깊이 있게 작성
2. 읽는 사람이 몰입할 수 있게
3. 구체적 장면과 숫자로
4. AI가 쓴 티가 나면 실패

글의 톤: 선배가 후배에게 진심으로 조언해주는 느낌."""
    return ask_ai("베스트셀러 고스트라이터", prompt, temperature=0.8)


def refine_content(content, style="친근한"):
    style_guide = {
        "친근한": """자청(역행자) 스타일
- 친구에게 말하듯 편안하고 솔직한 톤
- "솔직히 말할게", "이건 진짜야", "나도 그랬어"
- 약간의 반말 섞인 존댓말
- 독자를 '너' 또는 '당신'으로 호칭""",
        
        "전문적": """김승호(돈의 속성) 스타일
- 신뢰감 있고 권위있는 전문가 톤
- 구체적 숫자와 데이터로 신뢰 구축
- 차분하지만 확신에 찬 어조
- 경험에서 우러나온 통찰""",
        
        "직설적": """엠제이 드마코(부의 추월차선) 스타일
- 핵심만 간결하게, 군더더기 제로
- 도발적이고 직설적인 표현
- "~하지 마라", "~은 거짓말이다"
- 독자의 안일함을 깨우는 톤""",
        
        "스토리텔링": """스토리 중심 스타일
- 모든 조언을 구체적 장면으로 전달
- 시간, 장소, 감정을 생생하게 묘사
- "그날 나는...", "그때 깨달았다..."
- 독자가 영화를 보듯 읽게 만듦"""
    }
    
    prompt = f"""당신은 베스트셀러 전자책 전문 에디터입니다.
다음 글의 문체를 다듬어서 더 몰입감 있고 읽기 좋게 만들어주세요.

[원본 글]
{content}

[목표 스타일]
{style_guide.get(style, style_guide["친근한"])}

[문체 다듬기 체크리스트]

1. AI 티 제거
   - "~입니다", "~하겠습니다" 반복 → 다양한 종결어미로 변경
   - "중요합니다", "필요합니다" → 더 강렬한 표현으로
   - "첫째, 둘째, 셋째" → 자연스러운 연결로
   - "따라서", "그러므로" → 제거하거나 구어체로

2. 문장 리듬 개선
   - 긴 문장(30자 이상) → 2~3개로 분리
   - 비슷한 길이 문장 연속 → 길이 변화 주기
   - 수동태 → 능동태로

3. 구체성 강화
   - 추상적 표현 → 구체적 숫자/상황으로
   - "많이", "다양하게" → 구체적 수치로
   - "잘 됐다" → 어떻게 잘 됐는지 구체적으로

4. 몰입감 강화
   - 평범한 시작 → 훅(Hook)으로 변경
   - 설명 위주 → 장면 묘사로
   - 일반론 → 개인 경험담으로

[미션]
위 원본 글을 {style} 스타일로 다듬어주세요.
내용은 유지하되, 읽는 사람이 손에서 책을 놓을 수 없게 만들어주세요.
반드시 전체 글을 다듬어서 출력해주세요."""
    return ask_ai("베스트셀러 에디터", prompt, temperature=0.75)

def check_quality(content):
    prompt = f"""당신은 "역행자", "부의 추월차선", "돈의 속성" 수준의 베스트셀러를 편집한 전문 편집자입니다.
다음 글이 베스트셀러 수준인지 냉정하게 평가해주세요.

[평가할 글]
{content[:4000]}

[평가 기준 - 베스트셀러 체크리스트]

1. 첫 문장 (10점)
   - 첫 문장이 독자의 뒤통수를 치는가?
   - 첫 문장만 읽고도 다음이 궁금한가?

2. 몰입도 (10점)
   - 중간에 멈추지 않고 끝까지 읽게 되는가?
   - 문장 리듬이 좋은가?

3. 공감력 (10점)
   - 독자가 "이건 내 얘기잖아"라고 느끼는가?
   - 타겟의 아픔을 정확히 건드리는가?

4. 구체성 (10점)
   - 추상적 조언 대신 구체적 장면/숫자가 있는가?
   - "열심히 했다" 대신 "새벽 4시에 일어났다" 수준인가?

5. AI 티 (10점, 감점 항목)
   - "~입니다" 반복, "따라서", "중요합니다" 등 AI 표현이 있는가?
   - 문장이 너무 균일하고 딱딱한가?

[출력 형식]

📊 종합 점수: __/50점

📌 첫 문장 평가: __/10점
- 현재 첫 문장: "[첫 문장 인용]"
- 평가: [좋은 점 또는 문제점]
- 개선안: "[더 좋은 첫 문장 제안]"

📌 몰입도 평가: __/10점
- [구체적 평가]

📌 공감력 평가: __/10점
- [구체적 평가]

📌 구체성 평가: __/10점
- [구체적 평가]

📌 AI 티 체크: __/10점
- 발견된 AI 표현: [있다면 나열]
- 개선이 필요한 문장: [3개까지]

✍️ 수정하면 좋을 문장 TOP 3
1. 원문: "..." → 수정안: "..."
2. 원문: "..." → 수정안: "..."
3. 원문: "..." → 수정안: "..."

💡 잘 쓴 문장 TOP 2
1. "[잘 쓴 문장]" - 좋은 이유
2. "[잘 쓴 문장]" - 좋은 이유

🎯 총평
[베스트셀러가 되기 위해 가장 중요한 개선점 1~2가지]"""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.6)

def generate_marketing_copy(title, subtitle, topic, persona):
    prompt = f"""당신은 크몽에서 전자책을 수천 권 판매한 탑셀러입니다.
당신의 상세페이지는 방문자의 15%가 구매하는 전설적인 전환율을 기록합니다.
당신의 카피는 읽는 순간 "이거 안 사면 손해"라는 느낌을 줍니다.

[상품 정보]
제목: {title}
부제: {subtitle}
주제: {topic}
타겟: {persona}

[미션]
이 전자책을 폭발적으로 팔기 위한 킬러 카피를 만들어주세요.

---

1. 크몽 상품 제목 (40자 이내)
   - 검색 키워드 포함 (SEO)
   - 구체적 결과/숫자 제시
   - 예시: "[PDF] 월 300벌게 해준 크몽 전자책 공식 | 실제 매출 인증"
   - 예시: "31개월 만에 10억 번 비밀 | 직장인 부업 전자책"

2. 상세페이지 헤드라인 3개
   - 스크롤을 멈추게 만드는 한 줄
   - 상식을 파괴하거나 충격을 줘야 함
   - 금지: "~하는 법", "~방법", "~가이드"
   - 예시: "월급만 믿다가는 평생 가난하다"
   - 예시: "나는 퇴사 3개월 만에 월급보다 더 벌었다"

3. 구매 유도 문구 (CTA) 3개
   - 긴급성 + FOMO(놓치면 후회) 자극
   - 구체적 숫자 활용
   - 예시: "이 가격은 100부 한정입니다"
   - 예시: "어제도 47명이 구매했습니다"
   - 예시: "지금 안 사면, 다음 달에는 2배입니다"

4. 인스타그램 홍보 문구
   - 첫 줄에서 스크롤 멈추게 (훅 필수)
   - 스토리텔링 요소 포함
   - 해시태그 5개 (검색량 높은 것)
   - 형식:
     [훅 - 첫 줄]
     
     [스토리 - 2~3줄]
     
     [CTA]
     
     #해시태그1 #해시태그2 ...

5. 블로그 포스팅 제목 3개
   - 검색 유입 + 클릭 유도
   - 궁금증 유발형
   - 예시: "크몽 전자책으로 월 500버는 사람들의 공통점 (실화)"
   - 예시: "직장인 부업 3개월 해본 후기 (feat. 월 수익 공개)"

---

모든 카피의 핵심 원칙:
- "이거 안 보면 나만 손해" 느낌
- 구체적 숫자로 신뢰감
- 호기심 자극 → 클릭 유도 → 구매 전환"""
    return ask_ai("크몽 탑셀러 마케터", prompt, temperature=0.85)

# --- 메인 UI ---
st.markdown("""
<div class="hero-section">
    <div class="hero-label">CASHMAKER</div>
    <div class="hero-title">전자책 작성 프로그램</div>
    <div class="hero-subtitle">쉽고, 빠른 전자책 수익화</div>
</div>
""", unsafe_allow_html=True)

# 메인 탭
tabs = st.tabs([
    "주제 선정", 
    "타겟 & 컨셉", 
    "목차 설계", 
    "본문 작성", 
    "문체 다듬기",
    "최종 출력"
])

# === TAB 1: 주제 선정 ===
with tabs[0]:
    st.markdown("## 주제 선정 & 적합도 분석")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 주제 입력")
        
        topic_input = st.text_input(
            "어떤 주제로 전자책을 쓰고 싶으세요?",
            value=st.session_state['topic'],
            placeholder="예: 크몽으로 월 500만원 벌기"
        )
        
        if topic_input != st.session_state['topic']:
            st.session_state['topic'] = topic_input
            st.session_state['topic_score'] = None
            st.session_state['score_details'] = None
        
        st.markdown("""
        <div class="info-card">
            <div class="info-card-title">좋은 주제의 조건</div>
            <p>• 내가 직접 경험하고 성과를 낸 것</p>
            <p>• 사람들이 돈 주고 배우고 싶어하는 것</p>
            <p>• 구체적인 결과를 약속할 수 있는 것</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("적합도 분석하기", key="analyze_btn"):
            if not topic_input:
                st.error("주제를 입력해주세요.")
            else:
                with st.spinner("분석 중..."):
                    result = analyze_topic_score(topic_input)
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            score_data = json.loads(json_match.group())
                            st.session_state['topic_score'] = score_data.get('total_score', 0)
                            st.session_state['topic_verdict'] = score_data.get('verdict', '분석 실패')
                            st.session_state['score_details'] = score_data
                    except:
                        st.error("분석 결과 파싱 오류. 다시 시도해주세요.")
    
    with col2:
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 분석 결과")
        
        if st.session_state['topic_score'] is not None:
            score = st.session_state['topic_score']
            verdict = st.session_state['topic_verdict']
            details = st.session_state['score_details']
            
            verdict_class = "status-excellent" if verdict == "적합" else ("status-good" if verdict == "보통" else "status-warning")
            
            st.markdown(f"""
            <div class="score-card">
                <div class="score-number">{score}</div>
                <div class="score-label">종합 점수</div>
                <span class="status-badge {verdict_class}">{verdict}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if details:
                st.markdown("#### 세부 점수")
                
                items = [
                    ("시장성", details.get('market', {}).get('score', 0), details.get('market', {}).get('reason', '')),
                    ("수익성", details.get('profit', {}).get('score', 0), details.get('profit', {}).get('reason', '')),
                    ("차별화", details.get('differentiation', {}).get('score', 0), details.get('differentiation', {}).get('reason', '')),
                    ("작성 난이도", details.get('difficulty', {}).get('score', 0), details.get('difficulty', {}).get('reason', '')),
                    ("지속성", details.get('sustainability', {}).get('score', 0), details.get('sustainability', {}).get('reason', '')),
                ]
                
                for name, score_val, reason in items:
                    st.markdown(f"""
                    <div class="score-item">
                        <span class="score-item-label">{name}</span>
                        <span class="score-item-value">{score_val}</span>
                    </div>
                    <p class="score-item-reason">{reason}</p>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="summary-box">
                    <p><strong>종합 의견</strong><br>{details.get('summary', '')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <p>주제를 입력하고 분석 버튼을 클릭하세요</p>
            </div>
            """, unsafe_allow_html=True)

# === TAB 2: 타겟 & 컨셉 ===
with tabs[1]:
    st.markdown("## 타겟 설정 & 제목 생성")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 타겟 정의")
        
        persona = st.text_area(
            "누가 이 책을 읽나요?",
            value=st.session_state['target_persona'],
            placeholder="예: 30대 직장인, 퇴근 후 부업으로 월 100만원 추가 수입을 원하는 사람",
            height=100
        )
        st.session_state['target_persona'] = persona
        
        pain_points = st.text_area(
            "타겟의 가장 큰 고민은?",
            value=st.session_state['pain_points'],
            placeholder="예: 시간이 없다, 뭘 해야 할지 모르겠다, 시작이 두렵다",
            height=100
        )
        st.session_state['pain_points'] = pain_points
        
        st.markdown("---")
        
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 한 줄 컨셉")
        
        if st.button("컨셉 생성하기", key="concept_btn"):
            if not st.session_state['topic'] or not persona:
                st.error("주제와 타겟을 먼저 입력해주세요.")
            else:
                with st.spinner("생성 중..."):
                    concept = generate_concept(
                        st.session_state['topic'],
                        persona,
                        pain_points
                    )
                    st.session_state['one_line_concept'] = concept
        
        if st.session_state['one_line_concept']:
            st.markdown(f"""
            <div class="info-card">
                {st.session_state['one_line_concept'].replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p class="section-label">Step 03</p>', unsafe_allow_html=True)
        st.markdown("### 제목 생성")
        
        if st.button("제목 생성하기", key="title_btn"):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요.")
            else:
                with st.spinner("생성 중..."):
                    titles_result = generate_titles_advanced(
                        st.session_state['topic'],
                        st.session_state['target_persona'],
                        st.session_state['pain_points']
                    )
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', titles_result)
                        if json_match:
                            st.session_state['generated_titles'] = json.loads(json_match.group())
                    except:
                        st.session_state['generated_titles'] = None
                        st.markdown(titles_result)
        
        if st.session_state.get('generated_titles'):
            titles_data = st.session_state['generated_titles']
            if 'titles' in titles_data:
                for i, t in enumerate(titles_data['titles'], 1):
                    st.markdown(f"""
                    <div class="title-card">
                        <div class="card-number">TITLE 0{i}</div>
                        <div class="main-title">{t.get('title', '')}</div>
                        <div class="sub-title">{t.get('subtitle', '')}</div>
                        <div class="reason">{t.get('why_works', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<p class="section-label">Step 04</p>', unsafe_allow_html=True)
        st.markdown("### 최종 선택")
        st.session_state['book_title'] = st.text_input("제목", value=st.session_state['book_title'], placeholder="최종 제목")
        st.session_state['subtitle'] = st.text_input("부제", value=st.session_state['subtitle'], placeholder="부제")

# === TAB 3: 목차 설계 ===
with tabs[2]:
    st.markdown("## 목차 설계")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### AI 목차 생성")
        
        if st.button("목차 생성하기", key="outline_btn"):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요.")
            else:
                with st.spinner("설계 중..."):
                    outline_text = generate_outline(
                        st.session_state['topic'],
                        st.session_state['target_persona'],
                        st.session_state['pain_points']
                    )
                    chapters = re.findall(r'## (챕터\d+:?\s*.+)', outline_text)
                    if not chapters:
                        chapters = re.findall(r'(?:^|\n)(\d+\..+)', outline_text)
                    if not chapters:
                        chapters = [line.strip() for line in outline_text.split('\n') if line.strip() and len(line.strip()) > 5][:7]
                    
                    st.session_state['outline'] = chapters
                    st.session_state['full_outline'] = outline_text
        
        if 'full_outline' in st.session_state and st.session_state['full_outline']:
            st.text_area("전체 목차", value=st.session_state['full_outline'], height=400, key="full_outline_display")
    
    with col2:
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 목차 편집")
        
        if st.session_state['outline']:
            edited_outline = []
            for i, chapter in enumerate(st.session_state['outline']):
                edited = st.text_input(f"챕터 {i+1}", value=chapter, key=f"chapter_{i}")
                edited_outline.append(edited)
            
            if st.button("저장하기", key="save_outline"):
                st.session_state['outline'] = [ch for ch in edited_outline if ch.strip()]
                
                # 전체 목차에서 챕터별 소제목 파싱
                full_outline = st.session_state.get('full_outline', '')
                for ch in st.session_state['outline']:
                    if ch not in st.session_state['chapters']:
                        # 소제목 추출
                        subtopics = []
                        ch_pattern = re.escape(ch.split(':')[-1].strip() if ':' in ch else ch)
                        # 해당 챕터 다음의 - 로 시작하는 줄들을 소제목으로 추출
                        lines = full_outline.split('\n')
                        found_chapter = False
                        for line in lines:
                            if ch_pattern[:10] in line or (ch.split(':')[0] if ':' in ch else '') in line:
                                found_chapter = True
                                continue
                            if found_chapter:
                                if line.strip().startswith('##') or line.strip().startswith('챕터'):
                                    break
                                if line.strip().startswith('-'):
                                    subtopic = line.strip().lstrip('-').strip()
                                    if subtopic:
                                        subtopics.append(subtopic)
                        
                        if not subtopics:
                            subtopics = ['소제목 1', '소제목 2', '소제목 3']
                        
                        st.session_state['chapters'][ch] = {
                            'subtopics': subtopics,
                            'subtopic_data': {st: {'questions': [], 'answers': [], 'content': ''} for st in subtopics}
                        }
                st.success("저장됨")
        else:
            st.info("먼저 목차를 생성하세요.")

# === TAB 4: 본문 작성 ===
with tabs[3]:
    st.markdown("## 본문 작성")
    
    if not st.session_state['outline']:
        st.warning("먼저 목차를 생성해주세요.")
    else:
        # 챕터 선택
        selected_chapter = st.selectbox(
            "챕터 선택",
            st.session_state['outline'],
            key="chapter_select"
        )
        
        # 챕터 데이터 초기화
        if selected_chapter not in st.session_state['chapters']:
            st.session_state['chapters'][selected_chapter] = {
                'subtopics': ['소제목 1', '소제목 2', '소제목 3'],
                'subtopic_data': {}
            }
        
        chapter_data = st.session_state['chapters'][selected_chapter]
        
        # 소제목 리스트 확인 및 초기화
        if 'subtopics' not in chapter_data:
            chapter_data['subtopics'] = ['소제목 1', '소제목 2', '소제목 3']
        if 'subtopic_data' not in chapter_data:
            chapter_data['subtopic_data'] = {}
        
        for st_name in chapter_data['subtopics']:
            if st_name not in chapter_data['subtopic_data']:
                chapter_data['subtopic_data'][st_name] = {'questions': [], 'answers': [], 'content': ''}
        
        st.markdown("---")
        
        # 소제목 편집 섹션
        st.markdown('<p class="section-label">소제목 편집</p>', unsafe_allow_html=True)
        
        # AI 소제목 생성 버튼
        if st.button("✨ AI 소제목 생성", key="gen_subtopics"):
            with st.spinner("베스트셀러급 소제목 생성 중..."):
                subtopics_text = generate_subtopics(
                    selected_chapter,
                    st.session_state['topic'],
                    st.session_state['target_persona']
                )
                # 파싱
                new_subtopics = []
                for line in subtopics_text.split('\n'):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-')):
                        # "1. 소제목" 또는 "- 소제목" 형식 처리
                        cleaned = re.sub(r'^[\d\.\-\s]+', '', line).strip()
                        if cleaned:
                            new_subtopics.append(cleaned)
                
                if new_subtopics:
                    # 기존 데이터 초기화하고 새 소제목 적용
                    chapter_data['subtopics'] = new_subtopics[:3]
                    chapter_data['subtopic_data'] = {st: {'questions': [], 'answers': [], 'content': ''} for st in new_subtopics[:3]}
                    st.success("소제목 생성 완료!")
                    st.rerun()
        
        col_edit1, col_edit2 = st.columns([3, 1])
        with col_edit1:
            edited_subtopics = []
            for i, st_name in enumerate(chapter_data['subtopics']):
                edited_st = st.text_input(f"소제목 {i+1}", value=st_name, key=f"subtopic_edit_{selected_chapter}_{i}")
                edited_subtopics.append(edited_st)
        
        with col_edit2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("소제목 저장", key="save_subtopics"):
                # 기존 데이터 유지하면서 소제목 이름 업데이트
                old_subtopics = chapter_data['subtopics']
                new_subtopic_data = {}
                for i, new_name in enumerate(edited_subtopics):
                    if new_name.strip():
                        old_name = old_subtopics[i] if i < len(old_subtopics) else new_name
                        if old_name in chapter_data['subtopic_data']:
                            new_subtopic_data[new_name] = chapter_data['subtopic_data'][old_name]
                        else:
                            new_subtopic_data[new_name] = {'questions': [], 'answers': [], 'content': ''}
                
                chapter_data['subtopics'] = [s for s in edited_subtopics if s.strip()]
                chapter_data['subtopic_data'] = new_subtopic_data
                st.success("저장됨")
                st.rerun()
        
        st.markdown("---")
        
        # 소제목 선택
        selected_subtopic = st.selectbox(
            "작성할 소제목 선택",
            chapter_data['subtopics'],
            key="subtopic_select"
        )
        
        if selected_subtopic:
            if selected_subtopic not in chapter_data['subtopic_data']:
                chapter_data['subtopic_data'][selected_subtopic] = {'questions': [], 'answers': [], 'content': ''}
            
            subtopic_data = chapter_data['subtopic_data'][selected_subtopic]
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
                st.markdown(f"### 인터뷰: {selected_subtopic}")
                
                if st.button("질문 생성하기", key="gen_questions"):
                    with st.spinner("생성 중..."):
                        questions_text = generate_interview_questions(
                            selected_subtopic, 
                            selected_chapter, 
                            st.session_state['topic']
                        )
                        questions = re.findall(r'Q\d+:\s*(.+)', questions_text)
                        if not questions:
                            questions = [q.strip() for q in questions_text.split('\n') if q.strip() and '?' in q][:3]
                        subtopic_data['questions'] = questions
                        subtopic_data['answers'] = [''] * len(questions)
                
                if subtopic_data['questions']:
                    for i, q in enumerate(subtopic_data['questions']):
                        st.markdown(f"**Q{i+1}.** {q}")
                        if i >= len(subtopic_data['answers']):
                            subtopic_data['answers'].append('')
                        subtopic_data['answers'][i] = st.text_area(
                            f"A{i+1}",
                            value=subtopic_data['answers'][i],
                            key=f"answer_{selected_chapter}_{selected_subtopic}_{i}",
                            height=80,
                            label_visibility="collapsed"
                        )
            
            with col2:
                st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
                st.markdown(f"### 본문: {selected_subtopic}")
                
                if st.button("본문 생성하기", key="gen_content"):
                    if not subtopic_data['questions'] or not any(subtopic_data['answers']):
                        st.error("질문과 답변을 먼저 작성해주세요.")
                    else:
                        with st.spinner("작성 중... (30초~1분)"):
                            content = generate_subtopic_content(
                                selected_subtopic,
                                selected_chapter,
                                subtopic_data['questions'],
                                subtopic_data['answers'],
                                st.session_state['topic'],
                                st.session_state['target_persona']
                            )
                            subtopic_data['content'] = content
                
                if subtopic_data['content']:
                    edited_content = st.text_area(
                        "편집",
                        value=subtopic_data['content'],
                        height=400,
                        key=f"content_{selected_chapter}_{selected_subtopic}",
                        label_visibility="collapsed"
                    )
                    subtopic_data['content'] = edited_content
                    st.caption(f"{len(edited_content):,}자")
        
        st.markdown("---")
        
        # 챕터 전체 진행 상황
        st.markdown("### 챕터 진행 상황")
        for st_name in chapter_data['subtopics']:
            st_data = chapter_data['subtopic_data'].get(st_name, {})
            has_content = bool(st_data.get('content'))
            status = "✅" if has_content else "⬜"
            char_count = len(st_data.get('content', ''))
            st.markdown(f"{status} **{st_name}** - {char_count:,}자")
        
        # === 전체 미리보기 섹션 ===
        st.markdown("---")
        st.markdown("### 📖 전체 미리보기")
        
        with st.expander("작성된 전체 내용 보기 (클릭해서 펼치기)", expanded=False):
            preview_text = ""
            total_preview_chars = 0
            
            for ch in st.session_state['outline']:
                if ch in st.session_state['chapters']:
                    ch_data_preview = st.session_state['chapters'][ch]
                    chapter_has_content = False
                    chapter_content = ""
                    
                    if 'subtopic_data' in ch_data_preview:
                        for st_name in ch_data_preview.get('subtopics', []):
                            st_data_preview = ch_data_preview['subtopic_data'].get(st_name, {})
                            if st_data_preview.get('content'):
                                chapter_has_content = True
                                chapter_content += f"\n\n### {st_name}\n\n"
                                chapter_content += st_data_preview['content']
                    
                    if chapter_has_content:
                        preview_text += f"\n\n---\n\n## {ch}\n"
                        preview_text += chapter_content
                        total_preview_chars += len(chapter_content)
            
            if preview_text:
                st.markdown(f"**총 {total_preview_chars:,}자** (약 {total_preview_chars//1500}페이지)")
                st.markdown(preview_text)
            else:
                st.info("아직 작성된 내용이 없습니다.")

# === TAB 5: 문체 다듬기 ===
with tabs[4]:
    st.markdown("## 문체 다듬기")
    
    # 작성된 소제목 찾기
    completed_items = []
    for ch in st.session_state['outline']:
        if ch in st.session_state['chapters']:
            ch_data = st.session_state['chapters'][ch]
            if 'subtopic_data' in ch_data:
                for st_name, st_data in ch_data['subtopic_data'].items():
                    if st_data.get('content'):
                        completed_items.append((ch, st_name))
    
    if not completed_items:
        st.warning("먼저 본문을 작성해주세요.")
    else:
        # 챕터-소제목 선택
        chapter_options = list(set([item[0] for item in completed_items]))
        selected_ch = st.selectbox("챕터", chapter_options, key="refine_chapter_select")
        
        subtopic_options = [item[1] for item in completed_items if item[0] == selected_ch]
        selected_st = st.selectbox("소제목", subtopic_options, key="refine_subtopic_select")
        
        if selected_ch and selected_st:
            st_data = st.session_state['chapters'][selected_ch]['subtopic_data'][selected_st]
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
                st.markdown("### 스타일 변환")
                
                style = st.selectbox(
                    "문체",
                    ["친근한", "전문적", "직설적", "스토리텔링"],
                    key="style_select"
                )
                
                if st.button("변환하기", key="refine_btn"):
                    with st.spinner("변환 중..."):
                        refined = refine_content(st_data['content'], style)
                        st_data['refined'] = refined
                
                if st_data.get('refined'):
                    refined_edit = st.text_area(
                        "결과",
                        value=st_data['refined'],
                        height=400,
                        key="refined_content",
                        label_visibility="collapsed"
                    )
                    
                    if st.button("적용하기", key="apply_refined"):
                        st_data['content'] = refined_edit
                        st.success("적용됨")
            
            with col2:
                st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
                st.markdown("### 품질 검사")
                
                if st.button("검사하기", key="quality_btn"):
                    with st.spinner("분석 중..."):
                        quality = check_quality(st_data['content'])
                        st.markdown(f"""
                        <div class="info-card">
                            {quality.replace(chr(10), '<br>')}
                        </div>
                        """, unsafe_allow_html=True)

# === TAB 6: 최종 출력 ===
with tabs[5]:
    st.markdown("## 최종 출력")
    
    # 스타일 설정 섹션
    st.markdown('<p class="section-label">Style Settings</p>', unsafe_allow_html=True)
    st.markdown("### 📝 전자책 스타일 설정")
    
    col_style1, col_style2, col_style3, col_style4 = st.columns(4)
    
    with col_style1:
        font_family = st.selectbox(
            "본문 폰트",
            ["S-Core Dream", "Pretendard", "Noto Sans KR", "Noto Serif KR", "Gothic A1", "Nanum Gothic", "Nanum Myeongjo"],
            index=0,
            key="font_family"
        )
    
    with col_style2:
        font_size = st.selectbox(
            "본문 크기",
            ["14px", "15px", "16px", "17px", "18px", "20px"],
            index=2,
            key="font_size"
        )
    
    with col_style3:
        line_height = st.selectbox(
            "줄 간격",
            ["1.6", "1.8", "2.0", "2.2"],
            index=1,
            key="line_height"
        )
    
    with col_style4:
        text_color = st.selectbox(
            "본문 색상",
            ["#222222", "#333333", "#444444", "#000000"],
            index=0,
            key="text_color"
        )
    
    col_style5, col_style6, col_style7, col_style8 = st.columns(4)
    
    with col_style5:
        title_size = st.selectbox(
            "제목 크기",
            ["28px", "32px", "36px", "40px"],
            index=1,
            key="title_size"
        )
    
    with col_style6:
        chapter_size = st.selectbox(
            "챕터 크기",
            ["22px", "24px", "26px", "28px"],
            index=1,
            key="chapter_size"
        )
    
    with col_style7:
        subtopic_size = st.selectbox(
            "소제목 크기",
            ["18px", "20px", "22px"],
            index=1,
            key="subtopic_size"
        )
    
    with col_style8:
        max_width = st.selectbox(
            "본문 너비",
            ["640px", "720px", "800px", "100%"],
            index=1,
            key="max_width"
        )
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">Preview</p>', unsafe_allow_html=True)
        st.markdown("### 전자책")
        
        full_book = f"""# {st.session_state.get('book_title', '제목 없음')}
## {st.session_state.get('subtitle', '')}

---

"""
        total_chars = 0
        completed_subtopics = 0
        total_subtopics = 0
        
        for chapter in st.session_state['outline']:
            if chapter in st.session_state['chapters']:
                ch_data = st.session_state['chapters'][chapter]
                
                # 소제목별 콘텐츠 합치기
                if 'subtopic_data' in ch_data:
                    chapter_has_content = False
                    chapter_content = ""
                    
                    for st_name in ch_data.get('subtopics', []):
                        total_subtopics += 1
                        st_data = ch_data['subtopic_data'].get(st_name, {})
                        if st_data.get('content'):
                            chapter_has_content = True
                            completed_subtopics += 1
                            chapter_content += f"\n\n### {st_name}\n\n"
                            chapter_content += st_data['content']
                    
                    if chapter_has_content:
                        full_book += f"\n\n# {chapter}\n"
                        full_book += chapter_content
                        total_chars += len(chapter_content)
                
                # 기존 구조 호환 (content가 직접 있는 경우)
                elif ch_data.get('content'):
                    full_book += f"\n\n# {chapter}\n\n"
                    full_book += ch_data['content']
                    total_chars += len(ch_data['content'])
        
        st.text_area("원고", value=full_book, height=400, key="full_book", label_visibility="collapsed")
        
        total_chars = len(full_book)
        total_chapters = len(st.session_state['outline']) if st.session_state['outline'] else 1
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("글자수", f"{total_chars:,}")
        with col_stat2:
            st.metric("소제목", f"{completed_subtopics}/{total_subtopics}")
        with col_stat3:
            st.metric("페이지", f"~{total_chars//1500}")
        
        st.markdown("---")
        
        # HTML 콘텐츠 생성 (스타일 설정 적용)
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{st.session_state.get('book_title', '전자책')}</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&family=Noto+Serif+KR:wght@400;700&family=Gothic+A1:wght@400;700&family=Nanum+Gothic:wght@400;700&family=Nanum+Myeongjo:wght@400;700&display=swap" rel="stylesheet">
    <style>
        @font-face {{
            font-family: 'S-Core Dream';
            src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.2/S-CoreDream-3Light.woff') format('woff');
            font-weight: 300;
        }}
        @font-face {{
            font-family: 'S-Core Dream';
            src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.2/S-CoreDream-5Medium.woff') format('woff');
            font-weight: 500;
        }}
        @font-face {{
            font-family: 'S-Core Dream';
            src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.2/S-CoreDream-6Bold.woff') format('woff');
            font-weight: 700;
        }}
        @font-face {{
            font-family: 'Pretendard';
            src: url('https://cdn.jsdelivr.net/gh/Project-Noonnu/noonfonts_2107@1.1/Pretendard-Regular.woff') format('woff');
            font-weight: 400;
        }}
        @font-face {{
            font-family: 'Pretendard';
            src: url('https://cdn.jsdelivr.net/gh/Project-Noonnu/noonfonts_2107@1.1/Pretendard-Bold.woff') format('woff');
            font-weight: 700;
        }}
        body {{
            font-family: '{font_family}', sans-serif;
            max-width: {max_width};
            margin: 0 auto;
            padding: 60px 20px;
            line-height: {line_height};
            color: {text_color};
            font-size: {font_size};
            word-break: keep-all;
            font-weight: 500;
        }}
        h1 {{
            font-size: {title_size};
            font-weight: 700;
            margin-bottom: 10px;
            color: #111;
        }}
        h2 {{
            font-size: {chapter_size};
            font-weight: 700;
            margin-top: 60px;
            margin-bottom: 20px;
            color: #222;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        h3 {{
            font-size: {subtopic_size};
            font-weight: 700;
            margin-top: 40px;
            margin-bottom: 15px;
            color: #333;
        }}
        p {{
            margin-bottom: 1.2em;
            text-align: justify;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 40px 0;
        }}
    </style>
</head>
<body>
{full_book.replace(chr(10), '<br>')}
</body>
</html>"""
        
        col_dl1, col_dl2, col_dl3 = st.columns(3)
        with col_dl1:
            st.download_button(
                "TXT 다운로드",
                full_book,
                file_name=f"{st.session_state.get('book_title', 'ebook')}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
        
        with col_dl2:
            st.download_button(
                "HTML 다운로드",
                html_content,
                file_name=f"{st.session_state.get('book_title', 'ebook')}_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html"
            )
        
        with col_dl3:
            if st.button("미리보기", key="preview_btn"):
                st.session_state['show_preview'] = True
        
        # HTML 미리보기
        if st.session_state.get('show_preview'):
            st.markdown("---")
            st.markdown("### 스타일 미리보기")
            preview_sample = f"""
            <div style="font-family: '{font_family}', sans-serif; max-width: {max_width}; line-height: {line_height}; color: {text_color}; font-size: {font_size}; border: 1px solid #ddd; padding: 30px; border-radius: 8px; background: #fff;">
                <h1 style="font-size: {title_size}; font-weight: 700; color: #111; margin-bottom: 5px;">{st.session_state.get('book_title', '전자책 제목')}</h1>
                <p style="color: #666; font-size: 14px;">{st.session_state.get('subtitle', '부제목')}</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <h2 style="font-size: {chapter_size}; font-weight: 700; color: #222;">챕터1: 왜 열심히 하는 사람이 가난할까</h2>
                <h3 style="font-size: {subtopic_size}; font-weight: 700; color: #333;">그날 통장 잔고 47만원</h3>
                <p>2019년 3월. 통장 잔고를 확인했다. 47만원. 월급날까지 2주. 나는 바닥이었다.</p>
                <p>솔직히 말할게. 나도 처음엔 몰랐어. 열심히만 하면 되는 줄 알았거든. 새벽 6시에 일어나서 밤 11시까지 일했어. 주말도 없었어.</p>
            </div>
            """
            st.markdown(preview_sample, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p class="section-label">Marketing</p>', unsafe_allow_html=True)
        st.markdown("### 마케팅 카피")
        
        if st.button("카피 생성하기", key="marketing_btn"):
            with st.spinner("생성 중..."):
                marketing = generate_marketing_copy(
                    st.session_state.get('book_title', st.session_state['topic']),
                    st.session_state.get('subtitle', ''),
                    st.session_state['topic'],
                    st.session_state['target_persona']
                )
                st.session_state['marketing_copy'] = marketing
        
        if st.session_state.get('marketing_copy'):
            st.markdown(f"""
            <div class="info-card">
                {st.session_state['marketing_copy'].replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)

# --- 푸터 ---
st.markdown("""
<div class="premium-footer">
    <span class="premium-footer-text">전자책 작성 프로그램 — </span><span class="premium-footer-author">남현우 작가</span>
</div>
""", unsafe_allow_html=True)
