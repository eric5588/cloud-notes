import os
import requests
import frontmatter # Requires python-frontmatter
import sys

# Configuration
# Assuming using OpenAI-compatible API (could be OpenAI, deepseek, etc.)
API_KEY = os.environ.get("LLM_API_KEY")
API_BASE = "https://api.openai.com/v1" 
# For demo purposes, we will mock the LLM call if no key to prevent crashing,
# or user should replace this with their actual provider.

def get_summary(content):
    if not API_KEY:
        return "Auto-generated summary (No API Key provided)."
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"Please provide a concise 2-sentence summary of the following markdown note. Return only the summary text.\n\n{content[:2000]}"
    
    data = {
        "model": "gpt-3.5-turbo", # Or user preferred model
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    
    try:
        resp = requests.post(f"{API_BASE}/chat/completions", json=data, headers=headers)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'].strip()
        else:
            print(f"Error from API: {resp.text}")
            return "Summary generation failed."
    except Exception as e:
        print(f"Exception: {e}")
        return "Summary generation error."

def process_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md") and file != "README.md":
                filepath = os.path.join(root, file)
                
                # Load file
                post = frontmatter.load(filepath)
                
                # Check if it already has a summary to avoid re-generating expensive calls
                # or check if 'ai_summary' key exists.
                if 'ai_summary' not in post.metadata:
                    print(f"Generating summary for {file}...")
                    summary = get_summary(post.content)
                    post.metadata['ai_summary'] = summary
                    
                    # Write back
                    with open(filepath, 'w') as f:
                        f.write(frontmatter.dumps(post))

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    process_files(target_dir)
