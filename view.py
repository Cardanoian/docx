import streamlit as st
from streamlit_extras.colored_header import colored_header


def display_header():
    """페이지 상단의 헤더를 표시합니다."""
    colored_header(
        label="계획서 보고서 작성 AI (MVC)",  # Title updated slightly
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


def display_download_button(container, docx_data, filename="generated_report.docx"):
    """DOCX 다운로드 버튼을 표시합니다. 기존 컨테이너의 내용을 유지합니다."""
    # 새 컨테이너를 생성하여 다운로드 버튼만 표시
    download_container = st.container()
    with download_container:
        st.download_button(
            label="📄 DOCX로 다운로드",
            data=docx_data,
            file_name=filename,
            mime="application/docx",
            # mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # 정확한 MIME 타입
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


def display_footer():
    return st.text("04.08.11.20")
