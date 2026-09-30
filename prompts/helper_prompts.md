# NetSage AI - Helper and Auxiliary Prompts

This file contains specialized prompts used by the NetSage AI system for validation, human review comparison, and missing evidence handling.

---

## 1. Case Troubleshooting Prompt Template (User Message)
```markdown
Analyze the following Cisco Packet Tracer networking case and produce an evidence-backed diagnosis strictly in the required JSON format:

Case ID: {case_id}
Title: {title}
Symptom: {symptom}
Topology: {topology}
Reported Device: {device}
Client Configuration:
{client_configuration}

Show Command Executed:
# {show_command}

Show Command Output:
{show_output}

Instructions:
1. Examine the client configuration and the show command output.
2. Determine if the evidence conclusively identifies the fault or if evidence is insufficient.
3. Formulate the root cause, identify the exact OSI layer and networking concept.
4. Cite verbatim evidence lines from the output.
5. Provide the exact Cisco IOS commands required to remedy the problem.
6. Return ONLY the JSON object.
```

---

## 2. Incomplete Evidence Fallback Prompt
Used when the rule checker or preliminary parse indicates that a suspected fault domain lacks required diagnostic show commands.

```markdown
Diagnostic Warning: The provided case presents symptoms suggestive of a {suspected_fault} issue, but the command outputs provided do not include the definitive show command (e.g. {recommended_command}).

Do NOT hallucinate or assume interface states. Explicitly report:
- Confidence: LOW
- Root Cause: "Preliminary indication suggests possible {suspected_fault}, but required diagnostic evidence ({recommended_command}) is absent."
- Next Commands: ["{recommended_command}"]
```

---

## 3. Human Review Comparison Prompt
Used to evaluate reviewer edits and extract educational lessons for the Responsible AI log.

```markdown
Compare the AI-generated diagnosis with the human reviewer's final decision:

AI Root Cause: {ai_diagnosis}
Human Decision: {human_decision}
Corrected Root Cause: {corrected_diagnosis}
Reviewer Explanation: {explanation}

Summarize:
1. Why did the AI fail or require adjustment?
2. What specific evidence did the AI overlook or misinterpret?
3. What engineering principle or lesson should be logged?
```
