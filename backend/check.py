try:
    from google import genai
    from google.genai import types
    print("Found genai")
except Exception as e:
    print(e)
