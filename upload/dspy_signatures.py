# ghost_cell/src/dspy_signatures.py

import dspy
from typing import List

class GeneratePlan(dspy.Signature):
    """
    You are a world-class web automation agent. Generate a concise, step-by-step plan to accomplish the given task.
    Each step must be a specific, actionable command from the allowed list.
    Use CSS selectors to identify elements.
    """
    
    task = dspy.InputField(desc="The high-level objective for the agent.")
    allowed_tools = dspy.InputField(
        desc="A JSON string detailing available tools. Format: {'TOOL_NAME': 'description'}"
    )
    
    plan = dspy.OutputField(
        desc="A JSON formatted list of strings, where each string is a precise command.",
        prefix="```json\n"
    )

class AnalyzeContentAndRefinePlan(dspy.Signature):
    """
    You are a web automation agent. Analyze the provided webpage content and the remaining plan.
    Decide the single next best action. Your action must be one of the allowed tools.
    If the task is complete, use the FINISH tool.
    """
    
    task = dspy.InputField(desc="The original high-level objective.")
    remaining_plan = dspy.InputField(desc="The rest of the original plan.")
    page_content_summary = dspy.InputField(desc="A summary of the current webpage content.")
    scratchpad = dspy.InputField(desc="A log of recent actions and observations.")
    allowed_tools = dspy.InputField(desc="A list of available tool commands.")
    
    next_action = dspy.OutputField(desc="The single best command to execute next.")

