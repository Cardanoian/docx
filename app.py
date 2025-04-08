import markdown
import time  # For small delay in streaming view

# Import modules from the project
import model
import view


# --- UI 랜더링 ---
view.display_header()
uploaded_template_file, uploaded_reference_file = view.display_file_uploaders()
user_instructions = view.display_instructions_input()
generate_button_clicked = view.display_generate_button()
view.display_footer()

# --- 컨트롤러 로직 ---
if generate_button_clicked:
    # 새 결과 생성 시 이전 세션 값 초기화
    view.st.session_state.pop("last_result_md", None)
    view.st.session_state.pop("last_docx_data", None)

    # 1. 입력 유효성 검사
    if not uploaded_template_file:
        view.display_warning("PDF 서식 파일을 업로드하세요.")
    elif not user_instructions:
        view.display_warning("작성 지시사항을 입력하세요.")
    else:
        # 2. PDF 텍스트 추출
        template_text = model.extract_text_from_pdf(uploaded_template_file)
        reference_text = model.extract_text_from_pdf(
            uploaded_reference_file
        )  # Returns None if no file

        if not template_text:
            view.display_warning(
                "PDF 서식 파일에서 텍스트를 추출하지 못했습니다. 파일 내용을 확인해주세요."
            )
        else:
            # 3. 결과 영역 준비
            results_container, results_placeholder = view.display_results_area()

            # 4. 콘텐츠 생성 (스트리밍) 및 표시
            full_response_md = ""
            error_occurred = False
            try:
                with view.display_spinner("보고서/계획서 생성 중..."):
                    for chunk in model.generate_content_from_gemini(
                        template_text, reference_text, user_instructions
                    ):
                        full_response_md += chunk
                        view.update_results_stream(
                            results_placeholder, full_response_md
                        )
                        time.sleep(0.01)

                    if "오류 발생:" in full_response_md:
                        error_occurred = True

                # ✅ 결과 저장
                view.st.session_state["last_result_md"] = full_response_md

            except Exception as e:
                error_occurred = True
                view.display_error(f"콘텐츠 생성 중 심각한 오류 발생: {e}")
                full_response_md = f"오류: {e}"

            # 5. 최종 결과 처리 및 DOCX 생성/다운로드 버튼 표시
            if not error_occurred and full_response_md:
                final_html = markdown.markdown(
                    full_response_md, extensions=["tables", "fenced_code"]
                )
                view.display_final_result(results_placeholder, final_html)

                # docx_data = model.convert_html_to_docx(final_html)
                docx_data = model.markdown_to_docx(full_response_md)
                if docx_data:
                    # 결과는 유지하면서 다운로드 버튼 표시
                    view.st.session_state["last_docx_data"] = docx_data
                    view.display_download_button(results_container, docx_data)
                else:
                    view.display_warning("결과를 DOCX로 변환하는 데 실패했습니다.")

            # 결과 복원
            if (
                "last_result_md" in view.st.session_state
                and not generate_button_clicked
            ):
                prev_html = markdown.markdown(
                    view.st.session_state["last_result_md"],
                    extensions=["tables", "fenced_code"],
                )
                results_container, result_placeholder = view.display_results_area()
                view.display_final_result(result_placeholder, prev_html)

                if "last_docx_data" in view.st.session_state:
                    view.display_download_button(
                        results_container,
                        view.st.session_state["last_docx_data"],
                        key="download_button_restored",
                    )


# --- Footer or other UI elements can be added here via view functions ---
# Example:
# view.display_footer()
