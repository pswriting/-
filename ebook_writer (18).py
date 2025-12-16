import streamlit as st
import google.generativeai as genai
import re
import json
import io
import os
from datetime import datetime
from pathlib import Path

# ==========================================
# API 키 저장/불러오기 (로컬 파일)
# ==========================================
def get_config_path():
    """설정 파일 경로 반환"""
    home = Path.home()
    return home / ".ebook_app_config.json"

def load_saved_api_key():
    """저장된 API 키 불러오기"""
    config_path = get_config_path()
    try:
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('api_key', '')
    except Exception:
        pass
    return ''

def save_api_key(api_key):
    """API 키 저장"""
    config_path = get_config_path()
    try:
        config = {}
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        config['api_key'] = api_key
        with open(config_path, 'w') as f:
            json.dump(config, f)
        return True
    except Exception:
        return False

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
    
    * { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif; }
    
    .stDeployButton {display:none;} 
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    [data-testid="collapsedControl"] { display: flex !important; visibility: visible !important; }
    
    .stApp { background: #ffffff; }
    
    .main .block-container { background: #ffffff; padding: 2rem 3rem; max-width: 1200px; }
    
    [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #eeeeee; }
    [data-testid="stSidebar"] * { color: #222222 !important; }
    [data-testid="stSidebar"] .stProgress > div > div > div > div { background: #222222; border-radius: 10px; }
    
    .stMarkdown, .stText, p, span, label, .stMarkdown p { color: #222222 !important; line-height: 1.7; }
    
    h1 { color: #111111 !important; font-weight: 700 !important; font-size: 2rem !important; letter-spacing: -0.5px; margin-bottom: 1rem !important; }
    h2 { color: #111111 !important; font-weight: 700 !important; font-size: 1.4rem !important; margin-top: 2rem !important; margin-bottom: 1rem !important; }
    h3 { color: #222222 !important; font-weight: 600 !important; font-size: 1.1rem !important; margin-bottom: 0.8rem !important; }
    
    .stTabs [data-baseweb="tab-list"] { background: transparent; gap: 0; border-bottom: 2px solid #eeeeee; padding: 0; }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #888888 !important; border-radius: 0; font-weight: 500; padding: 16px 24px; font-size: 15px; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 0.2s; }
    .stTabs [data-baseweb="tab"]:hover { color: #222222 !important; }
    .stTabs [aria-selected="true"] { background: transparent !important; color: #111111 !important; font-weight: 700 !important; border-bottom: 2px solid #111111 !important; }
    
    .stButton > button { width: 100%; border-radius: 30px; font-weight: 600; background: #111111 !important; color: #ffffff !important; border: none !important; padding: 14px 32px; font-size: 15px; transition: all 0.2s; box-shadow: none; }
    .stButton > button:hover { background: #333333 !important; color: #ffffff !important; box-shadow: 0 4px 12px rgba(0,0,0,0.15); transform: translateY(-1px); }
    .stButton > button:active { transform: translateY(0); }
    .stButton > button p, .stButton > button span, .stButton > button div, .stButton > button * { color: #ffffff !important; }
    
    .stDownloadButton > button { background: #2d5a27 !important; color: #ffffff !important; border-radius: 30px; }
    .stDownloadButton > button:hover { background: #3d7a37 !important; }
    .stDownloadButton > button p, .stDownloadButton > button span, .stDownloadButton > button * { color: #ffffff !important; }
    
    .stTextInput > div > div > input, .stTextArea > div > div > textarea { background: #ffffff !important; border: 1px solid #dddddd !important; border-radius: 8px !important; color: #222222 !important; padding: 14px 16px !important; font-size: 15px !important; }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus { border-color: #111111 !important; box-shadow: none !important; }
    .stTextInput > div > div > input::placeholder, .stTextArea > div > div > textarea::placeholder { color: #aaaaaa !important; }
    
    .stSelectbox > div > div { background: #ffffff !important; border: 1px solid #dddddd !important; border-radius: 8px !important; }
    .stSelectbox > div > div > div { color: #222222 !important; }
    
    [data-testid="stMetricValue"] { color: #111111 !important; font-size: 2rem !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #666666 !important; }
    
    .stSuccess { background: #f0f9f0 !important; border: 1px solid #c8e6c9 !important; border-radius: 8px !important; }
    .stSuccess p { color: #2e7d32 !important; }
    .stWarning { background: #fff8e1 !important; border: 1px solid #ffecb3 !important; border-radius: 8px !important; }
    .stWarning p { color: #f57c00 !important; }
    .stError { background: #ffebee !important; border: 1px solid #ffcdd2 !important; border-radius: 8px !important; }
    .stError p { color: #c62828 !important; }
    .stInfo { background: #e3f2fd !important; border: 1px solid #bbdefb !important; border-radius: 8px !important; }
    .stInfo p { color: #1565c0 !important; }
    
    hr { border: none !important; border-top: 1px solid #eeeeee !important; margin: 2rem 0 !important; }
    .stProgress > div > div > div > div { background: #222222; border-radius: 10px; }
    
    .login-container { max-width: 400px; margin: 100px auto; padding: 40px; background: #ffffff; border: 1px solid #eeeeee; border-radius: 20px; text-align: center; }
    .login-title { font-size: 28px; font-weight: 700; color: #111111; margin-bottom: 8px; }
    .login-subtitle { font-size: 15px; color: #888888; margin-bottom: 30px; }
    
    .hero-section { text-align: center; padding: 60px 20px; margin-bottom: 40px; }
    .hero-label { font-size: 13px; font-weight: 600; color: #666666; letter-spacing: 3px; margin-bottom: 16px; text-transform: uppercase; }
    .hero-title { font-size: 42px; font-weight: 800; color: #111111; margin-bottom: 16px; letter-spacing: -1px; line-height: 1.2; }
    .hero-subtitle { font-size: 18px; color: #666666; font-weight: 400; }
    
    .section-label { font-size: 12px; font-weight: 600; color: #888888; letter-spacing: 2px; margin-bottom: 8px; text-transform: uppercase; }
    
    .score-card { background: #f8f8f8; border-radius: 20px; padding: 50px 40px; text-align: center; }
    .score-number { font-size: 80px; font-weight: 800; color: #111111; line-height: 1; margin-bottom: 8px; }
    .score-label { color: #888888; font-size: 14px; font-weight: 500; }
    
    .status-badge { display: inline-block; padding: 8px 20px; border-radius: 20px; font-weight: 600; font-size: 13px; margin-top: 20px; }
    .status-excellent { background: #111111; color: #ffffff; }
    .status-good { background: #f0f0f0; color: #333333; }
    .status-warning { background: #fff3e0; color: #e65100; }
    
    .info-card { background: #f8f8f8; border-radius: 16px; padding: 24px; margin: 16px 0; }
    .info-card-title { font-size: 12px; font-weight: 700; color: #888888; letter-spacing: 1px; margin-bottom: 12px; text-transform: uppercase; }
    .info-card p { color: #333333 !important; font-size: 15px; line-height: 1.8; margin: 8px 0; }
    
    .title-card { background: #ffffff; border: 1px solid #eeeeee; border-radius: 16px; padding: 24px; margin: 12px 0; transition: all 0.2s; }
    .title-card:hover { border-color: #cccccc; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
    .title-card .card-number { font-size: 12px; font-weight: 600; color: #aaaaaa; margin-bottom: 8px; }
    .title-card .main-title { color: #111111; font-size: 18px; font-weight: 700; margin-bottom: 6px; }
    .title-card .sub-title { color: #666666; font-size: 14px; margin-bottom: 16px; }
    .title-card .reason { color: #444444; font-size: 14px; padding: 14px 16px; background: #f8f8f8; border-radius: 10px; line-height: 1.6; }
    
    .score-item { background: #ffffff; border: 1px solid #eeeeee; border-radius: 12px; padding: 16px 20px; margin: 10px 0; display: flex; justify-content: space-between; align-items: center; }
    .score-item-label { color: #333333; font-weight: 500; font-size: 15px; }
    .score-item-value { color: #111111; font-weight: 700; font-size: 20px; }
    .score-item-reason { color: #666666; font-size: 14px; margin-top: 4px; line-height: 1.5; }
    
    .summary-box { background: #f8f8f8; border-radius: 12px; padding: 20px; margin-top: 20px; }
    .summary-box p { color: #333333 !important; font-size: 15px; line-height: 1.7; }
    
    .premium-footer { text-align: center; padding: 40px 20px; margin-top: 60px; border-top: 1px solid #eeeeee; }
    .premium-footer-text { color: #888888; font-size: 14px; }
    .premium-footer-author { color: #222222; font-weight: 600; }
    
    .empty-state { text-align: center; padding: 60px 20px; background: #f8f8f8; border-radius: 16px; }
    .empty-state p { color: #888888 !important; }
    
    .quick-action-box { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: 1px dashed #dee2e6; border-radius: 16px; padding: 24px; margin: 16px 0; text-align: center; }
    .quick-action-box p { color: #495057 !important; font-size: 14px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 비밀번호 설정
# ==========================================
CORRECT_PASSWORD = "cashmaker2024"

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
    'topic': '', 'target_persona': '', 'pain_points': '', 'one_line_concept': '',
    'outline': [], 'chapters': {}, 'current_step': 1, 'market_analysis': '',
    'book_title': '', 'subtitle': '', 'topic_score': None, 'topic_verdict': None,
    'score_details': None, 'generated_titles': None, 'outline_mode': 'ai',
}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 사이드바 ---
with st.sidebar:
    st.markdown("### Progress")
    progress_items = [
        bool(st.session_state['topic']), bool(st.session_state['target_persona']),
        bool(st.session_state['outline']), len(st.session_state['chapters']) > 0,
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
    st.markdown("### 💾 저장/불러오기")
    save_data = {
        'topic': st.session_state.get('topic', ''), 'target_persona': st.session_state.get('target_persona', ''),
        'pain_points': st.session_state.get('pain_points', ''), 'one_line_concept': st.session_state.get('one_line_concept', ''),
        'outline': st.session_state.get('outline', []), 'chapters': st.session_state.get('chapters', {}),
        'book_title': st.session_state.get('book_title', ''), 'subtitle': st.session_state.get('subtitle', ''),
        'market_analysis': st.session_state.get('market_analysis', ''), 'topic_score': st.session_state.get('topic_score'),
        'topic_verdict': st.session_state.get('topic_verdict'), 'score_details': st.session_state.get('score_details'),
        'generated_titles': st.session_state.get('generated_titles'),
    }
    save_json = json.dumps(save_data, ensure_ascii=False, indent=2)
    file_name = st.session_state.get('book_title', '전자책') or '전자책'
    file_name = re.sub(r'[^\w\s가-힣-]', '', file_name)[:20]
    st.download_button("📥 작업 저장하기", save_json, file_name=f"{file_name}_{datetime.now().strftime('%m%d_%H%M')}.json", mime="application/json", use_container_width=True)
    
    uploaded_file = st.file_uploader("📤 작업 불러오기", type=['json'], label_visibility="collapsed")
    if uploaded_file is not None:
        try:
            loaded_data = json.loads(uploaded_file.read().decode('utf-8'))
            if st.button("불러오기 적용", use_container_width=True):
                for key in ['topic', 'target_persona', 'pain_points', 'one_line_concept', 'outline', 'chapters', 'book_title', 'subtitle', 'market_analysis', 'topic_score', 'topic_verdict', 'score_details', 'generated_titles']:
                    if key in loaded_data:
                        st.session_state[key] = loaded_data[key]
                st.success("불러오기 완료!")
                st.rerun()
        except Exception as e:
            st.error(f"파일 오류: {e}")
    
    st.markdown("---")
    st.markdown("### API 설정")
    if 'api_key' not in st.session_state:
        saved_key = load_saved_api_key()
        st.session_state['api_key'] = saved_key
    
    api_key_input = st.text_input("Gemini API 키", value=st.session_state['api_key'], type="password", placeholder="AIza...", help="Google AI Studio에서 발급받은 API 키를 입력하세요")
    if api_key_input and api_key_input != st.session_state['api_key']:
        st.session_state['api_key'] = api_key_input
        if save_api_key(api_key_input):
            st.toast("✅ API 키가 저장되었습니다!", icon="💾")
    elif api_key_input:
        st.session_state['api_key'] = api_key_input
    
    with st.expander("API 키 발급 방법 (무료)"):
        st.markdown("""**2분이면 끝!**\n\n1. [Google AI Studio](https://aistudio.google.com/apikey) 접속\n2. Google 계정으로 로그인\n3. **"API 키 만들기"** 클릭\n4. 생성된 키 복사\n5. 위 입력창에 붙여넣기\n\n✅ 완전 무료 ✅ 신용카드 불필요 ✅ 분당 15회 요청 가능""")
    
    if not st.session_state.get('api_key'):
        st.caption("⚠️ API 키를 입력하세요")
    else:
        col_status, col_del = st.columns([3, 1])
        with col_status:
            st.caption("✅ API 키 입력됨 (자동 저장)")
        with col_del:
            if st.button("🗑️", key="del_api_key", help="API 키 삭제"):
                st.session_state['api_key'] = ''
                save_api_key('')
                st.rerun()


# ==========================================
# 헬퍼 함수들
# ==========================================
def get_api_key():
    return st.session_state.get('api_key', '')

def get_auto_save_data():
    return {
        'topic': st.session_state.get('topic', ''), 'target_persona': st.session_state.get('target_persona', ''),
        'pain_points': st.session_state.get('pain_points', ''), 'one_line_concept': st.session_state.get('one_line_concept', ''),
        'outline': st.session_state.get('outline', []), 'chapters': st.session_state.get('chapters', {}),
        'book_title': st.session_state.get('book_title', ''), 'subtitle': st.session_state.get('subtitle', ''),
        'market_analysis': st.session_state.get('market_analysis', ''), 'topic_score': st.session_state.get('topic_score'),
        'topic_verdict': st.session_state.get('topic_verdict'), 'score_details': st.session_state.get('score_details'),
        'generated_titles': st.session_state.get('generated_titles'), 'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def sync_full_outline():
    if not st.session_state.get('outline'):
        return
    new_full_outline = ""
    for ch in st.session_state['outline']:
        new_full_outline += f"## {ch}\n"
        if ch in st.session_state.get('chapters', {}):
            for st_name in st.session_state['chapters'][ch].get('subtopics', []):
                new_full_outline += f"- {st_name}\n"
        new_full_outline += "\n"
    st.session_state['full_outline'] = new_full_outline.strip()

def trigger_auto_save():
    sync_full_outline()
    st.session_state['auto_save_trigger'] = True

def calculate_char_count(text):
    if not text:
        return 0
    return len(text.replace('\n', '').replace(' ', ''))

def get_all_content_text():
    pure_content = ""
    for ch in st.session_state.get('outline', []):
        if ch in st.session_state.get('chapters', {}):
            ch_data = st.session_state['chapters'][ch]
            if 'subtopic_data' in ch_data:
                subtopic_list = ch_data.get('subtopics', [])
                if not subtopic_list and ch in ch_data['subtopic_data']:
                    subtopic_list = [ch]
                for st_name in subtopic_list:
                    st_data = ch_data['subtopic_data'].get(st_name, {})
                    if st_data.get('content'):
                        pure_content += st_data['content']
    return pure_content

def clean_content_for_display(content, subtopic_title=None, chapter_title=None):
    if not content:
        return ""
    unicode_control_chars = ['\u200e', '\u200f', '\u202a', '\u202b', '\u202c', '\u202d', '\u202e', '\u2066', '\u2067', '\u2068', '\u2069', '\u200b', '\u200c', '\u200d', '\ufeff', '\u061c']
    for char in unicode_control_chars:
        content = content.replace(char, '')
    content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', content)
    content = re.sub(r'<[^>]+>', '', content)
    content = content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    lines = content.split('\n')
    cleaned_lines = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            if idx > 3 or len(cleaned_lines) > 0:
                cleaned_lines.append(line)
            continue
        if stripped.startswith('#'):
            continue
        if stripped.startswith('챕터') and ':' in stripped[:15]:
            continue
        if stripped.startswith('소제목') and ':' in stripped[:10]:
            continue
        if subtopic_title and idx < 5:
            clean_subtopic = subtopic_title.replace('**', '').strip()
            clean_stripped = stripped.replace('**', '').strip()
            if clean_stripped == clean_subtopic:
                continue
            if clean_subtopic in clean_stripped and len(clean_stripped) < len(clean_subtopic) + 20:
                continue
        if chapter_title and idx < 5:
            clean_chapter = chapter_title.replace('**', '').strip()
            if clean_chapter in stripped or stripped in clean_chapter:
                continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()

def escape_rtf_unicode(text):
    if not text:
        return ""
    result = []
    for char in text:
        code = ord(char)
        if code < 128:
            if char == '\\': result.append('\\\\')
            elif char == '{': result.append('\\{')
            elif char == '}': result.append('\\}')
            elif char == '\n': result.append('\\line ')
            elif char == '\r': continue
            else: result.append(char)
        else:
            signed_code = code - 65536 if code > 32767 else code
            result.append(f'\\u{signed_code}?')
    return ''.join(result)


# ==========================================
# AI 기본 함수
# ==========================================
def ask_ai(system_role, prompt, temperature=0.7):
    api_key = get_api_key()
    if not api_key:
        return "⚠️ API 키를 먼저 입력해주세요."
    try:
        genai.configure(api_key=api_key)
        ai_model = genai.GenerativeModel('gemini-2.5-pro')
        generation_config = genai.types.GenerationConfig(temperature=temperature)
        full_prompt = f"""당신은 {system_role}입니다.\n\n{prompt}\n\n한국어로 답변해주세요."""
        response = ai_model.generate_content(full_prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        return f"오류 발생: {str(e)}"


# ==========================================
# 🔥 핵심 개선: 목차 생성 함수 (프드프 킬러 목차)
# ==========================================
def generate_outline(topic, persona, pain_points):
    prompt = f"""주제: {topic}
타겟: {persona}
고민: {pain_points}

위 주제로 전자책 목차를 만들어주세요.

[킬러 목차 7가지 트리거]
1. 뒤통수: "열심히 하면 망하는 이유"
2. 숫자: "31개월 만에 10억", "하루 47분"
3. 빈칸: "상위 1%만 아는 '○○○'"
4. 공포: "지금 안 하면 5년 후 똑같다"
5. 비밀: "업계에서 절대 안 알려주는"
6. 스토리: "통장 잔고 47만원, 그날 밤"
7. 반전: "적게 일해야 더 번다"

[4챕터 감정 곡선]
챕터1: 충격 - "내가 잘못 알고 있었어?"
챕터2: 분노+깨달음 - "그래서 안 됐구나!"
챕터3: 희망+비밀 - "이게 진짜 방법이었어!"
챕터4: 확신+행동 - "나도 할 수 있겠다!"

[절대 금지]
- "~의 중요성", "~하는 방법", "효과적인", "성공적인"
- 물음표(?)로 끝나는 질문형
- "전략", "가이드", "노하우", "비법"

[⚠️ 반복 금지 - 매우 중요]
- "이것", "그것", "이거" 등 지시대명사 반복 금지
- 같은 단어가 2번 이상 나오면 안 됨
- 각 제목/소제목은 완전히 다른 표현 사용
- "~만 아는", "~의 비밀" 같은 패턴도 1번만 사용

[출력 규칙]
- 설명 없이 목차만 출력
- "물론입니다", "네" 등 인사말 금지
- 아래 형식 그대로만 출력

## 챕터1: [20자 이내 제목]
- [15자 이내 소제목]
- [15자 이내 소제목]
- [15자 이내 소제목]

## 챕터2: [20자 이내 제목]
- [15자 이내 소제목]
- [15자 이내 소제목]
- [15자 이내 소제목]

## 챕터3: [20자 이내 제목]
- [15자 이내 소제목]
- [15자 이내 소제목]
- [15자 이내 소제목]

## 챕터4: [20자 이내 제목]
- [15자 이내 소제목]
- [15자 이내 소제목]
- [15자 이내 소제목]"""
    return ask_ai("전자책 기획의 신", prompt, temperature=0.95)


# ==========================================
# 🔥 핵심 개선: 소제목 생성 함수
# ==========================================
def generate_subtopics(chapter_title, topic, persona, num_subtopics=3):
    prompt = f"""주제: {topic}
챕터: {chapter_title}
타겟: {persona}

이 챕터의 소제목 {num_subtopics}개를 만들어주세요.

[클릭 유발 공식 - 15자 이내]
1. 숫자+스토리: "통장 잔고 47만원, 그날"
2. 빈칸 호기심: "'○○○' 하나로 인생역전"
3. 뒤통수 반전: "열심히 할수록 망하는 이유"
4. 공포/긴급: "30대에 모르면 40대에 후회"
5. 비밀 공개: "업계에서 쉬쉬하는 그 방법"
6. Before/After: "알기 전 vs 알고 난 후"

[절대 금지]
- "~의 중요성", "~하는 방법"
- "효과적인", "성공적인"
- 15자 초과
- 물음표(?) 질문형

[⚠️ 반복 금지]
- "이것", "그것", "이거" 사용 금지
- 같은 단어 2번 이상 사용 금지
- 각 소제목은 완전히 다른 표현 사용
- "~만 아는", "~의 비밀" 패턴 1번만 사용

[출력 규칙]
- 설명 없이 소제목만 출력
- 번호와 소제목만

1. [소제목]
2. [소제목]
3. [소제목]"""
    return ask_ai("전자책 기획의 신", prompt, temperature=0.95)


def regenerate_chapter_outline(chapter_number, topic, persona, existing_chapters):
    chapter_emotions = {
        1: "충격 - '내가 잘못 알고 있었어?'",
        2: "분노+깨달음 - '그래서 안 됐구나!'",
        3: "희망+비밀 - '이게 진짜 방법이었어!'",
        4: "확신+행동 - '나도 할 수 있겠다!'"
    }
    emotion = chapter_emotions.get(chapter_number, "호기심 폭발")
    prompt = f"""주제: {topic}

{chapter_number}번째 챕터를 새로 만들어주세요.
감정선: {emotion}

[킬러 목차 트리거]
1. 뒤통수: "당신이 알던 건 틀렸다"
2. 숫자: "31개월 만에", "하루 47분"
3. 빈칸: "○○○ 하나로"
4. 공포: "지금 안 하면", "남들은 이미"
5. 비밀: "아무도 안 알려주는"
6. 스토리: "그날 새벽 3시"
7. 반전: "적게 일해야 더 번다"

[절대 금지]
- "~의 중요성", "~하는 방법"
- "효과적인", "성공적인"
- 물음표(?) 질문형

[⚠️ 반복 금지]
- "이것", "그것" 사용 금지
- 같은 단어 2번 이상 금지
- "~만 아는", "~의 비밀" 패턴 1번만

[출력 - 설명 없이 이 형식만]
## 챕터{chapter_number}: [20자 이내 제목]
- [15자 이내 소제목]
- [15자 이내 소제목]
- [15자 이내 소제목]"""
    return ask_ai("전자책 기획의 신", prompt, temperature=0.95)


def regenerate_single_subtopic(chapter_title, subtopic_index, topic, existing_subtopics):
    prompt = f"""주제: {topic}
챕터: {chapter_title}

{subtopic_index}번 소제목을 새로 만들어주세요.

[클릭 유발 공식 - 15자 이내]
1. 숫자+스토리: "통장 잔고 47만원, 그날"
2. 빈칸 호기심: "'○○○' 모르면 평생 제자리"
3. 뒤통수 반전: "열심히 할수록 망하는 이유"
4. 공포/긴급: "지금 안 하면 5년 후 똑같다"
5. 비밀 공개: "상위 1%만 아는 숨겨진 루트"
6. Before/After: "알기 전 vs 알고 난 후"

[절대 금지]
- "~의 중요성", "~하는 방법"
- "이것", "그것", "이거" 사용 금지
- 15자 초과
- 물음표(?) 질문형

소제목만 출력 (번호, 기호 없이):"""
    result = ask_ai("전자책 기획의 신", prompt, temperature=0.95)
    result = result.strip().strip('[]').strip('-').strip('"').strip("'").strip()
    if '\n' in result:
        result = result.split('\n')[0].strip()
    result = result.lstrip('0123456789.-) ').strip()
    return result


# ==========================================
# 🔥 핵심 개선: 본문 생성 함수 (자청 스타일, 1500자+)
# ==========================================
def generate_subtopic_content(subtopic_title, chapter_title, questions, answers, topic, persona):
    qa_pairs = ""
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        if a.strip():
            qa_pairs += f"\n질문{i}: {q}\n답변{i}: {a}\n"
    
    prompt = f"""당신은 "역행자" 자청, "부의 추월차선" 엠제이 드마코 수준의 베스트셀러 작가입니다.
당신의 글은 첫 문장부터 독자를 사로잡고, 마지막 문장까지 손에서 책을 놓지 못하게 만듭니다.

[집필 정보]
주제: {topic}
챕터: {chapter_title}
현재 작성할 소제목: {subtopic_title}
타겟: {persona}

⚠️ 매우 중요: 오직 '{subtopic_title}'에 대한 본문만 작성하세요.
- 다른 챕터나 소제목 내용을 언급하지 마세요
- 소제목 제목을 본문에 다시 쓰지 마세요

[작가 인터뷰 - 이 내용만 바탕으로 작성]
{qa_pairs}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 자청 스타일 글쓰기 10가지 법칙
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[법칙 1] 첫 문장 = 뒤통수 한 방 🥊
- 첫 문장에서 독자의 뒤통수를 쳐라
- 상식을 뒤집거나, 충격적인 사실로 시작
- 좋은 예: "월급 230만원. 그게 제 전부였습니다."
- 좋은 예: "저는 3번 망했습니다. 그리고 4번째에 성공했습니다."
- 좋은 예: "솔직히 말씀드릴게요. 저도 처음엔 사기라고 생각했습니다."
- 나쁜 예: "오늘은 ~에 대해 이야기해보겠습니다." (❌ 절대 금지)

[법칙 2] 짧은 문장, 강한 임팩트 💥
- 한 문장 = 한 호흡 (15~25자)
- 중요한 문장은 더 짧게 (10자 이하)
- 좋은 예: "그날. 모든 게 바뀌었습니다."
- 좋은 예: "단 3개월. 인생이 달라졌습니다."

[법칙 3] 문단 구성 = 리듬감 🎵
- 한 문단 = 3~5문장
- 문단과 문단 사이에 빈 줄 1개
- 절대 한 문장씩 띄어쓰지 마세요!
- 관련된 내용은 같은 문단에 묶으세요

[법칙 4] 스토리 > 설명 📖
- "~하세요"보다 "저는 ~했습니다"
- 추상적 조언 대신 구체적 경험
- Before(실패) → 깨달음 → After(성공) 구조

[법칙 5] 숫자로 증명하라 🔢
- 모호한 표현 대신 구체적 숫자
- "열심히 했다" → "새벽 4시에 일어났습니다"
- "많이 벌었다" → "월 847만원이 들어왔습니다"
- "빠르게 성장" → "3개월 만에 4배"

[법칙 6] 감정을 건드려라 ❤️
- 당시 감정을 생생하게 묘사
- "무서웠습니다", "분했습니다", "눈물이 났습니다"
- 단, 과잉 감정 표현은 금지

[법칙 7] 대화체 활용 💬
- 혼잣말, 내면의 목소리 삽입
- "이게 되겠어?" "아, 이거였구나"
- 독자와 대화하는 느낌

[법칙 8] 반복과 강조 🔄
- 핵심 메시지는 표현을 바꿔 2~3번 강조
- 같은 말을 다른 방식으로

[법칙 9] 구체적 장면 묘사 🎬
- 시간, 장소, 상황을 영화처럼
- "2019년 3월 어느 날, 강남역 스타벅스에서"
- "새벽 3시, 불 꺼진 사무실에서"

[법칙 10] 독자 = 친구 👋
- "당신"이 아니라 마치 옆에 앉은 친구에게 말하듯
- 딱딱한 설명 대신 대화하듯

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 문체 규칙 (합쇼체 100%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
모든 문장 끝:
✓ ~입니다 / ~습니다 / ~했습니다 / ~됩니다
✓ ~죠 / ~거죠 / ~셨죠 / ~네요
✓ ~세요 / ~하세요

절대 금지 (반말):
✗ ~다 / ~했다 / ~이다 / ~였다 / ~된다
✗ ~라 / ~인 것이다

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 AI 티 나는 표현 절대 금지
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
다음 표현 사용 시 0점 처리:
- "실수 1:", "실수 2:", "해결책:" (나열 금지)
- "첫째,", "둘째,", "셋째," (번호 금지)
- "중요합니다", "핵심입니다", "필수적입니다" (반복 금지)
- "따라서", "그러므로", "결론적으로" (딱딱한 연결어 금지)
- "~라고 할 수 있습니다" (에둘러 말하기 금지)
- "많은 분들이", "대부분의 사람들이" (일반화 금지)
- "~하는 것이 좋습니다" (조언체 금지)
- **굵은글씨**, *기울임*, 1. 2. 3. 번호 (마크다운 금지)
- "저는," (주어 뒤 쉼표 금지)
- "포기하지 마세요", "도전해보세요" (뻔한 교훈 금지)

대신 이렇게:
- 자연스러운 문장 연결로 이야기 전개
- 구체적 사례와 숫자로 설명
- "저는 ~했습니다. 결과는 ~였습니다."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ 베스트셀러급 본문 예시
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"2019년 3월. 통장 잔고를 확인했습니다. 47만원. 월급날까지 2주. 저는 완전히 바닥이었습니다.

매일 새벽 6시에 일어나서 밤 11시까지 일했습니다. 주말도 없었습니다. 성실함으로 치면 상위 1%였을 겁니다. 그런데 통장엔 47만원. 뭔가 심각하게 잘못됐다는 걸 그때 처음 깨달았습니다.

'열심히 하면 성공한다'는 말. 그게 거짓말이라는 걸 알기까지 5년이 걸렸습니다. 저는 방향이 틀렸던 겁니다. 열심히 잘못된 방향으로 달린 거죠.

그날 밤, 저는 처음으로 '왜'라는 질문을 던졌습니다. 왜 열심히 해도 안 될까? 왜 월급은 늘 부족할까? 왜 10년차도 신입과 크게 다르지 않을까?

답을 찾는 데 6개월이 걸렸습니다. 그리고 깨달았습니다. 문제는 '얼마나'가 아니라 '무엇을'이었습니다. 뭘 하느냐가 얼마나 하느냐보다 100배 중요했습니다.

그 깨달음 이후 모든 게 달라졌습니다. 3개월 만에 첫 부수입 100만원. 6개월 만에 월급을 넘었습니다. 1년 후, 저는 퇴사했습니다."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📏 분량: 1500~2000자 (공백 포함)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

반드시 1500자 이상 작성하세요. 
독자가 "이 부분만 읽어도 돈값 한다"고 느끼게 깊이 있는 내용을 담으세요.

[미션]
'{subtopic_title}'의 본문만 작성하세요.
- 자청 스타일 10가지 법칙 적용
- 합쇼체 100% 유지
- AI 티 나는 표현 완전 배제
- 1500자 이상 작성
- 첫 문장부터 뒤통수 치기"""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.8)


# ==========================================
# 기타 AI 함수들
# ==========================================
def analyze_topic_score(topic):
    prompt = f"""'{topic}' 주제의 전자책 적합도를 분석해주세요.

다음 5가지 항목을 각각 0~100점으로 채점하고, 종합 점수와 판정을 내려주세요.

채점 항목:
1. 시장성 (수요가 있는가?)
2. 수익성 (돈을 지불할 의향이 있는 주제인가?)
3. 차별화 가능성 (경쟁에서 이길 수 있는가?)
4. 작성 난이도 (전자책으로 만들기 쉬운가?)
5. 지속성 (오래 팔릴 수 있는가?)

반드시 아래 JSON 형식으로만 답변하세요:
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

[분석 대상]
주제: {topic}
타겟: {persona}  
타겟의 속마음: {pain_points}

[베스트셀러 제목의 핵심 원칙]
1. "읽는 순간 뒤통수를 맞은 느낌" - 기존 상식을 정면으로 뒤집어라
2. "이건 나만 몰랐던 거 아냐?" - 소외감과 긴급함을 동시에 자극
3. "구체적 숫자는 신뢰를 만든다" - 모호함 제거
4. "짧을수록 강하다" - 7자 이내 메인 타이틀

[절대 금지]
- "비법", "노하우", "성공", "방법", "전략", "가이드"
- "~하는 법", "~하기", "완벽한", "쉬운"
- 물음표로 끝나는 평범한 질문형

형식 (JSON만 출력):
{{
    "titles": [
        {{
            "title": "7자 이내 임팩트 제목",
            "subtitle": "15자 이내 보조 설명",
            "concept": "이 제목의 핵심 컨셉",
            "why_works": "왜 사람들이 이 제목에 끌리는지"
        }}
    ]
}}"""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.9)


def generate_concept(topic, persona, pain_points):
    prompt = f"""주제: {topic}
타겟: {persona}
타겟의 고민: {pain_points}

"이 책 안 읽으면 손해"라는 느낌을 주는 한 줄 컨셉 5개를 만들어주세요.

좋은 컨셉의 조건:
- 상식을 정면으로 부정 ("~한다고? 틀렸다")
- 호기심 자극 ("진짜 이유는 따로 있다")
- 구체적 숫자 포함 ("3개월 만에", "상위 1%")

출력 형식:
1. [한 줄 컨셉]
   → 왜 끌리는가

2. [한 줄 컨셉]
   → 왜 끌리는가

(5개까지)"""
    return ask_ai("카피라이터", prompt, temperature=0.9)


def generate_interview_questions(subtopic_title, chapter_title, topic):
    prompt = f"""당신은 베스트셀러 작가의 고스트라이터입니다.
'{topic}' 전자책의 '{chapter_title}' 챕터 중 '{subtopic_title}' 소제목 부분을 쓰기 위해 작가를 인터뷰합니다.

[좋은 질문의 특징]
1. 구체적 상황을 묻는다: "언제, 어디서, 어떻게"
2. 감정을 묻는다: "그때 기분이 어땠나요?"
3. 실패를 묻는다: "처음에 뭘 잘못했나요?"
4. 반전을 묻는다: "뭘 깨닫고 달라졌나요?"
5. 디테일을 묻는다: "구체적으로 어떻게 했나요?"

[좋은 질문 예시]
- "처음 이걸 시작했을 때 가장 크게 실패한 경험은 뭔가요?"
- "이걸 깨닫기 전과 후, 구체적으로 뭐가 달라졌나요? 숫자로 말해주실 수 있나요?"
- "이 방법을 처음 시도한 날, 그 상황을 자세히 묘사해주실 수 있나요?"

'{subtopic_title}' 소제목의 핵심 내용을 끌어낼 수 있는 인터뷰 질문 3개를 만들어주세요.

형식:
Q1: [질문]
Q2: [질문]
Q3: [질문]"""
    return ask_ai("베스트셀러 고스트라이터", prompt, temperature=0.7)


def refine_content(content, style="친근한"):
    style_guide = {
        "친근한": "친근한 스타일 - 합니다체, 자신감 있는 단정, 구체적 숫자와 팩트",
        "전문적": "전문가 스타일 - 합니다체, 데이터와 출처 강조, 논리적 전개",
        "직설적": "직설 스타일 - 합니다체, 핵심만 간결하게, 군더더기 제로",
        "스토리텔링": "스토리 스타일 - 합니다체, 구체적 장면 묘사, 대화체 활용"
    }
    prompt = f"""다음 글을 다듬어주세요.

[원본]
{content}

[수정 사항]
1. 반드시 "합니다체(존댓말)"로 통일
2. 한 문단은 3~5문장으로 구성
3. AI 티 나는 표현 모두 제거 ("따라서", "중요합니다" 반복 등)
4. 마크다운 제거 (**굵게**, *기울임*, 번호 매기기)

[목표 스타일]
{style_guide.get(style, style_guide["친근한"])}

다듬어진 글만 출력하세요."""
    return ask_ai("에디터", prompt, temperature=0.7)


def check_quality(content):
    prompt = f"""다음 글이 베스트셀러 수준인지 평가해주세요.

[평가할 글]
{content[:4000]}

[평가 기준]
1. 첫 문장 (10점) - 뒤통수를 치는가?
2. 몰입도 (10점) - 끝까지 읽게 되는가?
3. 공감력 (10점) - "내 얘기잖아"라고 느끼는가?
4. 구체성 (10점) - 구체적 장면/숫자가 있는가?
5. AI 티 (10점) - AI 표현이 있는가?

[출력 형식]
📊 종합 점수: __/50점

📌 각 항목 점수와 평가

✍️ 수정하면 좋을 문장 TOP 3

🎯 총평"""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.6)


def generate_marketing_copy(title, subtitle, topic, persona):
    prompt = f"""당신은 크몽에서 전자책을 수천 권 판매한 탑셀러입니다.

[상품 정보]
제목: {title}
부제: {subtitle}
주제: {topic}
타겟: {persona}

다음을 만들어주세요:

1. 크몽 상품 제목 (40자 이내) - 검색 키워드 포함

2. 상세페이지 헤드라인 3개 - 스크롤을 멈추게 만드는 한 줄

3. 구매 유도 문구 (CTA) 3개 - 긴급성 + FOMO 자극

4. 인스타그램 홍보 문구 - 훅 + 스토리 + CTA + 해시태그 5개

5. 블로그 포스팅 제목 3개 - 검색 유입 + 클릭 유도"""
    return ask_ai("크몽 탑셀러 마케터", prompt, temperature=0.85)


# ==========================================
# 메인 UI
# ==========================================
st.markdown("""
<div class="hero-section">
    <div class="hero-label">CASHMAKER</div>
    <div class="hero-title">전자책 작성 프로그램</div>
    <div class="hero-subtitle">쉽고, 빠른 전자책 수익화</div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["① 주제 선정", "② 타겟 & 컨셉", "③ 목차 설계", "④ 본문 작성", "⑤ 문체 다듬기", "⑥ 최종 출력"])

# === TAB 1: 주제 선정 ===
with tabs[0]:
    st.markdown("## 주제 선정 & 적합도 분석")
    st.markdown('<div class="quick-action-box"><p>💡 <strong>이미 주제가 있다면?</strong> 아래에 입력 후 바로 다음 탭으로 이동하세요!</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 주제 입력")
        topic_input = st.text_input("어떤 주제로 전자책을 쓰고 싶으세요?", value=st.session_state['topic'], placeholder="예: 크몽으로 월 500만원 벌기")
        if topic_input != st.session_state['topic']:
            st.session_state['topic'] = topic_input
            st.session_state['topic_score'] = None
            st.session_state['score_details'] = None
        
        st.markdown('<div class="info-card"><div class="info-card-title">좋은 주제의 조건</div><p>• 내가 직접 경험하고 성과를 낸 것</p><p>• 사람들이 돈 주고 배우고 싶어하는 것</p><p>• 구체적인 결과를 약속할 수 있는 것</p></div>', unsafe_allow_html=True)
        
        if st.button("📊 적합도 분석하기 (선택)", key="analyze_btn"):
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
            st.markdown(f'<div class="score-card"><div class="score-number">{score}</div><div class="score-label">종합 점수</div><span class="status-badge {verdict_class}">{verdict}</span></div>', unsafe_allow_html=True)
            if details:
                st.markdown("#### 세부 점수")
                for name, key in [("시장성", "market"), ("수익성", "profit"), ("차별화", "differentiation"), ("작성 난이도", "difficulty"), ("지속성", "sustainability")]:
                    score_val = details.get(key, {}).get('score', 0)
                    reason = details.get(key, {}).get('reason', '')
                    st.markdown(f'<div class="score-item"><span class="score-item-label">{name}</span><span class="score-item-value">{score_val}</span></div><p class="score-item-reason">{reason}</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="summary-box"><p><strong>종합 의견</strong><br>{details.get("summary", "")}</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state"><p>분석은 선택사항입니다.</p><p>주제만 입력해도 다음 단계로 진행 가능!</p></div>', unsafe_allow_html=True)

# === TAB 2: 타겟 & 컨셉 ===
with tabs[1]:
    st.markdown("## 타겟 설정 & 제목 생성")
    if not st.session_state['topic']:
        st.info("💡 주제를 먼저 입력하면 더 정확한 결과를 얻을 수 있어요.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 타겟 정의")
        if not st.session_state['topic']:
            topic_here = st.text_input("주제 (여기서 입력 가능)", value=st.session_state['topic'], placeholder="예: 크몽으로 월 500만원 벌기", key="topic_tab2")
            if topic_here:
                st.session_state['topic'] = topic_here
        persona = st.text_area("누가 이 책을 읽나요?", value=st.session_state['target_persona'], placeholder="예: 30대 직장인, 퇴근 후 부업으로 월 100만원 추가 수입을 원하는 사람", height=100)
        st.session_state['target_persona'] = persona
        pain_points = st.text_area("타겟의 가장 큰 고민은?", value=st.session_state['pain_points'], placeholder="예: 시간이 없다, 뭘 해야 할지 모르겠다, 시작이 두렵다", height=100)
        st.session_state['pain_points'] = pain_points
        
        st.markdown("---")
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 한 줄 컨셉")
        if st.button("컨셉 생성하기", key="concept_btn"):
            if not st.session_state['topic'] or not persona:
                st.error("주제와 타겟을 먼저 입력해주세요.")
            else:
                with st.spinner("생성 중..."):
                    concept = generate_concept(st.session_state['topic'], persona, pain_points)
                    st.session_state['one_line_concept'] = concept
        if st.session_state['one_line_concept']:
            st.markdown(f'<div class="info-card">{st.session_state["one_line_concept"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p class="section-label">Step 03</p>', unsafe_allow_html=True)
        st.markdown("### 제목 생성")
        if st.button("제목 생성하기", key="title_btn"):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요.")
            else:
                with st.spinner("생성 중..."):
                    titles_result = generate_titles_advanced(st.session_state['topic'], st.session_state['target_persona'], st.session_state['pain_points'])
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
                    st.markdown(f'<div class="title-card"><div class="card-number">TITLE 0{i}</div><div class="main-title">{t.get("title", "")}</div><div class="sub-title">{t.get("subtitle", "")}</div><div class="reason">{t.get("why_works", "")}</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<p class="section-label">Step 04</p>', unsafe_allow_html=True)
        st.markdown("### 최종 선택")
        st.session_state['book_title'] = st.text_input("제목", value=st.session_state['book_title'], placeholder="최종 제목")
        st.session_state['subtitle'] = st.text_input("부제", value=st.session_state['subtitle'], placeholder="부제")

# === TAB 3: 목차 설계 ===
with tabs[2]:
    st.markdown("## 목차 설계")
    st.markdown("### 🎯 작업 방식 선택")
    outline_mode = st.radio("목차를 어떻게 만드시겠어요?", ["🤖 자동으로 목차 생성", "✍️ 내가 직접 입력"], horizontal=True, key="outline_mode_radio")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if outline_mode == "🤖 자동으로 목차 생성":
            st.markdown('<p class="section-label">자동 목차 생성</p>', unsafe_allow_html=True)
            st.markdown("### 목차를 자동으로 설계합니다")
            if not st.session_state['topic']:
                st.warning("💡 주제를 먼저 입력해주세요")
                topic_here = st.text_input("주제", value=st.session_state['topic'], placeholder="예: 크몽으로 월 500만원 벌기", key="topic_tab3")
                if topic_here:
                    st.session_state['topic'] = topic_here
            
            if st.button("🚀 목차 생성하기", key="outline_btn"):
                if not st.session_state['topic']:
                    st.error("주제를 먼저 입력해주세요.")
                else:
                    with st.spinner("설계 중..."):
                        outline_text = generate_outline(st.session_state['topic'], st.session_state['target_persona'], st.session_state['pain_points'])
                        lines = outline_text.split('\n')
                        chapters = []
                        current_chapter = None
                        chapter_subtopics = {}
                        for line in lines:
                            line = line.strip()
                            if not line or line == '...':
                                continue
                            if line.startswith('##') or any(line.lower().startswith(kw) for kw in ['챕터', 'chapter']):
                                chapter_name = line.lstrip('#').strip()
                                current_chapter = chapter_name
                                chapters.append(current_chapter)
                                chapter_subtopics[current_chapter] = []
                            elif current_chapter and line.startswith('-'):
                                subtopic = line.lstrip('- ').strip()
                                if subtopic:
                                    chapter_subtopics[current_chapter].append(subtopic)
                        st.session_state['outline'] = chapters
                        # 순수 목차만 저장 (AI 설명문 제거)
                        clean_outline = ""
                        for ch in chapters:
                            clean_outline += f"## {ch}\n"
                            for st_name in chapter_subtopics.get(ch, []):
                                clean_outline += f"- {st_name}\n"
                            clean_outline += "\n"
                        st.session_state['full_outline'] = clean_outline.strip()
                        for ch in chapters:
                            subtopics = chapter_subtopics.get(ch, [])
                            st.session_state['chapters'][ch] = {'subtopics': subtopics, 'subtopic_data': {st: {'questions': [], 'answers': [], 'content': ''} for st in subtopics}}
                        total_subtopics = sum(len(chapter_subtopics.get(ch, [])) for ch in chapters)
                        st.success(f"✅ {len(chapters)}개 챕터, {total_subtopics}개 소제목 생성됨!")
                        st.rerun()
            
            if 'full_outline' in st.session_state and st.session_state['full_outline']:
                st.markdown("**📋 현재 목차**")
                st.code(st.session_state['full_outline'], language=None)
        else:
            st.markdown('<p class="section-label">직접 입력</p>', unsafe_allow_html=True)
            st.markdown("### 목차를 직접 입력하세요")
            st.markdown('<div class="info-card"><div class="info-card-title">📌 입력 형식 예시</div><p><b>챕터1: 첫 번째 챕터 제목</b></p><p style="margin-left: 20px;">- 소제목 1</p><p style="margin-left: 20px;">- 소제목 2</p></div>', unsafe_allow_html=True)
            existing_outline = ""
            if st.session_state['outline']:
                for ch in st.session_state['outline']:
                    existing_outline += f"## {ch}\n"
                    if ch in st.session_state['chapters']:
                        for st_name in st.session_state['chapters'][ch].get('subtopics', []):
                            existing_outline += f"- {st_name}\n"
            manual_outline = st.text_area("목차 입력", value=existing_outline, height=350, placeholder="## 챕터1: 제목\n- 소제목1\n- 소제목2\n\n## 챕터2: 제목\n- 소제목3", key="manual_outline_input")
            if st.button("✅ 목차 저장하기", key="save_manual_outline"):
                if manual_outline.strip():
                    lines = manual_outline.strip().split('\n')
                    chapters = []
                    current_chapter = None
                    chapter_subtopics = {}
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        if line.startswith('##') or any(line.lower().startswith(kw) for kw in ['챕터', 'chapter']):
                            chapter_name = line.lstrip('#').strip()
                            current_chapter = chapter_name
                            chapters.append(current_chapter)
                            chapter_subtopics[current_chapter] = []
                        elif current_chapter and line.startswith('-'):
                            subtopic = line.lstrip('- ').strip()
                            if subtopic:
                                chapter_subtopics[current_chapter].append(subtopic)
                    st.session_state['outline'] = chapters
                    st.session_state['full_outline'] = manual_outline
                    for ch in chapters:
                        subtopics = chapter_subtopics.get(ch, [])
                        st.session_state['chapters'][ch] = {'subtopics': subtopics, 'subtopic_data': {st_name: {'questions': [], 'answers': [], 'content': ''} for st_name in subtopics}}
                    trigger_auto_save()
                    total_subtopics = sum(len(chapter_subtopics.get(ch, [])) for ch in chapters)
                    st.success(f"✅ {len(chapters)}개 챕터, {total_subtopics}개 소제목 저장됨!")
                    st.rerun()
    
    with col2:
        st.markdown('<p class="section-label">목차 관리</p>', unsafe_allow_html=True)
        st.markdown("### 📋 현재 목차")
        if st.session_state['outline']:
            for i, chapter in enumerate(st.session_state['outline']):
                subtopic_count = len(st.session_state['chapters'].get(chapter, {}).get('subtopics', []))
                with st.expander(f"**{chapter}** ({subtopic_count}개 소제목)", expanded=False):
                    col_edit, col_actions = st.columns([3, 2])
                    with col_edit:
                        new_title = st.text_input("챕터 제목", value=chapter, key=f"edit_chapter_{i}", label_visibility="collapsed")
                    with col_actions:
                        col_regen, col_del = st.columns(2)
                        with col_regen:
                            if st.button("🔄", key=f"regen_chapter_{i}", help="재생성"):
                                with st.spinner("재생성 중..."):
                                    new_chapter_text = regenerate_chapter_outline(i + 1, st.session_state['topic'], st.session_state['target_persona'], st.session_state['outline'])
                                    lines = new_chapter_text.split('\n')
                                    new_chapter_title = None
                                    new_subtopics = []
                                    for line in lines:
                                        line = line.strip()
                                        if line.startswith('##'):
                                            new_chapter_title = line.lstrip('#').strip()
                                        elif line.startswith('-'):
                                            st_name = line.lstrip('- ').strip()
                                            if st_name:
                                                new_subtopics.append(st_name)
                                    if new_chapter_title:
                                        old_chapter = st.session_state['outline'][i]
                                        st.session_state['outline'][i] = new_chapter_title
                                        if old_chapter in st.session_state['chapters']:
                                            del st.session_state['chapters'][old_chapter]
                                        st.session_state['chapters'][new_chapter_title] = {'subtopics': new_subtopics, 'subtopic_data': {st: {'questions': [], 'answers': [], 'content': ''} for st in new_subtopics}}
                                        trigger_auto_save()
                                        st.rerun()
                        with col_del:
                            if st.button("🗑️", key=f"del_chapter_{i}", help="삭제"):
                                old_chapter = st.session_state['outline'].pop(i)
                                if old_chapter in st.session_state['chapters']:
                                    del st.session_state['chapters'][old_chapter]
                                trigger_auto_save()
                                st.rerun()
                    if new_title != chapter and new_title.strip():
                        if st.button("💾 제목 저장", key=f"save_chapter_title_{i}"):
                            st.session_state['outline'][i] = new_title
                            if chapter in st.session_state['chapters']:
                                st.session_state['chapters'][new_title] = st.session_state['chapters'].pop(chapter)
                            trigger_auto_save()
                            st.rerun()
                    st.markdown("---")
                    st.markdown("**📝 소제목**")
                    if chapter in st.session_state['chapters']:
                        subtopics = st.session_state['chapters'][chapter].get('subtopics', [])
                        for j, st_name in enumerate(subtopics):
                            col_st, col_st_actions = st.columns([3, 2])
                            with col_st:
                                new_st = st.text_input(f"소제목 {j+1}", value=st_name, key=f"edit_st_{i}_{j}", label_visibility="collapsed")
                            with col_st_actions:
                                col_st_regen, col_st_del = st.columns(2)
                                with col_st_regen:
                                    if st.button("🔄", key=f"regen_st_{i}_{j}", help="재생성"):
                                        with st.spinner("재생성 중..."):
                                            new_st_title = regenerate_single_subtopic(chapter, j + 1, st.session_state['topic'], subtopics)
                                            if new_st_title:
                                                old_st = st.session_state['chapters'][chapter]['subtopics'][j]
                                                st.session_state['chapters'][chapter]['subtopics'][j] = new_st_title
                                                if old_st in st.session_state['chapters'][chapter]['subtopic_data']:
                                                    st.session_state['chapters'][chapter]['subtopic_data'][new_st_title] = st.session_state['chapters'][chapter]['subtopic_data'].pop(old_st)
                                                else:
                                                    st.session_state['chapters'][chapter]['subtopic_data'][new_st_title] = {'questions': [], 'answers': [], 'content': ''}
                                                trigger_auto_save()
                                                st.rerun()
                                with col_st_del:
                                    if st.button("🗑️", key=f"del_st_{i}_{j}", help="삭제"):
                                        removed_st = st.session_state['chapters'][chapter]['subtopics'].pop(j)
                                        if removed_st in st.session_state['chapters'][chapter]['subtopic_data']:
                                            del st.session_state['chapters'][chapter]['subtopic_data'][removed_st]
                                        trigger_auto_save()
                                        st.rerun()
                            if new_st != st_name and new_st.strip():
                                if st.button("💾", key=f"save_st_{i}_{j}", help="저장"):
                                    st.session_state['chapters'][chapter]['subtopics'][j] = new_st
                                    if st_name in st.session_state['chapters'][chapter]['subtopic_data']:
                                        st.session_state['chapters'][chapter]['subtopic_data'][new_st] = st.session_state['chapters'][chapter]['subtopic_data'].pop(st_name)
                                    trigger_auto_save()
                                    st.rerun()
            st.markdown("---")
            if st.button("➕ 새 챕터 추가", key="add_chapter"):
                new_ch_name = f"챕터{len(st.session_state['outline'])+1}: 새 챕터"
                st.session_state['outline'].append(new_ch_name)
                st.session_state['chapters'][new_ch_name] = {'subtopics': [], 'subtopic_data': {}}
                trigger_auto_save()
                st.rerun()
        else:
            st.markdown('<div class="empty-state"><p>왼쪽에서 목차를 생성하거나 직접 입력하세요</p></div>', unsafe_allow_html=True)


# === TAB 4: 본문 작성 ===
with tabs[3]:
    st.markdown("## 본문 작성")
    if not st.session_state['outline']:
        st.warning("⚠️ 먼저 '③ 목차 설계' 탭에서 목차를 작성해주세요.")
        st.stop()
    
    chapter_list = [item for item in st.session_state['outline'] if not item.strip().startswith('-')]
    if not chapter_list:
        st.warning("⚠️ 챕터가 없습니다.")
        st.stop()
    
    selected_chapter = st.selectbox("📚 챕터 선택", chapter_list, key="chapter_select_main")
    if selected_chapter not in st.session_state['chapters']:
        st.session_state['chapters'][selected_chapter] = {'subtopics': [], 'subtopic_data': {}}
    chapter_data = st.session_state['chapters'][selected_chapter]
    if 'subtopics' not in chapter_data:
        chapter_data['subtopics'] = []
    if 'subtopic_data' not in chapter_data:
        chapter_data['subtopic_data'] = {}
    
    st.markdown("---")
    
    # 소제목 전체 보기
    with st.expander(f"📋 '{selected_chapter}' 소제목 ({len(chapter_data.get('subtopics', []))}개)", expanded=False):
        if chapter_data.get('subtopics'):
            for j, st_name in enumerate(chapter_data['subtopics']):
                has_content = bool(chapter_data['subtopic_data'].get(st_name, {}).get('content', '').strip())
                status_icon = "✅" if has_content else "⬜"
                col_st_view, col_st_regen = st.columns([5, 1])
                with col_st_view:
                    st.write(f"{status_icon} {j+1}. {st_name}")
                with col_st_regen:
                    if st.button("🔄", key=f"regen_st_tab4_{j}", help="재생성"):
                        with st.spinner("재생성 중..."):
                            new_title = regenerate_single_subtopic(selected_chapter, j + 1, st.session_state['topic'], chapter_data['subtopics'])
                            if new_title:
                                old_st = chapter_data['subtopics'][j]
                                chapter_data['subtopics'][j] = new_title
                                if old_st in chapter_data['subtopic_data']:
                                    chapter_data['subtopic_data'][new_title] = chapter_data['subtopic_data'].pop(old_st)
                                else:
                                    chapter_data['subtopic_data'][new_title] = {'questions': [], 'answers': [], 'content': ''}
                                trigger_auto_save()
                                st.rerun()
    
    st.markdown("---")
    
    if chapter_data['subtopics']:
        st.markdown("### ✍️ 본문 작성")
        selected_subtopic = st.selectbox("작성할 소제목", chapter_data['subtopics'], key="subtopic_select_main", format_func=lambda x: f"{'✅' if chapter_data['subtopic_data'].get(x, {}).get('content') else '⬜'} {x}")
        
        completed = sum(1 for s in chapter_data['subtopics'] if chapter_data['subtopic_data'].get(s, {}).get('content'))
        total = len(chapter_data['subtopics'])
        st.progress(completed / total if total > 0 else 0)
        st.caption(f"진행: {completed}/{total} 완료")
        st.markdown("---")
        
        if selected_subtopic:
            if selected_subtopic not in chapter_data['subtopic_data']:
                chapter_data['subtopic_data'][selected_subtopic] = {'questions': [], 'answers': [], 'content': ''}
            subtopic_data = chapter_data['subtopic_data'][selected_subtopic]
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
                st.markdown(f"### 🎤 인터뷰: {selected_subtopic}")
                if st.button("🎤 질문 생성하기", key="gen_questions_main"):
                    with st.spinner("질문 생성 중..."):
                        questions_text = generate_interview_questions(selected_subtopic, selected_chapter, st.session_state['topic'])
                        questions = re.findall(r'Q\d+:\s*(.+)', questions_text)
                        if not questions:
                            questions = [q.strip() for q in questions_text.split('\n') if q.strip() and '?' in q][:3]
                        subtopic_data['questions'] = questions
                        subtopic_data['answers'] = [''] * len(questions)
                        st.rerun()
                
                if subtopic_data['questions']:
                    for i, q in enumerate(subtopic_data['questions']):
                        st.markdown(f"**Q{i+1}.** {q}")
                        if i >= len(subtopic_data['answers']):
                            subtopic_data['answers'].append('')
                        subtopic_data['answers'][i] = st.text_area(f"A{i+1}", value=subtopic_data['answers'][i], key=f"answer_main_{selected_chapter}_{selected_subtopic}_{i}", height=80, label_visibility="collapsed")
                else:
                    st.info("👆 '질문 생성하기' 버튼을 눌러 인터뷰를 시작하세요.")
            
            with col2:
                st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
                st.markdown(f"### 📝 본문: {selected_subtopic}")
                has_answers = subtopic_data.get('questions') and any(a.strip() for a in subtopic_data.get('answers', []))
                content_widget_key = f"content_main_{selected_chapter}_{selected_subtopic}"
                
                if has_answers:
                    if st.button("✨ 본문 생성하기", key="gen_content_main"):
                        with st.spinner("집필 중... (30초~1분)"):
                            content = generate_subtopic_content(selected_subtopic, selected_chapter, subtopic_data['questions'], subtopic_data['answers'], st.session_state['topic'], st.session_state['target_persona'])
                            st.session_state['chapters'][selected_chapter]['subtopic_data'][selected_subtopic]['content'] = content
                            st.session_state[content_widget_key] = content
                            trigger_auto_save()
                            st.rerun()
                else:
                    st.info("👈 먼저 인터뷰 질문에 답변해주세요.")
                
                stored_content = st.session_state['chapters'][selected_chapter]['subtopic_data'][selected_subtopic].get('content', '')
                current_selection_key = f"_last_selected_{selected_chapter}"
                last_selected = st.session_state.get(current_selection_key, None)
                if last_selected != selected_subtopic:
                    st.session_state[content_widget_key] = stored_content
                    st.session_state[current_selection_key] = selected_subtopic
                elif content_widget_key not in st.session_state:
                    st.session_state[content_widget_key] = stored_content
                
                edited_content = st.text_area("본문 내용", height=400, key=content_widget_key, label_visibility="collapsed")
                if content_widget_key in st.session_state:
                    st.session_state['chapters'][selected_chapter]['subtopic_data'][selected_subtopic]['content'] = st.session_state[content_widget_key]
                
                final_content = st.session_state['chapters'][selected_chapter]['subtopic_data'][selected_subtopic].get('content', '')
                if final_content:
                    char_count = calculate_char_count(final_content)
                    st.caption(f"📊 {char_count:,}자")
                    st.success(f"✅ '{selected_subtopic}' 본문 작성 완료!")
        
        with st.expander("⚙️ 소제목 편집/추가", expanded=False):
            col_gen, col_add = st.columns(2)
            with col_gen:
                num_subtopics = st.number_input("생성할 개수", min_value=1, max_value=10, value=3, key="num_subtopics_gen_exp")
                if st.button("✨ 소제목 자동 생성", key="gen_subtopics_exp"):
                    with st.spinner("생성 중..."):
                        subtopics_text = generate_subtopics(selected_chapter, st.session_state['topic'], st.session_state['target_persona'], num_subtopics)
                        new_subtopics = []
                        for line in subtopics_text.split('\n'):
                            line = line.strip()
                            if line and (line[0].isdigit() or line.startswith('-')):
                                cleaned = re.sub(r'^[\d\.\-\s]+', '', line).strip()
                                if cleaned:
                                    new_subtopics.append(cleaned)
                        if new_subtopics:
                            chapter_data['subtopics'] = new_subtopics[:num_subtopics]
                            for st_name in new_subtopics[:num_subtopics]:
                                if st_name not in chapter_data['subtopic_data']:
                                    chapter_data['subtopic_data'][st_name] = {'questions': [], 'answers': [], 'content': ''}
                            st.success(f"✅ {len(new_subtopics[:num_subtopics])}개 생성됨!")
                            st.rerun()
            with col_add:
                new_name = st.text_input("새 소제목", placeholder="직접 입력", key="new_subtopic_exp")
                if st.button("➕ 추가", key="add_subtopic_exp"):
                    if new_name.strip() and new_name not in chapter_data['subtopics']:
                        chapter_data['subtopics'].append(new_name)
                        chapter_data['subtopic_data'][new_name] = {'questions': [], 'answers': [], 'content': ''}
                        st.rerun()
    else:
        st.warning("⚠️ 이 챕터에 소제목이 없습니다.")
        col_gen, col_add = st.columns(2)
        with col_gen:
            num_subtopics = st.number_input("생성할 개수", min_value=1, max_value=10, value=3, key="num_subtopics_gen_empty")
            if st.button("✨ 소제목 자동 생성", key="gen_subtopics_empty"):
                with st.spinner("생성 중..."):
                    subtopics_text = generate_subtopics(selected_chapter, st.session_state['topic'], st.session_state['target_persona'], num_subtopics)
                    new_subtopics = []
                    for line in subtopics_text.split('\n'):
                        line = line.strip()
                        if line and (line[0].isdigit() or line.startswith('-')):
                            cleaned = re.sub(r'^[\d\.\-\s]+', '', line).strip()
                            if cleaned:
                                new_subtopics.append(cleaned)
                    if new_subtopics:
                        chapter_data['subtopics'] = new_subtopics[:num_subtopics]
                        for st_name in new_subtopics[:num_subtopics]:
                            chapter_data['subtopic_data'][st_name] = {'questions': [], 'answers': [], 'content': ''}
                        st.success(f"✅ {len(new_subtopics[:num_subtopics])}개 생성됨!")
                        st.rerun()
        with col_add:
            new_subtopic_name = st.text_input("소제목 이름", placeholder="직접 입력", key="new_subtopic_empty")
            if st.button("➕ 소제목 추가", key="add_subtopic_empty"):
                if new_subtopic_name.strip():
                    chapter_data['subtopics'].append(new_subtopic_name)
                    chapter_data['subtopic_data'][new_subtopic_name] = {'questions': [], 'answers': [], 'content': ''}
                    st.rerun()
    
    # 전체 본문 보기
    st.markdown("---")
    st.markdown("### 📖 작성된 본문")
    pure_content = get_all_content_text()
    if pure_content:
        total_chars = calculate_char_count(pure_content)
        content_count = sum(1 for ch in st.session_state['chapters'].values() for st_data in ch.get('subtopic_data', {}).values() if st_data.get('content'))
        st.success(f"✅ 총 {content_count}개 소제목 | {total_chars:,}자")
        with st.expander("📖 전체 본문 펼쳐보기", expanded=False):
            for ch in st.session_state['outline']:
                if ch in st.session_state['chapters']:
                    ch_data = st.session_state['chapters'][ch]
                    if 'subtopic_data' in ch_data:
                        has_content = any(ch_data['subtopic_data'].get(s, {}).get('content') for s in ch_data.get('subtopics', []))
                        if has_content:
                            st.markdown(f"## {ch}")
                            for st_name in ch_data.get('subtopics', []):
                                st_data = ch_data['subtopic_data'].get(st_name, {})
                                if st_data.get('content'):
                                    st.markdown(f"**{st_name}**")
                                    st.markdown(clean_content_for_display(st_data['content'], st_name, ch))
                                    st.markdown("")
    else:
        st.info("💡 아직 작성된 본문이 없습니다.")


# === TAB 5: 문체 다듬기 ===
with tabs[4]:
    st.markdown("## 문체 다듬기 & 품질 검사")
    
    has_content = any(st_data.get('content') for ch_data in st.session_state['chapters'].values() for st_data in ch_data.get('subtopic_data', {}).values())
    if not has_content:
        st.info("💡 먼저 본문을 작성해주세요.")
        direct_content = st.text_area("다듬을 텍스트 직접 입력", height=300, placeholder="다듬고 싶은 텍스트를 여기에 붙여넣으세요...")
        if direct_content:
            has_content = True
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<p class="section-label">Style</p>', unsafe_allow_html=True)
        st.markdown("### 문체 다듬기")
        content_options = []
        for ch in st.session_state['outline']:
            if ch in st.session_state['chapters']:
                ch_data = st.session_state['chapters'][ch]
                if 'subtopic_data' in ch_data:
                    for st_name, st_data in ch_data['subtopic_data'].items():
                        if st_data.get('content'):
                            content_options.append(f"{ch} > {st_name}")
        if content_options:
            selected_content = st.selectbox("다듬을 콘텐츠 선택", content_options, key="refine_select")
        style = st.selectbox("목표 스타일", ["친근한", "전문적", "직설적", "스토리텔링"], key="style_select")
        
        if st.button("✨ 문체 다듬기", key="refine_btn"):
            content_to_refine = ""
            if content_options and 'selected_content' in dir() and selected_content:
                parts = selected_content.split(" > ")
                if len(parts) == 2:
                    ch, st_name = parts
                    content_to_refine = st.session_state['chapters'][ch]['subtopic_data'][st_name]['content']
            elif 'direct_content' in dir() and direct_content:
                content_to_refine = direct_content
            if content_to_refine:
                with st.spinner("다듬는 중..."):
                    refined = refine_content(content_to_refine, style)
                    st.session_state['refined_content'] = refined
            else:
                st.error("다듬을 콘텐츠를 선택해주세요.")
        
        if st.session_state.get('refined_content'):
            st.text_area("다듬어진 본문", value=st.session_state['refined_content'], height=400)
            if st.button("원본에 적용", key="apply_refined"):
                if content_options and 'selected_content' in dir() and selected_content:
                    parts = selected_content.split(" > ")
                    if len(parts) == 2:
                        ch, st_name = parts
                        st.session_state['chapters'][ch]['subtopic_data'][st_name]['content'] = st.session_state['refined_content']
                        trigger_auto_save()
                        st.success("적용됨!")
                        st.rerun()
    
    with col2:
        st.markdown('<p class="section-label">Quality</p>', unsafe_allow_html=True)
        st.markdown("### 품질 검사")
        if st.button("🔍 베스트셀러 체크", key="quality_btn"):
            content_to_check = ""
            if content_options and 'selected_content' in dir() and selected_content:
                parts = selected_content.split(" > ")
                if len(parts) == 2:
                    ch, st_name = parts
                    content_to_check = st.session_state['chapters'][ch]['subtopic_data'][st_name]['content']
            elif 'direct_content' in dir() and direct_content:
                content_to_check = direct_content
            if content_to_check:
                with st.spinner("분석 중..."):
                    quality_result = check_quality(content_to_check)
                    st.session_state['quality_result'] = quality_result
            else:
                st.error("검사할 콘텐츠를 선택해주세요.")
        if st.session_state.get('quality_result'):
            st.markdown(f'<div class="info-card">{st.session_state["quality_result"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)


# === TAB 6: 최종 출력 ===
with tabs[5]:
    st.markdown("## 최종 출력 & 마케팅")
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown('<p class="section-label">Export</p>', unsafe_allow_html=True)
        st.markdown("### 전자책 다운로드")
        book_title = st.text_input("전자책 제목", value=st.session_state.get('book_title', ''), key="final_title")
        subtitle = st.text_input("부제", value=st.session_state.get('subtitle', ''), key="final_subtitle")
        st.session_state['book_title'] = book_title
        st.session_state['subtitle'] = subtitle
        
        # 전체 책 내용 생성
        full_book_txt = ""
        full_book_html = ""
        if book_title:
            full_book_txt += f"{book_title}\n"
            full_book_html += f"<h1>{book_title}</h1>\n"
        if subtitle:
            full_book_txt += f"{subtitle}\n"
            full_book_html += f"<p style='color: #666;'>{subtitle}</p>\n"
        full_book_txt += "\n" + "="*50 + "\n\n"
        full_book_html += "<hr>\n"
        
        for chapter in st.session_state['outline']:
            if chapter in st.session_state['chapters']:
                ch_data = st.session_state['chapters'][chapter]
                if 'subtopic_data' in ch_data:
                    chapter_has_content = any(ch_data['subtopic_data'].get(st_name, {}).get('content') for st_name in ch_data.get('subtopics', []))
                    if chapter_has_content:
                        full_book_txt += f"\n{chapter}\n" + "-"*40 + "\n\n"
                        full_book_html += f"<h2>{chapter}</h2>\n"
                        for st_name in ch_data.get('subtopics', []):
                            st_data = ch_data['subtopic_data'].get(st_name, {})
                            if st_data.get('content'):
                                full_book_txt += f"\n{st_name}\n\n{st_data['content']}\n\n"
                                full_book_html += f"<h3>{st_name}</h3>\n"
                                for para in st_data['content'].split('\n\n'):
                                    if para.strip():
                                        full_book_html += f"<p>{para.strip()}</p>\n"
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{book_title or '전자책'}</title>
    <style>
        body {{ font-family: 'Pretendard', sans-serif; max-width: 800px; margin: 0 auto; padding: 40px 20px; line-height: 1.8; }}
        h1 {{ font-size: 32px; margin-bottom: 10px; }}
        h2 {{ font-size: 24px; margin-top: 50px; }}
        h3 {{ font-size: 18px; margin-top: 30px; }}
        p {{ font-size: 16px; margin: 16px 0; }}
    </style>
</head>
<body>{full_book_html}</body>
</html>"""
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("📄 TXT 다운로드", full_book_txt, file_name=f"{book_title or 'ebook'}_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain", use_container_width=True)
        with col_dl2:
            st.download_button("🌐 HTML 다운로드", html_content, file_name=f"{book_title or 'ebook'}_{datetime.now().strftime('%Y%m%d')}.html", mime="text/html", use_container_width=True)
        
        # RTF 다운로드
        rtf_content = "{\\rtf1\\ansi\\ansicpg949\\deff0\n{\\fonttbl{\\f0\\fnil 맑은 고딕;}}\n\\f0\\fs24\n"
        rtf_content += escape_rtf_unicode(book_title or '') + "\\par\n"
        rtf_content += escape_rtf_unicode(subtitle or '') + "\\par\\par\n"
        for chapter in st.session_state['outline']:
            if chapter in st.session_state['chapters']:
                ch_data = st.session_state['chapters'][chapter]
                if 'subtopic_data' in ch_data:
                    chapter_has_content = any(ch_data['subtopic_data'].get(st_name, {}).get('content') for st_name in ch_data.get('subtopics', []))
                    if chapter_has_content:
                        rtf_content += "\\par\\b " + escape_rtf_unicode(chapter) + "\\b0\\par\\par\n"
                        for st_name in ch_data.get('subtopics', []):
                            st_data = ch_data['subtopic_data'].get(st_name, {})
                            if st_data.get('content'):
                                rtf_content += "\\b " + escape_rtf_unicode(st_name) + "\\b0\\par\n"
                                rtf_content += escape_rtf_unicode(st_data['content']) + "\\par\\par\n"
        rtf_content += "}"
        st.download_button("📗 RTF 다운로드", rtf_content.encode('utf-8'), file_name=f"{book_title or 'ebook'}_{datetime.now().strftime('%Y%m%d')}.rtf", mime="application/rtf", use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📖 전체 본문")
        pure_content = get_all_content_text()
        if pure_content:
            total_chars = calculate_char_count(pure_content)
            content_count = sum(1 for ch in st.session_state['chapters'].values() for st_data in ch.get('subtopic_data', {}).values() if st_data.get('content'))
            st.success(f"✅ 총 {content_count}개 소제목 | {total_chars:,}자 | 약 {total_chars//500}페이지")
            with st.expander("📖 전체 본문 펼쳐보기", expanded=False):
                for ch in st.session_state['outline']:
                    if ch in st.session_state['chapters']:
                        ch_data = st.session_state['chapters'][ch]
                        if 'subtopic_data' in ch_data:
                            has_content = any(ch_data['subtopic_data'].get(s, {}).get('content') for s in ch_data.get('subtopics', []))
                            if has_content:
                                st.markdown(f"## {ch}")
                                for st_name in ch_data.get('subtopics', []):
                                    st_data = ch_data['subtopic_data'].get(st_name, {})
                                    if st_data.get('content'):
                                        st.markdown(f"**{st_name}**")
                                        st.markdown(clean_content_for_display(st_data['content'], st_name, ch))
        else:
            st.info("💡 아직 작성된 본문이 없습니다.")
    
    with col2:
        st.markdown('<p class="section-label">Marketing</p>', unsafe_allow_html=True)
        st.markdown("### 마케팅 카피")
        if st.button("카피 생성하기", key="marketing_btn"):
            with st.spinner("생성 중..."):
                marketing = generate_marketing_copy(st.session_state.get('book_title', st.session_state['topic']), st.session_state.get('subtitle', ''), st.session_state['topic'], st.session_state['target_persona'])
                st.session_state['marketing_copy'] = marketing
        if st.session_state.get('marketing_copy'):
            st.markdown(f'<div class="info-card">{st.session_state["marketing_copy"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)


# --- 자동 저장 처리 ---
if st.session_state.get('auto_save_trigger'):
    st.session_state['auto_save_trigger'] = False
    auto_save_data = get_auto_save_data()
    auto_save_json = json.dumps(auto_save_data, ensure_ascii=False, indent=2)
    file_name = st.session_state.get('book_title', '전자책') or '전자책'
    file_name = re.sub(r'[^\w\s가-힣-]', '', file_name)[:20]
    st.toast("💾 자동 저장됨!")

# --- 푸터 ---
st.markdown('<div class="premium-footer"><span class="premium-footer-text">전자책 작성 프로그램 — </span><span class="premium-footer-author">남현우 작가</span></div>', unsafe_allow_html=True)
