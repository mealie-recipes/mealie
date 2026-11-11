from mealie.services.email.email_service import EmailService, EmailTemplate


def test_email_template_escapes_values():
    template = EmailTemplate(
        subject="subject",
        header_text="<b>header</b>",
        message_top="<img src=x onerror=alert(1)>",
        message_bottom="bottom",
        button_link='https://example.com/reset?token=a&next="x"',
        button_text="Reset",
    )

    html = template.render_html(EmailService().default_template)

    assert "<b>header</b>" not in html
    assert "&lt;b&gt;header&lt;/b&gt;" in html
    assert "<img src=x" not in html
    assert 'href="https://example.com/reset?token=a&amp;next=&#34;x&#34;"' in html
