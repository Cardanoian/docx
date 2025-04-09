from controller import click_generate_btn
from view import (
    display_header,
    display_file_uploaders,
    display_instructions_input,
    display_generate_button,
    display_faq,
)


# --- UI 랜더링 ---
display_header()
uploaded_template_file, uploaded_reference_file = display_file_uploaders()
user_instructions = display_instructions_input()
generate_button_clicked = display_generate_button()
display_faq()

click_generate_btn(
    (
        uploaded_template_file,
        uploaded_reference_file,
        user_instructions,
        generate_button_clicked,
    )
)
