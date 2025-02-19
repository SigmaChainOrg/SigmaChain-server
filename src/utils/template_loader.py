from jinja2 import Template


def load_html_template(template_path: str, **kwargs):
    with open(template_path, "r", encoding="utf-8") as file:
        template = Template(file.read())
    return template.render(**kwargs)
