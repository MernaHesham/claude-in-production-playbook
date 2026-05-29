from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

FEW_SHOT_EXAMPLES = """
<examples>

<example>
<input>Customer: The dashboard is loading slowly.</input>
<output>
Category: Performance
Priority: Medium
Suggested response: "Thanks for flagging this. Our engineering team has noted the issue and is investigating. Could you tell us your browser and the approximate time it occurred?"
</output>
</example>

<example>
<input>Customer: I was charged twice for the same month.</input>
<output>
Category: Billing
Priority: High
Suggested response: "We're sorry for this. Please send your account email to billing@company.com with 'Duplicate Charge' in the subject and we'll resolve it within 24h."
</output>
</example>

</examples>
"""

SYSTEM = f"""You are a support ticket classifier.
Classify the customer message and draft an acknowledgement.

{FEW_SHOT_EXAMPLES}

Format your response as:
Category: <category>
Priority: <critical|high|medium|low>
Suggested response: <2-3 sentence acknowledgement>
"""

if __name__ == "__main__":
    ticket = "My API key stopped working after I reset my password."
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=SYSTEM,
        messages=[{"role": "user", "content": ticket}]
    )
    print(response.content[0].text)
