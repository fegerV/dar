from typing import Any

from app.models.template import Scene, TemplateVersion
from app.schemas.brief import CreativeBriefRead


class PromptCompiler:
    def compile(self, template_version: TemplateVersion, brief: CreativeBriefRead, scene: Scene | None = None) -> str:
        sections: list[str] = []
        sections.append("SYSTEM:\n" + self._resolve(template_version.prompt_config.get("system_prompt", "")))
        sections.append("CHARACTER:\n" + self._character_block(brief))
        sections.append("PERSONALITY:\n" + ", ".join(brief.personality or []))
        if brief.interests:
            sections.append("INTERESTS:\n" + ", ".join(brief.interests))
        if scene:
            sections.append("SCENE:\n" + self._resolve(scene.scene_config.get("prompt", scene.title)))
        sections.append("STYLE:\n" + self._resolve(template_version.prompt_config.get("style", "")))
        if brief.inside_joke:
            sections.append("INSIDE_JOKE:\n" + brief.inside_joke)
        if brief.sender_message:
            sections.append("MESSAGE:\n" + brief.sender_message)
        negative = template_version.prompt_config.get("negative_prompt")
        if negative:
            sections.append("NEGATIVE:\n" + negative)
        return "\n\n".join(sections)

    def _character_block(self, brief: CreativeBriefRead) -> str:
        parts = []
        if brief.recipient:
            parts.append(f"{brief.recipient.get('name','')}, {brief.recipient.get('age','')} years old")
        if brief.relationship_:
            parts.append(f"relationship: {brief.relationship_}")
        return ", ".join(parts) if parts else ""

    def _resolve(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value)


PromptCompilerService = PromptCompiler
