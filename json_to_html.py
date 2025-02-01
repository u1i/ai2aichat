import json
import sys
import os
from pathlib import Path
import markdown2

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Conversation</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
            background: #f8f9fa;
            color: #333;
        }}
        .message {{
            margin: 1.5rem 0;
            padding: 1.2rem;
            border-radius: 12px;
            position: relative;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .o1 {{
            background: #ffffff;
            margin-left: 2rem;
            border-left: 4px solid #2563eb;
        }}
        .r1 {{
            background: #ffffff;
            margin-right: 2rem;
            border-left: 4px solid #059669;
        }}
        .speaker {{
            font-weight: 600;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .o1 .speaker {{
            color: #2563eb;
        }}
        .r1 .speaker {{
            color: #059669;
        }}
        .content {{
            color: #1f2937;
        }}
        .content p {{
            margin: 0.5em 0;
        }}
        .content p:first-child {{
            margin-top: 0;
        }}
        .content p:last-child {{
            margin-bottom: 0;
        }}
        .content strong {{
            color: #111827;
        }}
        .content ul, .content ol {{
            margin: 0.5em 0;
            padding-left: 1.5em;
        }}
        .reasoning-toggle {{
            cursor: pointer;
            color: #059669;
            font-size: 0.85rem;
            margin-top: 0.8rem;
            user-select: none;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            background: #ecfdf5;
            transition: all 0.2s ease;
        }}
        .reasoning-toggle:hover {{
            background: #d1fae5;
        }}
        .reasoning {{
            margin-top: 1rem;
            padding: 1rem;
            background: #f9fafb;
            border-radius: 8px;
            font-size: 0.9rem;
            color: #4b5563;
            border-left: 2px solid #059669;
        }}
        .initial {{
            text-align: center;
            font-style: italic;
            color: #666;
            margin: 2rem 0;
        }}
        @media (max-width: 600px) {{
            .message {{
                margin: 1rem 0;
            }}
            .o1, .r1 {{
                margin-left: 0;
                margin-right: 0;
            }}
        }}
    </style>
    <script>
        function toggleReasoning(id) {{
            const reasoning = document.getElementById(id);
            const toggle = document.getElementById(id + '-toggle');
            if (reasoning.style.display === 'block') {{
                reasoning.style.display = 'none';
                toggle.innerHTML = '<span>▶</span> Show reasoning';
            }} else {{
                reasoning.style.display = 'block';
                toggle.innerHTML = '<span>▼</span> Hide reasoning';
            }}
        }}
    </script>
</head>
<body>
    {content}
</body>
</html>
'''

MESSAGE_TEMPLATE = {
    'o1': '''
    <div class="message o1">
        <div class="speaker">O1</div>
        <div class="content">{message}</div>
    </div>
    ''',
    'r1': '''
    <div class="message r1">
        <div class="speaker">R1</div>
        <div class="content">{message}</div>
        <div id="reasoning-{id}-toggle" class="reasoning-toggle" onclick="toggleReasoning('reasoning-{id}')"><span>▶</span> Show reasoning</div>
        <div id="reasoning-{id}" class="reasoning" style="display: none">{reasoning}</div>
    </div>
    ''',
    'initial': '''
    <div class="initial">{message}</div>
    '''
}

def convert_markdown(text):
    """Convert markdown to HTML with specific features enabled."""
    return markdown2.markdown(text, extras=['fenced-code-blocks', 'break-on-newline'])

def convert_json_to_html(json_file):
    # Read JSON file
    with open(json_file, 'r') as f:
        conversation = json.load(f)
    
    # Generate message HTML
    messages_html = []
    for i, entry in enumerate(conversation):
        msg_type = entry['type']
        template = MESSAGE_TEMPLATE[msg_type]
        
        # Convert markdown to HTML
        message_html = convert_markdown(entry['message'])
        
        if msg_type == 'r1':
            reasoning_html = convert_markdown(entry.get('reasoning', 'No reasoning provided'))
            messages_html.append(template.format(
                message=message_html,
                reasoning=reasoning_html,
                id=i
            ))
        else:
            messages_html.append(template.format(message=message_html))
    
    # Generate full HTML
    content = '\n'.join(messages_html)
    html = HTML_TEMPLATE.format(content=content)
    
    # Write HTML file
    output_file = Path(json_file).with_suffix('.html')
    with open(output_file, 'w') as f:
        f.write(html)
    
    return output_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python json_to_html.py <json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    if not os.path.exists(json_file):
        print(f"Error: File {json_file} not found")
        sys.exit(1)
    
    output_file = convert_json_to_html(json_file)
    print(f"Created HTML file: {output_file}")

if __name__ == "__main__":
    main()
