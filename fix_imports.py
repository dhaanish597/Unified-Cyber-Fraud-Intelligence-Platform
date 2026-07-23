import re
import os

files = [
    'web/src/components/fabric/DigitalTwinBaseline.jsx',
    'web/src/components/fabric/ResponseOrchestrator.jsx',
    'web/src/components/fabric/TrustFabric.jsx',
    'web/src/components/layout/Sidebar.jsx',
    'web/src/pages/CustomersPage.jsx',
    'web/src/pages/OperationsCenterPage.jsx',
    'web/src/pages/SyntheticLabPage.jsx'
]

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the lucide-react import block
    import_pattern = re.compile(r'import\s+\{([^}]+)\}\s+from\s+[\'\"`]lucide-react[\'\"`];')
    match = import_pattern.search(content)
    if not match:
        continue

    imported_str = match.group(1)
    # Extract all imported icon names
    icons = [i.strip() for i in imported_str.replace('\n', '').split(',') if i.strip()]

    # Find which ones are actually used in the rest of the file
    content_without_import = content[:match.start()] + content[match.end():]
    
    used_icons = []
    for icon in icons:
        # A simple check: if the word appears with word boundaries
        if re.search(r'\b' + icon + r'\b', content_without_import):
            used_icons.append(icon)

    # Reconstruct the import
    if used_icons:
        new_import = f"import {{ {', '.join(used_icons)} }} from 'lucide-react';"
    else:
        new_import = ''

    new_content = content[:match.start()] + new_import + content[match.end():]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Fixed {file_path}. Used {len(used_icons)} out of {len(icons)}.')
