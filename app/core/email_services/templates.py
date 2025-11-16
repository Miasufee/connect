def build_verification_template(code: str, expires: int):
    html = f"""<html><body>
        <h3>Your Verification Code</h3>
        <div style='font-size:24px;font-weight:bold'>{code}</div>
        <p>This code expires in {expires} minutes.</p>
    </body></html>"""

    text = f"Your verification code is {code}. It expires in {expires} minutes."
    return html, text


def build_welcome_template(name: str):
    greeting = f"Hello {name}!" if name else "Hello!"
    html = f"<html><body><h2>Welcome!</h2><p>{greeting} Thanks for joining us!</p></body></html>"
    text = f"Welcome! {greeting} Thanks for joining us!"
    return html, text


def build_unique_id_template(unique_id: str):
    html = f"<html><body><h3>Your Unique ID</h3><p>{unique_id}</p></body></html>"
    text = f"Your Unique ID: {unique_id}"
    return html, text


def build_password_reset_template(reset_url: str, expires: int):
    html = f"<html><body><h3>Reset Password</h3><a href='{reset_url}'>Reset Password</a><p>Expires in {expires} minutes.</p></body></html>"
    text = f"Reset your password using this link: {reset_url} (expires in {expires} minutes)"
    return html, text


def build_password_changed_template():
    html = "<html><body><h3>Password Changed</h3><p>Your password has been updated successfully.</p></body></html>"
    text = "Your password has been updated successfully."
    return html, text
