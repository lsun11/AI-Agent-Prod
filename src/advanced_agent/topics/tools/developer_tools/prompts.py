# src/topics/developer_tools/base_prompts.py
from __future__ import annotations

from ..base_prompts import BaseCSResearchPrompts



class DeveloperToolsPrompts(BaseCSResearchPrompts):
    """
    Classic developer tools and programming ecosystems.

    Examples:
      - IDEs/editors (VS Code, JetBrains, Vim, Emacs)
      - Build tools, test runners, debugging/profiling tools
      - Package managers, CLIs, SDKs, frameworks, libraries

    NOT:
      - Cloud infra platforms (AWS → cloud)
      - API companies whose product is an API (Stripe API → api)
    """

    TOPIC_LABEL = "developer tool, library, SDK, or programming platform"
    ANALYSIS_SUBJECT = "developer tools, programming technologies, and open-source libraries"
    RECOMMENDER_ROLE = "senior software engineer"

