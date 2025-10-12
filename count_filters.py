#!/usr/bin/env python3
"""
Count filters from test output.
"""

import json

with open('test_output.txt', 'r') as f:
    content = f.read()
    
# Extract JSON from the output
lines = content.split('\n')
json_start = False
json_lines = []

for line in lines:
    if line.startswith('Response: {'):
        json_start = True
        json_lines.append(line[10:])  # Remove "Response: " prefix
    elif json_start:
        json_lines.append(line)

json_str = '\n'.join(json_lines)
data = json.loads(json_str)

filters = data['data']['model_metadata']['filters']
print(f"Found {len(filters)} filters for the Post model")

# Show first few and last few filters
print("\nFirst 5 filters:")
for i, f in enumerate(filters[:5]):
    print(f"  {i+1}. {f['name']} ({f['filter_type']})")

print(f"\n... ({len(filters)-10} more filters) ...\n")

print("Last 5 filters:")
for i, f in enumerate(filters[-5:], len(filters)-4):
    print(f"  {i}. {f['name']} ({f['filter_type']})")