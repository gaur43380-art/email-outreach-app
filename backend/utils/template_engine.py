# backend/utils/template_engine.py

def render_template(template: str, context: dict) -> str:
    """
    Replace placeholders in email templates.

    template: Email template string
    context: Dictionary containing values
    Example:
        {
          "Name": "Ankit",
          "Company": "Google",
          "MyName": "Gaurav"
        }
    """

    if not template or not context:
        return template

    rendered = template

    for key, value in context.items():
        placeholder = "{" + str(key) + "}"
        rendered = rendered.replace(placeholder, str(value))

    return rendered
