import streamlit as st
from streamlit_extras.colored_header import colored_header


def display_header():
    """페이지 상단의 헤더를 표시합니다."""
    colored_header(
        label="계획서 보고서 작성 AI",  # Title updated slightly
        description="PDF 서식 및 참고 파일을 업로드하고 지시사항을 입력하면 계획서 또는 보고서를 작성해줍니다.",
        color_name="blue-70",
    )


def display_file_uploaders():
    """PDF 파일 업로더 위젯들을 표시하고 업로드된 파일 객체들을 반환합니다."""
    uploaded_template = st.file_uploader(
        "PDF 서식 파일 업로드", type=["pdf"], key="template_uploader"
    )
    uploaded_reference = st.file_uploader(
        "참고 파일 PDF 업로드 (선택 사항)", type=["pdf"], key="reference_uploader"
    )
    return uploaded_template, uploaded_reference


def display_instructions_input():
    """사용자 지시사항 입력 영역 위젯을 표시하고 입력된 텍스트를 반환합니다."""
    instructions = st.text_area(
        "작성 지시사항 입력",
        placeholder="""예시:
- 이 PDF 템플릿을 사용하여 2025학년도 1-1-1 프로젝트 학습 계획 초안을 작성해주세요. 핵심 목표는 학생 중심 교육 강화입니다. 성취 기준은...
- [참고 파일 PDF] 제출된 교육 활동 계획서 PDF를 참고하여, 계획의 타당성을 분석하고, 개선점을 3가지 제안해주세요.
- 이 프로젝트 학습 계획서 템플릿을 사용하여, '기후 변화와 우리'라는 주제로 5학년 학생 대상의 프로젝트 학습 계획서를 작성해주세요. 탐구 단계를 구체적으로 작성해주세요.
""",
        height=200,
        key="instructions_input",
    )
    return instructions


def display_generate_button():
    """'보고서/계획서 생성' 버튼 위젯을 표시하고 클릭 여부를 반환합니다."""
    return st.button("보고서/계획서 생성", key="generate_button")


def display_results_area():
    """결과 표시를 위한 컨테이너와 빈 영역(placeholder)을 생성하고 반환합니다."""
    container = st.container()
    with container:
        results_placeholder = st.empty()
    return container, results_placeholder  # Return both container and placeholder


def update_results_stream(placeholder, current_text):
    """스트리밍 중인 텍스트를 결과 영역에 업데이트합니다."""
    placeholder.markdown(
        current_text + "▌", unsafe_allow_html=True
    )  # Add cursor effect


def display_final_result(placeholder, html_content):
    """최종 결과를 HTML 형식으로 결과 영역에 표시합니다."""
    placeholder.markdown(html_content, unsafe_allow_html=True)


def display_download_button(title, docx_data):
    """DOCX 다운로드 버튼을 표시합니다. 기존 컨테이너의 내용을 유지합니다."""
    # 새 컨테이너를 생성하여 다운로드 버튼만 표시
    download_container = st.container()
    with download_container:
        st.download_button(
            label="📄 DOCX로 다운로드",
            data=docx_data,
            file_name=f"{title}.docx",
            # mime="application/docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # 정확한 MIME 타입
            key="download_button",
        )


def display_error(message):
    """에러 메시지를 표시합니다."""
    st.error(message)


def display_warning(message):
    """경고 메시지를 표시합니다."""
    st.warning(message)


def display_spinner(message="처리 중..."):
    """스피너(로딩 표시) 컨텍스트를 반환합니다."""
    return st.spinner(message)


def display_faq():
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
            A.  현재는 **Markdown 형식**으로 결과를 출력합니다.  
            * **DOCX 다운로드**버튼으로 Word 문서(.docx)로 다운받을 수 있습니다.
        """
        )
