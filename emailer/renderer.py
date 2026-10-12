"""Template rendering using Jinja2."""

import logging
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger(__name__)

DEFAULT_TEXT_TEMPLATE = """Hi {{ name | default('there', true) }},

Here is your unique problem statement:

--------------------------------------------------
{{ statement }}
--------------------------------------------------

Good luck and happy coding!
"""

DEFAULT_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1e293b; background-color: #f8fafc; margin: 0; padding: 24px; }
    .card { max-width: 580px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; padding: 32px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    h2 { color: #0f172a; margin-top: 0; }
    .statement-box { background: #f1f5f9; border-left: 4px solid #3b82f6; border-radius: 6px; padding: 18px 20px; font-size: 16px; font-weight: 500; color: #0f172a; margin: 24px 0; white-space: pre-wrap; }
    .footer { font-size: 13px; color: #64748b; margin-top: 24px; border-top: 1px solid #f1f5f9; padding-top: 16px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>Your Problem Statement</h2>
    <p>Hi <strong>{{ name | default('there', true) }}</strong>,</p>
    <p>You have been assigned the following unique challenge:</p>
    <div class="statement-box">{{ statement }}</div>
    <div class="footer">
      This is an automated delivery. Best of luck with your problem solving!
    </div>
  </div>
</body>
</html>
"""


class TemplateRenderer:
    """Renders text and HTML templates using Jinja2."""

    def __init__(self, text_template_path: Optional[Path] = None, html_template_path: Optional[Path] = None):
        self.text_template = self._load_template(text_template_path, DEFAULT_TEXT_TEMPLATE)
        self.html_template = self._load_template(html_template_path, DEFAULT_HTML_TEMPLATE) if html_template_path else None

    def _load_template(self, path: Optional[Path], default_source: str) -> Template:
        if path and Path(path).exists():
            try:
                env = Environment(loader=FileSystemLoader(str(Path(path).parent)), autoescape=True)
                return env.get_template(Path(path).name)
            except Exception as e:
                logger.warning("Could not load template from %s (%s). Using built-in default.", path, e)
        return Environment(autoescape=True).from_string(default_source)

    def render_text(self, name: str, statement: str) -> str:
        """Render plaintext template."""
        return self.text_template.render(name=name, statement=statement)

    def render_html(self, name: str, statement: str) -> Optional[str]:
        """Render HTML template if configured."""
        if self.html_template:
            return self.html_template.render(name=name, statement=statement)
        return None
