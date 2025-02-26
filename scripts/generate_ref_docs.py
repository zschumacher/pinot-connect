import pathlib
from typing import TextIO

import docspec
from docspec import Module
from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.smart import GoogleProcessor
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Context
from pydoc_markdown.util.docspec import is_method
from yaml import safe_load

CONFIG_FILE = pathlib.Path(__file__).parent.parent / "pydoc_markdown.yml"


def load_module_config() -> dict[str, str]:
    file = CONFIG_FILE.open()
    return safe_load(file)["modules"]


class CustomMarkdownRenderer(MarkdownRenderer):
    def _render_header(self, fp: TextIO, level: int, obj: docspec.ApiObject):
        """Not a good override point, so had to copy some code here.

        We are only changing the header writing functionality to make the docs a little prettier
        """
        if self.render_module_header_template and isinstance(obj, docspec.Module):
            fp.write(
                self.render_module_header_template.format(
                    module_name=obj.name, relative_module_name=obj.name.rsplit(".", 1)[-1]
                )
            )
            return

        object_id = self._resolver.generate_object_id(obj)
        if self.use_fixed_header_levels:
            header_levels = {
                **type(self).__dataclass_fields__["header_level_by_type"].default_factory(),  # type: ignore
                **self.header_level_by_type,
            }
            # Backwards compat for when we used "Data" instead of "Variable" which mirrors the docspec API
            header_levels["Variable"] = header_levels.get("Data", header_levels["Variable"])

            type_name = "Method" if self._is_method(obj) else type(obj).__name__
            level = header_levels.get(type_name, level)
        if self.insert_header_anchors and not self.html_headers:
            fp.write('<a id="{}"></a>\n\n'.format(object_id))
        if self.html_headers:
            header_template = '<h{0} id="{1}">{{title}}</h{0}>'.format(level, object_id)
        else:
            header_template = level * "#" + " {title}"
            # only line we changed is here, to allow nicer formatting of generated markdown
            if (
                (isinstance(obj, docspec.Function) and not is_method(obj))  # don't want class methods sectioned off
                or isinstance(obj, docspec.Class)
                or isinstance(obj, docspec.Variable)
            ):
                header_template = "---\n" + header_template

        if self.render_novella_anchors:
            fp.write(f"@anchor pydoc:" + ".".join(x.name for x in obj.path) + "\n")
        fp.write(header_template.format(title=self._get_title(obj)))
        fp.write("\n\n")


def build_config(modules: dict[str, str]) -> PydocMarkdown:
    context = Context(directory=str(pathlib.Path(__file__).parent))
    config = PydocMarkdown(
        renderer=CustomMarkdownRenderer(descriptive_class_title=False),
        processors=[FilterProcessor(), GoogleProcessor(), CrossrefProcessor()],
        loaders=[PythonLoader(modules=list(modules))],
    )
    config.init(context)
    return config


def parse_modules(config: PydocMarkdown) -> list[Module]:
    modules = config.load_modules()
    config.process(modules)
    return modules


def write_to_file(modules: dict[str, str], config: PydocMarkdown, module: Module):
    path = pathlib.Path(modules[module.name])
    print(f"Writing docs for {module.name} to {path}...")

    s = config.renderer.render_to_string([module])  # type: ignore
    path.write_text(s)


if __name__ == "__main__":
    modules_ = load_module_config()
    config_ = build_config(modules_)
    for module_ in parse_modules(config_):
        write_to_file(modules_, config_, module_)
