#!/usr/bin/env python3
"""Update .env file with Supabase credentials"""

from pathlib import Path

# Supabase credentials
SUPABASE_PROJECT_ID = "rpygndzdvyqeeygvkheq"
SUPABASE_PUBLISHABLE_KEY = "sb_publishable_CgHA897jQ3kLMrkLQ5G_rA_5KcOerkw"
SUPABASE_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co"

# Read existing .env
env_path = Path(".env")
if env_path.exists():
    content = env_path.read_text()
    
    # Update Supabase URL
    if "SUPABASE_URL=" in content:
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith("SUPABASE_URL="):
                new_lines.append(f"SUPABASE_URL={SUPABASE_URL}")
            elif line.startswith("SUPABASE_KEY="):
                new_lines.append(f"SUPABASE_KEY={SUPABASE_PUBLISHABLE_KEY}")
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
    else:
        # Add if missing
        content += f"\nSUPABASE_URL={SUPABASE_URL}\n"
        content += f"SUPABASE_KEY={SUPABASE_PUBLISHABLE_KEY}\n"
    
    env_path.write_text(content)
    print(f"[OK] Updated .env with Supabase credentials")
    print(f"  URL: {SUPABASE_URL}")
    print(f"  Key: {SUPABASE_PUBLISHABLE_KEY[:20]}...")
else:
    print(".env file not found. Run create_env_template.py first.")

if __name__ == "__main__":
    pass

