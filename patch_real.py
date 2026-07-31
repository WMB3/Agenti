import re

with open('backend/main.py', 'r') as f:
    content = f.read()

# Replace the specific sync call with async in analyze_vehicle
old_call = """        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
"""

new_call = """        response = await gemini_client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
"""

if old_call in content:
    content = content.replace(old_call, new_call)
    with open('backend/main.py', 'w') as f:
        f.write(content)
    print("Patched successfully")
else:
    print("Could not find the target code to patch.")
