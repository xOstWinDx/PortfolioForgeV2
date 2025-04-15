# descriptions.py
from src.config import policy

AUTH_HEADER_NOTE = (
    "<ul>"
    "<li>Передайте заголовок <code>Authorization: Bearer &lt;token&gt;</code></li>"
    "</ul>"
)

REFRESH_COOKIE_NOTE = (
    "<p><strong>🔁 Требуется refresh-токен</strong></p>"
    "<ul>"
    "<li>Передайте <code>refresh_token</code> в Cookie</li>"
    "</ul>"
)

RETURN_TOKENS = (
    "<p><strong>📦 Возвращает:</strong></p>"
    "<ul>"
    "<li><code>access_token</code> в теле ответа</li>"
    "<li><code>refresh_token</code> в Cookie</li>"
    "</ul>"
)

CACHE_NOTE = "<p><em>🕒 Ответ кешируется на 3 минуты</em></p>"

# Парольные требования красиво в список
_password_req = "".join(
    f"<li><strong>{repr(e).replace('(', ' - ').replace(')', '')}</strong></li>"
    for e in policy._tests
)
PASSWORD_REQUIRED = f"<ul>{_password_req}</ul>"
