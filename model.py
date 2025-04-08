import os
import google.generativeai as genai
import PyPDF2
import utils  # utils.py import
import io
import platform
from docx import Document
from docx.shared import Pt
from bs4 import BeautifulSoup
import html2docx

# --- Initialization ---
utils.load_environment_variables()  # Load env vars first
API_KEY = utils.get_api_key()

if not API_KEY:
    raise ValueError("GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")

genai.configure(api_key=API_KEY)

# --- Configuration ---
GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 10000,
    "response_mime_type": "text/plain",
}

# --- Model Instantiation ---
# Using a recommended model, adjust if needed
llm_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",  # or "gemini-pro" if preferred
    generation_config=GENERATION_CONFIG,
)


def get_system_font():
    system = platform.system()
    if system == "Darwin":  # macOS
        return "AppleGothic"
    elif system == "Linux":
        return "NanumGothic"
    elif system == "Windows":
        return "Malgun Gothic"
    else:
        return "Arial"  # 기본 폰트


SYSTEM_FONT = get_system_font()

# --- Font Path Setup ---
# model.py 파일이 위치한 디렉토리를 기준으로 fonts 폴더 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_ROOT = os.path.join(BASE_DIR, "fonts")
# 사용할 폰트 파일 이름 (fonts 폴더 안에 있는 실제 파일 이름과 일치해야 함)
FONT_FILENAME = "NanumGothic.ttf"
FONT_PATH = os.path.join(FONT_ROOT, FONT_FILENAME)


# --- Resource Fetching Callback ---
def fetch_resources(uri, rel):
    """
    xhtml2pdf가 로컬 리소스(폰트 등)를 찾을 수 있도록 경로를 변환하는 콜백 함수.
    uri: CSS 등에서 참조하는 경로 (예: 'fonts/NanumGothicRegular.ttf')
    """
    # CSS의 url() 경로를 실제 파일 시스템 경로로 변환
    # 여기서는 CSS의 경로가 'fonts/...' 형태라고 가정
    if uri.startswith("fonts/"):
        path = os.path.join(FONT_ROOT, uri[len("fonts/") :])
    else:
        # 다른 종류의 로컬 리소스 경로 처리가 필요하면 여기에 추가
        # 기본적인 처리: BASE_DIR 기준으로 경로 해석 시도
        path = os.path.join(BASE_DIR, uri)

    path = os.path.normpath(path)
    print(f"Fetching resource: URI='{uri}', Mapped Path='{path}'")  # 디버깅용 출력
    # 파일 존재 여부 확인 (선택적이지만 권장)
    if not os.path.isfile(path):
        print(f"Error: Resource file not found at {path}")
        # 파일을 찾지 못했을 때의 처리 (예: 에러 발생 또는 None 반환)
        # 여기서는 일단 경로를 반환하되, 오류는 pisa 내부에서 처리될 수 있음
        # raise FileNotFoundError(f"Resource not found: {path}") # 필요시 에러 발생
    return path


# --- Core Logic Functions ---
def extract_text_from_pdf(uploaded_pdf_file):
    """PDF 파일 객체에서 텍스트를 추출합니다."""
    text = ""
    if uploaded_pdf_file is None:
        return None
    try:
        # Reset buffer position for reading
        uploaded_pdf_file.seek(0)
        pdf_reader = PyPDF2.PdfReader(uploaded_pdf_file)
        for page in pdf_reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            except Exception:
                # Log or handle page-specific extraction errors if needed
                continue  # Continue to next page even if one fails
        return text if text else None  # Return None if no text extracted
    except Exception as e:
        print(f"PDF 텍스트 추출 오류: {e}")  # Log error
        return None  # Return None on error


def generate_content_from_gemini(template_text, reference_text, instructions):
    """Gemini 모델을 사용하여 콘텐츠 생성을 스트리밍 방식으로 처리합니다."""
    prompt_text = f"""
# 계획서 또는 보고서 작성

## PDF 서식 파일 내용:
{template_text}

"""
    if reference_text:
        prompt_text += f"""
## 참고 파일 PDF 내용:
{reference_text}

"""

    prompt_text += f"""
## 사용자 지시사항:
{instructions}

---

**지시사항에 따라 PDF 템플릿{", 참고 PDF" if reference_text else ""}를 분석하고, 내용을 채워 계획서 또는 보고서를 작성하세요.**
**한국어로 작성하며, 명확하고 논리적인 구조로 작성해주세요.**
**템플릿 양식에 맞춰 내용을 작성하고, 필요하다면 추가적인 정보나 내용을 생성해도 좋습니다.**
**만약 템플릿 내용이 부족하거나 지시사항을 수행하기 어렵다면, 솔직하게 답변해주세요.**
**학교 사업 계획서, 교육 활동 계획서, 프로젝트 학습 계획서 등 교육 관련 계획서 및 보고서 작성에 특화되어 있습니다.**
**표(테이블)가 필요한 경우 마크다운 테이블 형식으로 생성해주세요.**
"""
    try:
        # stream=True로 설정하여 응답을 청크 단위로 받음
        response_stream = llm_model.generate_content([prompt_text], stream=True)
        for chunk in response_stream:
            # Check if the chunk has text content and it's not empty
            if hasattr(chunk, "text") and chunk.text:
                yield chunk.text  # 각 텍스트 청크를 반환 (yield)
    except Exception as e:
        print(f"Gemini API 호출 오류: {e}")  # Log error
        yield f"\n\n오류 발생: 콘텐츠 생성 중 문제가 발생했습니다. ({e})"  # Yield error message


def convert_html_to_docx(html_content):
    """HTML 내용을 docx 파일로 변환합니다."""

    try:
        # HTML2DOCX 라이브러리 사용
        buffer = io.BytesIO()
        buffer = html2docx(html_content)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"HTML2DOCX 변환 오류: {e}")

        try:
            # 대안: BeautifulSoup을 사용한 수동 변환
            soup = BeautifulSoup(html_content, "html.parser")
            doc = Document()

            # 기본 폰트 설정
            style = doc.styles["Normal"]
            font = style.font
            # 운영체제에 맞는 폰트 사용
            font.name = SYSTEM_FONT
            font.size = Pt(11)

            # 텍스트 추출 및 문서에 추가
            for p in soup.find_all("p"):
                paragraph = doc.add_paragraph(p.get_text())
                # 각 단락에도 폰트 적용
                for run in paragraph.runs:
                    run.font.name = SYSTEM_FONT

            # 테이블 추가
            for table in soup.find_all("table"):
                rows = table.find_all("tr")
                if rows:
                    t = doc.add_table(
                        rows=len(rows), cols=len(rows[0].find_all(["td", "th"]))
                    )
                    t.style = "Table Grid"

                    for i, row in enumerate(rows):
                        cells = row.find_all(["td", "th"])
                        for j, cell in enumerate(cells):
                            if j < len(t.rows[i].cells):  # 인덱스 범위 확인
                                t.rows[i].cells[j].text = cell.get_text().strip()
                                # 테이블 셀에도 폰트 적용
                                for paragraph in t.rows[i].cells[j].paragraphs:
                                    for run in paragraph.runs:
                                        run.font.name = SYSTEM_FONT

            # 결과 저장
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            return buffer
        except Exception as e:
            print(f"수동 DOCX 변환 오류: {e}")
            return None
