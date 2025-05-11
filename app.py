from resemble import Resemble

# Set your API key
Resemble.api_key('Ew2pEvxMVxWWBQ2DzYzUTgtt')

# Get default project
project_uuid = Resemble.v2.projects.all(1, 10)['items'][0]['uuid']

# Get default voice
voice_uuid = Resemble.v2.voices.all(1, 10)['items'][0]['uuid']

# Prepare clip text
body = 'This is a test'

# Create the voice clip synchronously
response = Resemble.v2.clips.create_sync(
    project_uuid,
    voice_uuid,
    body
)

# Output response
print("API Response:")
print(response)

# Check audio URL
audio_url = response.get('audio_src')
if audio_url:
    print("✅ Audio URL:", audio_url)
else:
    print("❌ No audio_src returned.")
