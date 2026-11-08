"""
Universal Skill.md Synthesizer for SkillForge.
Converts arbitrary text, SOPs, documentation, or extracted files into a standardized,
highly effective SKILL.md file compatible across Claude, Grok, ChatGPT, Gemini, and Antigravity.
"""

from __future__ import annotations
import re
import os
import yaml
from typing import Dict, Any, List, Optional, Tuple


class SkillSynthesizer:
    """Transforms parsed inputs into valid, cross-platform SKILL.md documents."""

    DEFAULT_PLATFORMS = ["claude", "grok", "chatgpt", "gemini", "antigravity"]

    @classmethod
    def synthesize(
        cls,
        raw_text: str,
        skill_name: Optional[str] = None,
        description: Optional[str] = None,
        target_platforms: Optional[List[str]] = None,
        author: str = "Titus SkillForge Universal",
        version: str = "1.0.0",
        boundary_level: str = "standard",
        category: str = "general",
        custom_tags: Optional[List[str]] = None,
        gemini_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        platforms = target_platforms or cls.DEFAULT_PLATFORMS

        if gemini_api_key or os.getenv("GEMINI_API_KEY"):
            llm_result = cls._try_llm_synthesis(
                raw_text, skill_name, description, platforms, author, version, boundary_level, category, gemini_api_key
            )
            if llm_result:
                return llm_result

        return cls._offline_semantic_synthesizer(
            raw_text=raw_text,
            skill_name=skill_name,
            description=description,
            platforms=platforms,
            author=author,
            version=version,
            boundary_level=boundary_level,
            category=category,
            custom_tags=custom_tags
        )

    @staticmethod
    def slugify(text: str) -> str:
        clean = text.lower().strip()
        clean = re.sub(r'[\s_]+', '-', clean)
        clean = re.sub(r'[^a-z0-9-]', '', clean)
        clean = re.sub(r'-+', '-', clean)
        clean = clean.strip('-')
        return clean[:48] or "universal-skill"

    @classmethod
    def _extract_intent_keywords(cls, text: str) -> List[str]:
        tokens = re.findall(r'\b[a-zA-Z]{3,15}\b', text.lower())
        stop_words = {
            'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have', 'were', 'which',
            'will', 'your', 'about', 'into', 'some', 'could', 'them', 'than', 'then',
            'also', 'each', 'make', 'when', 'what', 'been', 'user', 'should', 'would',
            'you', 'are', 'was', 'has', 'had', 'not', 'but', 'can', 'all', 'any', 'our',
            'their', 'they', 'its', 'his', 'her', 'she', 'him', 'who', 'how', 'why',
            'may', 'might', 'must', 'shall', 'being', 'been', 'does', 'did', 'doing',
            'only', 'just', 'more', 'most', 'other', 'such', 'very', 'own', 'same',
            'over', 'under', 'again', 'further', 'once', 'here', 'there', 'where',
            'please', 'using', 'used', 'use', 'based', 'via', 'per', 'etc'
        }
        filtered = [t for t in tokens if t not in stop_words and len(t) > 2]
        
        action_triggers = [
            'analyze', 'audit', 'build', 'cleanup', 'configure', 'convert', 'create',
            'debug', 'deploy', 'detect', 'diagnose', 'document', 'evaluate', 'export',
            'fix', 'generate', 'inspect', 'integrate', 'migrate', 'monitor', 'optimize',
            'parse', 'profile', 'refactor', 'repair', 'review', 'scan', 'test', 'validate'
        ]
        found_actions = [t for t in set(filtered) if t in action_triggers]
        
        counts: Dict[str, int] = {}
        for w in filtered:
            counts[w] = counts.get(w, 0) + 1
        sorted_words = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        top_domain = [w for w, _ in sorted_words[:8] if w not in found_actions]
        
        combined = (found_actions[:3] + top_domain[:5])
        return combined[:6] if combined else ["execute", "process", "workflow"]

    @classmethod
    def _extract_steps_and_rules(cls, text: str) -> Tuple[List[str], List[str], List[str]]:
        lines = text.splitlines()
        steps = []
        rules = []
        errors = []

        in_steps = False
        in_rules = False

        for line in lines:
            sline = line.strip()
            if not sline:
                continue

            lower_line = sline.lower()
            if any(k in lower_line for k in ['step', 'workflow', 'procedure', 'instructions', 'process', 'how to']):
                in_steps = True
                in_rules = False
                continue
            elif any(k in lower_line for k in ['rule', 'constraint', 'requirement', 'boundary', 'safety', 'warning']):
                in_rules = True
                in_steps = False
                continue
            elif any(k in lower_line for k in ['error', 'troubleshoot', 'failure', 'fallback', 'edge case']):
                in_steps = False
                in_rules = False

            m_step = re.match(r'^(?:\d+[\.\)]|\-|\*|\#\#\#)\s+(.+)$', sline)
            if m_step:
                content = m_step.group(1).strip()
                if len(content) > 10:
                    if in_rules or any(rk in content.lower() for rk in ['must', 'never', 'do not', 'only', 'ensure']):
                        rules.append(content)
                    else:
                        steps.append(content)
                continue

            if any(ek in lower_line for ek in ['error', 'fail', 'timeout', 'missing', 'exception', 'invalid']):
                if len(sline) > 15:
                    errors.append(sline)

        if not steps:
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 25]
            if sentences:
                steps = sentences[:5]
            else:
                steps = [
                    "Inspect the context, inputs, and environment parameters.",
                    "Validate requirements, preconditions, and safety boundaries.",
                    "Execute the primary transformation according to specifications.",
                    "Verify the resulting output and ensure structural integrity.",
                    "Deliver the final structured outcome with diagnostic verification."
                ]

        if not rules:
            rules = [
                "Never execute unconfirmed destructive operations without explicit confirmation.",
                "Preserve existing user code, comments, and project configurations.",
                "Maintain complete idempotency and deterministic execution.",
                "Adhere to minimal token bloat and high signal-to-noise communication."
            ]

        if not errors:
            errors = [
                "Missing inputs or prerequisites: Halt gracefully and request specific missing parameters.",
                "Validation or syntax failure: Diagnose root cause, self-correct, or log detailed telemetry.",
                "Environment constraint: Fall back to safe read-only simulation and alert user."
            ]

        return steps, rules, errors

    @classmethod
    def _offline_semantic_synthesizer(
        cls,
        raw_text: str,
        skill_name: Optional[str],
        description: Optional[str],
        platforms: List[str],
        author: str,
        version: str,
        boundary_level: str,
        category: str,
        custom_tags: Optional[List[str]]
    ) -> Dict[str, Any]:
        clean_text = raw_text.strip()
        
        if not skill_name or not skill_name.strip():
            first_heading_match = re.search(r'^#+\s+(.+)$', clean_text, re.MULTILINE)
            if first_heading_match:
                candidate = first_heading_match.group(1).strip()
            else:
                keywords = cls._extract_intent_keywords(clean_text)
                candidate = "-".join(keywords[:3]) if keywords else "universal-workflow"
            final_name = cls.slugify(candidate)
        else:
            final_name = cls.slugify(skill_name)

        extracted_keywords = cls._extract_intent_keywords(clean_text)
        tags = custom_tags or []
        for kw in extracted_keywords:
            if kw not in tags:
                tags.append(kw)
        if category not in tags:
            tags.append(category)

        if not description or not description.strip():
            trigger_list = ", ".join(tags[:4])
            final_description = (
                f"Automates and standardizes {final_name.replace('-', ' ')} tasks with robust validation "
                f"and safety boundaries. Trigger when: {trigger_list}, or handling related workflows."
            )
        else:
            desc_clean = description.strip()
            if "trigger" not in desc_clean.lower() and "use for" not in desc_clean.lower():
                final_description = f"{desc_clean} Use for: {', '.join(tags[:4])}."
            else:
                final_description = desc_clean

        steps, rules, errors = cls._extract_steps_and_rules(clean_text)

        boundary_matrix = {
            "read-only": [
                "Strict Read-Only Mode: This skill must never modify external files, repositories, or system state without user consent.",
                "No destructive terminal commands or unapproved state alterations."
            ],
            "standard": [
                "Standard Operation: Safe modifications within current workspace scope permitted.",
                "Consequential external actions (force-pushing, cloud deletion, billing changes) require explicit confirmation.",
                "Always run verification checks prior to completing operations."
            ],
            "high-consequence": [
                "High Consequence Protection: Multi-stage verification required for all operations.",
                "Mandatory pre-flight audit and dry-run execution.",
                "Complete backup or snapshot must be confirmed before destructive operations."
            ]
        }.get(boundary_level, [
            "Maintain minimal privilege and adhere to safe workspace operations."
        ])

        all_rules = rules + boundary_matrix

        frontmatter_dict: Dict[str, Any] = {
            "name": final_name,
            "description": final_description,
            "version": version,
            "author": author,
            "license": "MIT",
            "compatibility": ", ".join(platforms),
            "metadata": {
                "generator": "Titus SkillForge",
                "category": category,
                "boundary_level": boundary_level,
                "tags": tags[:8],
                "grok": {
                    "tags": tags[:8],
                    "related_skills": [f"{tags[0]}-helper" if tags else "assistant", "systematic-debugging"]
                },
                "claude": {
                    "slash_command": f"/{final_name}"
                },
                "antigravity": {
                    "auto_trigger": True
                }
            }
        }

        yaml_content = yaml.dump(
            frontmatter_dict,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True
        ).strip()

        title_display = " ".join(word.capitalize() for word in final_name.split("-"))
        
        md_body_parts = [
            f"---",
            yaml_content,
            f"---",
            "",
            f"# {title_display}",
            "",
            "## Purpose & Capability Overview",
            "",
            final_description,
            "",
            "## Activation & Trigger Criteria",
            "",
            "Agents should invoke this skill when the following conditions or user prompts occur:",
            "",
            f"- **Direct keywords**: `{', '.join(tags)}`",
            f"- **User intent**: Requests relating to {title_display.lower()}, automated processing, or pipeline execution.",
            f"- **Context cues**: Presence of relevant files, error logs, or configuration artifacts matching this domain.",
            "",
            "## Execution Workflow",
            "",
            "Execute the following steps in sequence:"
        ]

        for idx, step in enumerate(steps, 1):
            md_body_parts.append(f"{idx}. **{step.split(':')[0]}**: {step}")

        md_body_parts.extend([
            "",
            "## Operational Rules & Boundaries",
            ""
        ])

        for r in all_rules:
            md_body_parts.append(f"- {r}")

        md_body_parts.extend([
            "",
            "## Expected Input & Output Contracts",
            "",
            "| Contract Component | Specification |",
            "|---|---|",
            f"| **Inputs** | Target file, text context, or command arguments relevant to `{final_name}`. |",
            "| **Outputs** | Structured, verified artifact or diagnostic report adhering to the task goal. |",
            "| **Verification** | Automated validation or sanity check confirming zero regressions. |",
            "",
            "## Error Handling & Edge Cases",
            "",
            "| Scenario | Agent Response Protocol |",
            "|---|---|",
            f"| Missing context or parameter | Request specific missing parameter before proceeding. |",
            f"| Malformed input structure | Report exact parsing discrepancy and attempt safe normalization. |",
            f"| Safety boundary violation | Abort execution and prompt user for explicit authorization. |"
        ])

        for err in errors[:3]:
            if ":" in err:
                scen, resp = err.split(":", 1)
                md_body_parts.append(f"| {scen.strip()} | {resp.strip()} |")
            else:
                md_body_parts.append(f"| Unexpected condition | {err.strip()} |")

        md_body_parts.extend([
            "",
            "## Concrete Scenarios & Examples",
            "",
            f"### Scenario: Running `{final_name}` with default parameters",
            "",
            "**User Request:**",
            f"> \"Please run {final_name} on the current project assets and report results.\"",
            "",
            "**Agent Action:**",
            f"1. Ingests source files and validates preconditions.",
            f"2. Executes the workflow sequence without destructive side effects.",
            f"3. Delivers a verified summary report with actionable output.",
            "",
            "---",
            "*Generated by Titus SkillForge — Multi-Modal Universal Agent Engine (Compatible with Claude, Grok, ChatGPT, Gemini, and Antigravity).*"
        ])

        full_markdown = "\n".join(md_body_parts).strip() + "\n"

        return {
            "markdown": full_markdown,
            "frontmatter": frontmatter_dict,
            "name": final_name,
            "validation": {
                "valid": True,
                "name": final_name,
                "character_count": len(full_markdown),
                "word_count": len(full_markdown.split()),
                "platforms": platforms
            }
        }

    @classmethod
    def _try_llm_synthesis(
        cls,
        raw_text: str,
        skill_name: Optional[str],
        description: Optional[str],
        platforms: List[str],
        author: str,
        version: str,
        boundary_level: str,
        category: str,
        api_key: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not key:
            return None

        try:
            from google import genai
            client = genai.Client(api_key=key)
            prompt = f"""
You are the world's leading Agent Skill Architect.
Synthesize the provided source document/instructions into a pristine, production-ready universal SKILL.md.

Source Content:
\"\"\"
{raw_text[:20000]}
\"\"\"

Requirements:
1. Output MUST start with standard YAML frontmatter bounded by triple dashes (`---`).
2. Frontmatter fields required:
   - name: kebab-case string (e.g. {cls.slugify(skill_name or 'my-skill')})
   - description: Concise summary of capability AND trigger criteria ("Use for: ... Trigger when: ...")
   - version: "{version}"
   - author: "{author}"
   - license: "MIT"
   - compatibility: "{', '.join(platforms)}"
   - metadata:
       generator: "Titus SkillForge"
       category: "{category}"
       boundary_level: "{boundary_level}"
       tags: list of relevant keywords
       grok:
         tags: list of keywords
         related_skills: list
       claude:
         slash_command: "/{cls.slugify(skill_name or 'my-skill')}"
       antigravity:
         auto_trigger: true
3. Following the frontmatter, write comprehensive Markdown containing:
   # <Title>
   ## Purpose & Capability Overview
   ## Activation & Trigger Criteria
   ## Execution Workflow
   ## Operational Rules & Boundaries
   ## Expected Input & Output Contracts
   ## Error Handling & Edge Cases
   ## Concrete Scenarios & Examples
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            if response and response.text:
                text_out = response.text.strip()
                if text_out.startswith("```markdown"):
                    text_out = text_out[11:].strip()
                if text_out.startswith("```"):
                    text_out = text_out[3:].strip()
                if text_out.endswith("```"):
                    text_out = text_out[:-3].strip()

                fm_match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n(.*)$', text_out, re.DOTALL)
                if fm_match:
                    fm_data = yaml.safe_load(fm_match.group(1))
                    actual_name = fm_data.get("name", cls.slugify(skill_name or "skill"))
                    return {
                        "markdown": text_out,
                        "frontmatter": fm_data,
                        "name": actual_name,
                        "validation": {
                            "valid": True,
                            "source": "gemini-llm",
                            "name": actual_name,
                            "character_count": len(text_out),
                            "word_count": len(text_out.split()),
                            "platforms": platforms
                        }
                    }
        except Exception:
            pass

        return None
