import os
import time
import streamlit as st
from PIL import (
    Image,
)  # Pillow is imported but not used, let's keep it for potential future image features
import google.generativeai as genai
from streamlit_extras.colored_header import colored_header
import markdown
import PyPDF2  # PDF 처리 라이브러리
from dotenv import load_dotenv

load_dotenv()
# Google Gemini API 키 설정
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 모델 설정
generation_config = {
    "temperature": 0.7,  # 보고서/계획서 톤에 맞춰 temperature 낮춤
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 10000,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",  # 필요에 따라 모델 변경
    generation_config=generation_config,
)


# PDF 텍스트 추출 함수 (기존 함수 재활용)
def extract_text_from_pdf(uploaded_pdf_file):
    """PDF 파일에서 텍스트를 추출합니다."""
    text = ""
    if uploaded_pdf_file is not None:  # 파일이 업로드되었는지 확인
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf_file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        except Exception as e:
            st.error(f"PDF 파일 처리 오류: {e}")
            return None
    return text


def generate_report_or_plan(pdf_template_text, reference_pdf_text, user_instructions):
    """
    PDF 템플릿, 참고 PDF, 사용자 지시사항을 기반으로 보고서 또는 계획서를 생성합니다.
    """
    full_text = ""
    try:
        prompt_text = f"""
        # 계획서 또는 보고서 작성

        ## PDF 서식 파일 내용:
        ```
        {pdf_template_text}
        ```

        """
        if reference_pdf_text:  # 참고 파일 내용이 있을 경우에만 추가
            prompt_text += f"""
        ## 참고 파일 PDF 내용:
        ```
        {reference_pdf_text}
        ```
            """

        prompt_text += f"""
        ## 사용자 지시사항:
        {user_instructions}

        ---

        **지시사항에 따라 PDF 템플릿{", 참고 PDF" if reference_pdf_text else ""}를 분석하고, 내용을 채워 계획서 또는 보고서를 작성하세요.**
        **한국어로 작성하며, 명확하고 논리적인 구조로 작성해주세요.**
        **템플릿 양식에 맞춰 내용을 작성하고, 필요하다면 추가적인 정보나 내용을 생성해도 좋습니다.**
        **만약 템플릿 내용이 부족하거나 지시사항을 수행하기 어렵다면, 솔직하게 답변해주세요.**
        **학교 사업 계획서, 교육 활동 계획서, 프로젝트 학습 계획서 등 교육 관련 계획서 및 보고서 작성에 특화되어 있습니다.**
        """

        response = model.generate_content([prompt_text])
        for chunk in response.text:
            full_text += chunk
            time.sleep(0.01)
            st.session_state.generated_result += chunk
            output_area.markdown(
                st.session_state.generated_result, unsafe_allow_html=True
            )
    except Exception as e:
        st.error(f"보고서/계획서 생성 중 오류 발생: {str(e)}")
    return full_text


# Streamlit 인터페이스 설정
colored_header(
    label="계획서 보고서 작성 AI",
    description="PDF 서식 및 참고 파일을 업로드하고 지시사항을 입력하면 계획서 또는 보고서를 작성해줍니다.",
    color_name="blue-70",
)

# 파일 업로드 버튼 (PDF 파일만 허용)
uploaded_pdf_template_file = st.file_uploader("PDF 서식 파일 업로드", type=["pdf"])
uploaded_reference_pdf_file = st.file_uploader(
    "참고 파일 PDF 업로드 (선택 사항)", type=["pdf"]
)  # 참고 파일 업로드 추가

# 지시사항 입력 텍스트 영역 추가 (placeholder, height 조정)
user_instructions = st.text_area(
    "작성 지시사항 입력",
    placeholder="""예시:
- 이 PDF 템플릿을 사용하여 2025학년도 1-1-1 프로젝트 학습 계획 초안을 작성해주세요. 핵심 목표는 학생 중심 교육 강화입니다. 성취 기준은...
- [참고 파일 PDF] 제출된 교육 활동 계획서 PDF를 참고하여, 계획의 타당성을 분석하고, 개선점을 3가지 제안해주세요.
- 이 프로젝트 학습 계획서 템플릿을 사용하여, '기후 변화와 우리'라는 주제로 5학년 학생 대상의 프로젝트 학습 계획서를 작성해주세요. 탐구 단계를 구체적으로 작성해주세요.
""",
    height=200,  # 높이 조정
)

generate_button = st.button("보고서/계획서 생성")

output_area = st.empty()

if generate_button and uploaded_pdf_template_file and user_instructions:
    try:
        pdf_template_text = extract_text_from_pdf(uploaded_pdf_template_file)
        reference_pdf_text = extract_text_from_pdf(
            uploaded_reference_pdf_file
        )  # 참고 파일 텍스트 추출

        if pdf_template_text:
            st.session_state.generated_result = ""
            with st.spinner("보고서/계획서 생성 중..."):  # 로딩 스피너 추가
                result = generate_report_or_plan(
                    pdf_template_text, reference_pdf_text, user_instructions
                )  # 참고 파일 텍스트 추가

            html_text = markdown.markdown(result, extensions=["tables"])
            output_area.markdown(html_text, unsafe_allow_html=True)
            print(html_text)

        else:
            st.warning(
                "PDF 서식 파일에서 텍스트를 추출하는데 실패했습니다. 파일 형식을 확인해주세요."
            )

    except Exception as e:
        st.error(f"보고서/계획서 생성 중 오류 발생: {str(e)}")

elif generate_button and not uploaded_pdf_template_file:
    st.warning("PDF 서식 파일을 업로드하세요.")
elif generate_button and not user_instructions:
    st.warning("작성 지시사항을 입력하세요.")


# FAQ (계획서 보고서 작성에 맞게 수정)
with st.expander("❓ 계획서 보고서 작성 AI FAQ"):
    st.write(
        """
        **Q1. 계획서 보고서 작성 AI는 어떤 기능을 제공하나요?**

        A. 이 앱은 학교에서 필요한 다양한 **계획서 및 보고서** 작성을 돕기 위해 개발된 AI 도구입니다. PDF 서식 파일, **참고 파일 PDF (선택 사항)**, 그리고 작성 지시사항을 입력하면, AI가 서식에 맞춰 계획서 또는 보고서 초안을 생성합니다.  사업 계획서, 교육 활동 계획서, 프로젝트 학습 계획서, 각종 보고서 등 다양한 문서 작성을 지원합니다.  생성된 초안은 필요에 따라 수정 및 보완하여 완성할 수 있습니다.

        **Q2. 어떤 종류의 계획서 및 보고서 작성을 지원하나요?**

        A.  주로 학교 현장에서 사용되는 계획서 및 보고서 작성을 지원합니다. 예시는 다음과 같습니다:
        * **사업 계획서:** 학교 발전 계획, 특정 사업 운영 계획 등
        * **교육 활동 계획서:**  수업 계획, 방과후학교 운영 계획, 창의적 체험활동 계획 등
        * **프로젝트 학습 계획서:**  학생 주도 프로젝트 학습 운영 계획
        * **각종 보고서:**  활동 결과 보고서, 사업 결과 보고서, 평가 보고서 등
        * (향후 지원 확대 예정)

        **Q3. PDF 서식 파일은 어떻게 활용하나요?**

        A.  **PDF 서식 파일은 계획서 또는 보고서의 템플릿 역할**을 합니다.  기존에 사용하던 서식 파일(.pdf)을 업로드하면, AI가 해당 서식에 맞춰 내용을 채워줍니다.  별도의 서식 파일 없이 백지 상태에서 내용을 생성하고 싶다면, 비어있는 PDF 파일을 업로드하거나, 지시사항에 '자유 형식으로 작성해줘' 와 같이 요청할 수 있습니다.

        **Q3-1. 참고 파일 PDF는 어떻게 활용하나요?**

        A. **참고 파일 PDF는 AI가 보고서/계획서를 작성할 때 참고할 추가 정보**를 제공합니다.  예를 들어, '참고 파일 PDF를 바탕으로 ~를 분석해주세요' 와 같은 지시사항과 함께 참고 PDF를 업로드하면, AI가 해당 PDF 내용을 분석하여 보고서/계획서 작성에 활용합니다.  **참고 파일 PDF는 선택 사항**이며, 필수가 아닙니다.

        **Q4.  작성 지시사항은 어떻게 입력해야 하나요?**

        A.  **구체적이고 명확하게 지시사항을 입력**할수록 AI가 더 정확하게 이해하고 원하는 결과물을 생성할 수 있습니다.  다음과 같은 내용을 포함하여 지시사항을 작성해보세요:
        * **작성할 문서의 종류:** (예: 2025학년도 각종 사업 계획서, OOO 프로젝트 보고서,  OOO 교육 활동 계획서 초안)
        * **주요 내용 및 핵심 목표:** (예:  학생 중심 교육 강화,  창의적 체험활동 활성화,  OOO 사업 성과 분석)
        * **참고 자료:** (**참고 파일 PDF** 외에 추가적으로 참고할 내용이 있다면 간략하게 언급, **참고 파일 PDF 활용 지시 포함**)
        * **특정 양식 요청:** (예:  표 형식으로 작성,  핵심 내용만 요약,  자유 형식으로 작성)
        * **분량:** (예:  A4 2장 내외로 요약)

        **Q5. 계획서/보고서 생성 후 수정은 어떻게 하나요?**

        A. 계획서/보고서 생성 후, 하단 출력 내용을 확인하고, 필요한 경우 **텍스트를 선택하여 복사**한 후, 워드프로세서(MS Word, 한글 등)에 붙여넣어 수정할 수 있습니다.  향후 챗봇 기능을 추가하여 앱 내에서 직접 수정하고 추가적인 요청을 할 수 있도록 개선할 예정입니다.

        **Q6.  PDF 파일 텍스트 추출 오류가 발생할 경우 어떻게 해야 하나요?**

        A.  PDF 파일이 이미지 형태로 스캔된 경우, 텍스트 추출이 제대로 이루어지지 않을 수 있습니다.  가능하다면 **텍스트 기반 PDF 파일**을 사용하거나, OCR (광학 문자 인식) 기능을 활용하여 텍스트를 추출한 후 다시 시도해보세요.  향후 OCR 기능 내장 또는 PDF 텍스트 추출 성능 향상을 위해 지속적으로 개선할 예정입니다.

        **Q7.  지원하는 출력 형식은 무엇인가요?**

        A.  현재는 **Markdown 형식**으로 결과를 출력합니다.  향후 **Word 문서(.docx) 다운로드** 기능을 추가하여 사용 편의성을 높일 계획입니다.  PDF 다운로드 기능은 추후 검토하겠습니다.
    """
    )
