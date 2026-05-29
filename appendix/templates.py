"""
15 production-ready prompt templates for common Claude use cases.
Each template uses XML structuring and includes all critical ingredients:
role, context, task, format, and constraints.
"""

EXTRACTION_TEMPLATE = """
You are a data extraction specialist. Extract exactly the fields listed in
<schema> from the <source>. Return valid JSON only — no prose, no commentary.
If a field is not present, use null. If a value is ambiguous, use the most literal interpretation.

<schema>
{json_schema}
</schema>

<source>
{raw_text}
</source>
"""

QA_TEMPLATE = """
Answer the question using only the information in <document>.
For every factual claim, add a parenthetical citation like (§2.3) or (p.14).
If the answer is not in the document, say "Not covered in this document" — do not infer.

<document>
{document_text}
</document>

<question>
{question}
</question>
"""

CODE_REVIEW_TEMPLATE = """
You are a senior {language} engineer. Review the code in <code> and report:
1. Security vulnerabilities (label CRITICAL / HIGH / MEDIUM / LOW)
2. Logic errors or bugs
3. Performance issues
4. Best-practice violations

For each issue: file/line reference, severity, description, fix suggestion.
If no issues in a category, write "None found."

<code>
{code}
</code>
"""

SUPPORT_TRIAGE_TEMPLATE = """
You are a support triage specialist. Classify the ticket and draft a response.
Return ONLY valid JSON — no prose outside the JSON.

{{"priority": "critical|high|medium|low",
  "category": "billing|technical|feature|general",
  "sentiment": "frustrated|neutral|positive",
  "suggested_team": "engineering|billing|sales|support",
  "draft_response": "2-3 sentence empathetic acknowledgement",
  "internal_note": "one sentence for the agent handling this"}}

<ticket>
From: {from_email}
Subject: {subject}

{body}
</ticket>
"""

SUMMARISATION_TEMPLATE = """
Summarise the following document for {audience}.

<requirements>
- Length: {length_words} words
- Tone: {tone}
- Include: {must_include}
- Exclude: {must_exclude}
</requirements>

<document>
{document}
</document>
"""

TRANSLATION_TEMPLATE = """
Translate the following text from {source_language} to {target_language}.

<requirements>
- Preserve formatting (headers, bullet points, code blocks)
- Maintain technical terminology in the target language
- If a term has no direct translation, keep the original and add a parenthetical explanation
- Do not translate proper nouns, brand names, or code
</requirements>

<text>
{text}
</text>
"""

SQL_GENERATION_TEMPLATE = """
You are a SQL expert. Generate a {dialect} SQL query for the following request.

<schema>
{table_schema}
</schema>

<request>
{natural_language_request}
</request>

<constraints>
- SELECT queries only — no INSERT, UPDATE, DELETE, DROP
- Use table aliases for readability
- Add a comment explaining any non-obvious logic
- Return the query and a one-sentence explanation of what it does
</constraints>
"""

EMAIL_DRAFTING_TEMPLATE = """
Draft a professional email for the following situation.

<context>
Sender: {sender_name}, {sender_role} at {company}
Recipient: {recipient_name}, {recipient_role}
Relationship: {relationship}
</context>

<task>
{email_purpose}
</task>

<tone>
{tone_description}
</tone>

<constraints>
- Maximum {max_words} words
- No generic openers ("I hope this email finds you well")
- End with a clear, single call to action
</constraints>
"""

CONTENT_MODERATION_TEMPLATE = """
Review the following user-generated content for policy violations.
Return JSON only.

{{"verdict": "approved|rejected|escalate",
  "violations": ["list of specific policy violations, empty if none"],
  "severity": "none|low|medium|high|critical",
  "reasoning": "one sentence explanation",
  "recommended_action": "approve|warn|remove|ban_user"}}

<policies>
{policy_list}
</policies>

<content>
{user_content}
</content>
"""

MEETING_NOTES_TEMPLATE = """
You are an executive assistant. Convert the following meeting transcript into structured notes.

<output_format>
## Meeting: {meeting_title}
**Date:** {date}
**Attendees:** {attendees}

### Key Decisions
- [Each firm decision made, with owner]

### Action Items
| Item | Owner | Due Date |
|------|-------|----------|

### Open Questions
- [Questions raised but not resolved]

### Summary
[2-3 sentence overview]
</output_format>

<transcript>
{transcript}
</transcript>
"""

PERSONA_CHAT_TEMPLATE = """
You are {persona_name}, {persona_description}.

<personality>
Tone: {tone}
Communication style: {style}
Areas of expertise: {expertise}
</personality>

<constraints>
{constraints}
</constraints>

<context>
{session_context}
</context>
"""

RISK_ASSESSMENT_TEMPLATE = """
You are a risk analyst. Assess the following proposal for risks and mitigations.

<proposal>
{proposal_text}
</proposal>

<assessment_criteria>
Evaluate across: technical feasibility, regulatory compliance, financial exposure,
operational complexity, reputational risk.
</assessment_criteria>

<output_format>
For each risk: description, likelihood (1-5), impact (1-5), risk score (likelihood × impact),
recommended mitigation, residual risk after mitigation.
Return as a JSON array of risk objects, then a one-paragraph executive summary.
</output_format>
"""

COMPETITIVE_ANALYSIS_TEMPLATE = """
Analyse the competitive landscape for {company} in the {market} market.

<companies_to_analyse>
{competitor_list}
</companies_to_analyse>

<dimensions>
Compare across: pricing model, target customer segment, key differentiators,
known weaknesses, recent strategic moves.
</dimensions>

<output_format>
1. Comparison table (markdown)
2. SWOT for {company} relative to the field
3. Three strategic recommendations (one sentence each)
</output_format>

<constraints>
- Base analysis on facts — flag any claims that are uncertain
- Do not fabricate pricing or market share numbers
- Cite the basis for each claim where possible
</constraints>
"""

INCIDENT_REPORT_TEMPLATE = """
Generate a structured incident report from the following raw notes.

<output_format>
## Incident Report: {incident_id}

**Severity:** {severity}
**Status:** {status}
**Duration:** {duration}

### Timeline
[Chronological list of events with timestamps]

### Root Cause
[Technical root cause in plain language]

### Impact
[Quantified impact: users affected, data at risk, revenue impact]

### Resolution
[Steps taken to resolve]

### Action Items
[Preventive measures with owners and due dates]

### Communication Sent
[Summary of external communications]
</output_format>

<raw_notes>
{raw_notes}
</raw_notes>
"""

HYPOTHESIS_TESTING_TEMPLATE = """
You are a data scientist. Interpret the following A/B test results.

<experiment>
Name: {experiment_name}
Hypothesis: {hypothesis}
Control: {control_description}
Variant: {variant_description}
Duration: {duration}
Sample size: {sample_size}
Primary metric: {primary_metric}
</experiment>

<results>
{results_data}
</results>

<output>
1. Statistical significance assessment (p-value interpretation)
2. Practical significance (effect size and business impact)
3. Recommendation: ship / iterate / abandon — with justification
4. Risks of implementing based on these results
5. Follow-up experiments recommended
</output>
"""


TEMPLATES = {
    "extraction": EXTRACTION_TEMPLATE,
    "qa": QA_TEMPLATE,
    "code_review": CODE_REVIEW_TEMPLATE,
    "support_triage": SUPPORT_TRIAGE_TEMPLATE,
    "summarisation": SUMMARISATION_TEMPLATE,
    "translation": TRANSLATION_TEMPLATE,
    "sql_generation": SQL_GENERATION_TEMPLATE,
    "email_drafting": EMAIL_DRAFTING_TEMPLATE,
    "content_moderation": CONTENT_MODERATION_TEMPLATE,
    "meeting_notes": MEETING_NOTES_TEMPLATE,
    "persona_chat": PERSONA_CHAT_TEMPLATE,
    "risk_assessment": RISK_ASSESSMENT_TEMPLATE,
    "competitive_analysis": COMPETITIVE_ANALYSIS_TEMPLATE,
    "incident_report": INCIDENT_REPORT_TEMPLATE,
    "hypothesis_testing": HYPOTHESIS_TESTING_TEMPLATE,
}


if __name__ == "__main__":
    print(f"Loaded {len(TEMPLATES)} production-ready prompt templates.")
    for name in TEMPLATES:
        print(f"  - {name}")
