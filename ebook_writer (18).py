# ==========================================
# 🔧 러시아어 문제 해결 패치
# ==========================================
# 
# 기존 app.py에서 ask_ai 함수를 찾아서 아래 코드로 교체하세요.
# 
# 위치: 약 450~470줄 근처 (def ask_ai 함수)
# ==========================================

# 1. 먼저 이 함수를 ask_ai 함수 위에 추가하세요:

def clean_unicode_control_chars(text):
    """Unicode 제어 문자 제거 (RTL/LTR 마커, 제로폭 문자 등) - 러시아어처럼 보이는 문제 방지"""
    if not text:
        return ""
    
    import re
    
    # Unicode 방향 제어 문자 제거
    unicode_control_chars = [
        '\u200e',  # LEFT-TO-RIGHT MARK
        '\u200f',  # RIGHT-TO-LEFT MARK
        '\u202a',  # LEFT-TO-RIGHT EMBEDDING
        '\u202b',  # RIGHT-TO-LEFT EMBEDDING
        '\u202c',  # POP DIRECTIONAL FORMATTING
        '\u202d',  # LEFT-TO-RIGHT OVERRIDE
        '\u202e',  # RIGHT-TO-LEFT OVERRIDE
        '\u2066',  # LEFT-TO-RIGHT ISOLATE
        '\u2067',  # RIGHT-TO-LEFT ISOLATE
        '\u2068',  # FIRST STRONG ISOLATE
        '\u2069',  # POP DIRECTIONAL ISOLATE
        '\u200b',  # ZERO WIDTH SPACE
        '\u200c',  # ZERO WIDTH NON-JOINER
        '\u200d',  # ZERO WIDTH JOINER
        '\ufeff',  # ZERO WIDTH NO-BREAK SPACE (BOM)
        '\u061c',  # ARABIC LETTER MARK
        '\u200a',  # HAIR SPACE
        '\u2009',  # THIN SPACE
        '\u2008',  # PUNCTUATION SPACE
        '\u2007',  # FIGURE SPACE
        '\u2006',  # SIX-PER-EM SPACE
        '\u2005',  # FOUR-PER-EM SPACE
        '\u2004',  # THREE-PER-EM SPACE
        '\u2003',  # EM SPACE
        '\u2002',  # EN SPACE
        '\u2001',  # EM QUAD
        '\u2000',  # EN QUAD
    ]
    for char in unicode_control_chars:
        text = text.replace(char, '')
    
    # 제어 문자 범위 제거 (U+0000 ~ U+001F, U+007F ~ U+009F)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    return text


# 2. 기존 ask_ai 함수를 이 함수로 교체하세요:

def ask_ai(system_role, prompt, temperature=0.7):
    api_key = get_api_key()
    if not api_key:
        return "⚠️ API 키를 먼저 입력해주세요."
    
    try:
        genai.configure(api_key=api_key)
        ai_model = genai.GenerativeModel('models/gemini-2.0-flash')
        generation_config = genai.types.GenerationConfig(temperature=temperature)
        
        # 🔧 핵심 수정: 한국어만 사용하도록 강조
        full_prompt = f"""당신은 {system_role}입니다.

{prompt}

중요: 반드시 한국어로만 답변해주세요. 러시아어, 아랍어, 히브리어 등 다른 언어를 절대 사용하지 마세요."""
        
        response = ai_model.generate_content(full_prompt, generation_config=generation_config)
        
        # 🔧 핵심 수정: Unicode 제어 문자 제거하여 반환
        return clean_unicode_control_chars(response.text)
    except Exception as e:
        return f"오류 발생: {str(e)}"


# ==========================================
# 적용 방법:
# ==========================================
# 
# 1. 기존 app.py 파일을 열기
# 2. "def ask_ai" 검색
# 3. 기존 ask_ai 함수 위에 clean_unicode_control_chars 함수 추가
# 4. 기존 ask_ai 함수를 위의 새 버전으로 교체
# 5. 저장 후 앱 재시작
# 
# ==========================================
