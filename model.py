import os
import google.generativeai as genai
import PyPDF2
import io
import platform
from docx import Document
from docx.shared import Pt
from bs4 import BeautifulSoup

from utils import get_api_key

# --- Initialization ---
API_KEY = get_api_key()

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


# --- Font Path Setup ---
# 운영체제별 한글 폰트 설정
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

# model.py 파일이 위치한 디렉토리를 기준으로 fonts 폴더 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_ROOT = os.path.join(BASE_DIR, "fonts")


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
        # BeautifulSoup을 사용하여 HTML 파싱
        soup = BeautifulSoup(html_content, "html.parser")
        doc = Document()

        # 기본 폰트 설정 (문서 전체에 적용)
        style = doc.styles["Normal"]
        font = style.font
        font.name = SYSTEM_FONT  # 운영체제에 맞는 폰트 사용
        font.size = Pt(11)

        # 제목 추출 (있는 경우)
        title = soup.find("h1")
        if title:
            doc.add_heading(title.get_text(), level=1)

        # 모든 요소 처리
        for element in soup.body.children:
            if element.name == "p":
                # 단락 추가
                text = element.get_text()
                if text.strip():  # 빈 텍스트가 아닌 경우에만 처리
                    p = doc.add_paragraph()
                    # 텍스트가 볼드인지 확인
                    if element.find("strong"):
                        run = p.add_run(text)
                        run.bold = True
                    else:
                        p.add_run(text)

            elif element.name == "h1":
                # 이미 처리했으므로 스킵
                continue

            elif element.name == "h2":
                doc.add_heading(element.get_text(), level=2)

            elif element.name == "h3":
                doc.add_heading(element.get_text(), level=3)

            elif element.name == "ul":
                # 불렛 리스트 처리
                for li in element.find_all("li"):
                    p = doc.add_paragraph(li.get_text(), style="List Bullet")
                    # 리스트에도 폰트 적용
                    for run in p.runs:
                        run.font.name = SYSTEM_FONT

            elif element.name == "ol":
                # 번호 리스트 처리
                for li in element.find_all("li"):
                    p = doc.add_paragraph(li.get_text(), style="List Number")
                    for run in p.runs:
                        run.font.name = SYSTEM_FONT

            elif element.name == "table":
                # 테이블 처리
                rows = element.find_all("tr")
                if rows:
                    num_cols = max(len(row.find_all(["td", "th"])) for row in rows)
                    table = doc.add_table(rows=len(rows), cols=num_cols)
                    table.style = "Table Grid"

                    for i, row in enumerate(rows):
                        cells = row.find_all(["td", "th"])
                        for j, cell in enumerate(cells):
                            if j < num_cols:  # 인덱스 범위 확인
                                cell_text = cell.get_text(separator=" ", strip=True)
                                table.cell(i, j).text = cell_text
                                # 폰트 스타일 적용
                                for paragraph in table.cell(i, j).paragraphs:
                                    for run in paragraph.runs:
                                        run.font.name = SYSTEM_FONT
                                # <th>인 경우 굵게
                                if cell.name == "th":
                                    for paragraph in table.cell(i, j).paragraphs:
                                        for run in paragraph.runs:
                                            run.bold = True

        # 결과 저장
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"DOCX 변환 오류: {e}")

        # 긴급 폴백: 간단한 텍스트만 추출해서 문서 생성
        try:
            doc = Document()
            style = doc.styles["Normal"]
            font = style.font
            font.name = SYSTEM_FONT
            font.size = Pt(11)

            # HTML 태그 제거 후 텍스트만 추출
            text_content = soup.get_text()
            paragraphs = text_content.split("\n")

            for para in paragraphs:
                if para.strip():  # 빈 줄 제외
                    p = doc.add_paragraph(para.strip())
                    for run in p.runs:
                        run.font.name = SYSTEM_FONT

            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            return buffer

        except Exception as e2:
            print(f"긴급 폴백 DOCX 변환도 실패: {e2}")
            return None
