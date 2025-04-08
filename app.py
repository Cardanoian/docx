import markdown
import time  # For small delay in streaming view

# Import modules from the project
import model
import view

# --- 초기 설정 ---
# Load environment variables (though model might load it too, ensures it's done early)
# utils.load_environment_variables()

# --- UI 랜더링 ---
view.display_header()
uploaded_template_file, uploaded_reference_file = view.display_file_uploaders()
user_instructions = view.display_instructions_input()
generate_button_clicked = view.display_generate_button()

# --- 컨트롤러 로직 ---
if generate_button_clicked:
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
            full_response_md = ""  # Initialize empty string for full response
            error_occurred = False
            try:
                with view.display_spinner("보고서/계획서 생성 중..."):
                    # model.generate_content_from_gemini yields chunks
                    for chunk in model.generate_content_from_gemini(
                        template_text, reference_text, user_instructions
                    ):
                        full_response_md += chunk
                        # Update the view incrementally
                        view.update_results_stream(
                            results_placeholder, full_response_md
                        )
                        time.sleep(0.01)  # Small delay for smoother UI update

                    # Check if the response generation itself indicated an error
                    if "오류 발생:" in full_response_md:
                        error_occurred = True

            except Exception as e:
                error_occurred = True
                view.display_error(f"콘텐츠 생성 중 심각한 오류 발생: {e}")
                full_response_md = f"오류: {e}"  # Ensure some error info is available

            # 5. 최종 결과 처리 및 DOCX 생성/다운로드 버튼 표시
            if not error_occurred and full_response_md:
                # Convert final Markdown to HTML
                final_html = markdown.markdown(
                    full_response_md, extensions=["tables", "fenced_code"]
                )

                # Display the final formatted result (replacing the streaming version)
                view.display_final_result(results_placeholder, final_html)

                # Convert to DOCX
                docx_data = model.convert_html_to_docx(final_html)

                if docx_data:
                    # 결과는 유지하면서 다운로드 버튼 표시 (별도 컨테이너에)
                    view.display_download_button(results_container, docx_data)
                else:
                    # Display warning if DOCX conversion failed
                    view.display_warning("결과를 DOCX로 변환하는 데 실패했습니다.")
            elif error_occurred:
                # Display the error message permanently if generation failed
                view.display_final_result(results_placeholder, full_response_md)


# --- Footer or other UI elements can be added here via view functions ---
# Example:
# view.display_footer()
