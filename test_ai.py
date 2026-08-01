from google import genai

client = genai.Client(
    api_key="googlekey"
)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Say hello in one sentence."
)

print(response.text)