import os
import yaml
from jinja2 import Template
from typing import Optional, Dict, Any

class PromptTemplateManager:
    """
    Simple prompt template manager:
    - Loads YAML templates from prompts directory
    - Supports `inherits` (single-level) via '{{ super }}' placeholder
    - Renders templates with Jinja2 using variables dict
    - Supports provider/variant keys: 'providers/<provider>/<template>.yaml' or 'variants/<template>__<name>.yaml'
    """

    def __init__(self, prompts_dir: Optional[str] = None, prompt_dir: Optional[str] = None):
        """
        Initialize the PromptTemplateManager.

        Backwards-compatible parameters:
        - `prompts_dir`: preferred name used internally
        - `prompt_dir`: alias used elsewhere in the codebase/tests
        """
        # accept either `prompt_dir` (older callers/tests) or `prompts_dir`
        base = prompt_dir or prompts_dir
        self.base_dir = base or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "prompts")
        )
        self._templates = {}
        self._load_templates()
        self._resolve_inheritance()

    @property
    def templates(self):
        """Expose templates dict as `templates` for backwards compatibility."""
        return self._templates

    def _load_templates(self):
        for root, _, files in os.walk(self.base_dir):
            for fname in files:
                if not (fname.endswith(".yaml") or fname.endswith(".yml")):
                    continue
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, self.base_dir)
                key = rel.replace(os.sep, "/").rsplit(".", 1)[0]  
                with open(full, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    template = data.get("template", "")
                    inherits = data.get("inherits")
                    meta = {k: v for k, v in data.items() if k not in ("template", "inherits")}
                    self._templates[key] = {"template": template, "inherits": inherits, "meta": meta}

    def _resolve_inheritance(self):

        for key, info in list(self._templates.items()):
            parent = info.get("inherits")
            if parent:
                parent_info = self._templates.get(parent)
                if parent_info:
                    child_t = info["template"]
                    parent_t = parent_info["template"]
                    merged = child_t.replace("{{ super }}", parent_t)
                    self._templates[key]["template"] = merged

    def _find_template_key_candidates(self, name: str, provider: Optional[str], variant: Optional[str]):

        candidates = []
        if provider:
            candidates.append(f"providers/{provider}/{name}")
        if variant:
            candidates.append(f"variants/{name}__{variant}")
        candidates.append(name)
        candidates.append("base")
        return candidates

    def render(self, name: str, variables: Dict[str, Any], provider: Optional[str] = None, variant: Optional[str] = None) -> str:
        """
        Render the template for `name` with variables.
        `name` example: "intents/create_function" or "intents/create_function" -> to match key used in prompts folder
        """
        candidates = self._find_template_key_candidates(name, provider, variant)
        template_text = None
        for c in candidates:
            info = self._templates.get(c)
            if info and info.get("template"):
                template_text = info["template"]
                break

        if not template_text:
            raise FileNotFoundError(f"No prompt template found for keys: {candidates}")

        tpl = Template(template_text)
        return tpl.render(**variables)


    def render_for_intent(self, intent_key: str, variables: Dict[str, Any], provider: Optional[str] = None, variant: Optional[str] = None) -> str:

        candidates = [f"intents/{intent_key}", intent_key]
        for cand in candidates:
            try:
                return self.render(cand, variables, provider=provider, variant=variant)
            except FileNotFoundError:
                continue
        
        return self.render("base", variables, provider=provider, variant=variant)
