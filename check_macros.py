import re
import os

def get_defined_macros(macros_file_path):
    with open(macros_file_path, 'r') as f:
        content = f.read()

    # Regex patterns to find definitions
    # \newcommand{\cmd}
    # \renewcommand{\cmd}
    # \providecommand{\cmd}
    # \DeclareMathOperator{\cmd}
    # \DeclareMathOperator*{\cmd}
    # \def\cmd
    
    # We will look for anything that looks like a command definition and extract the name
    
    defined_macros = set()
    
    # Matches \newcommand{\xyz} or \renewcommand{\xyz} etc.
    # Group 2 will be the command name without backslash if it's inside curly braces
    # Patterns:
    # 1. \newcommand{\name}
    # 2. \newcommand\name
    
    # Pattern for \newcommand{\name}
    p1 = r'\\(?:newcommand|renewcommand|providecommand|DeclareMathOperator\*?)\s*\{\\([a-zA-Z0-9]+)\}'
    matches = re.finditer(p1, content)
    for m in matches:
        defined_macros.add(m.group(1))

    # Pattern for \newcommand\name
    p2 = r'\\(?:newcommand|renewcommand|providecommand|DeclareMathOperator\*?)\s*\\([a-zA-Z0-9]+)\b'
    matches = re.finditer(p2, content)
    for m in matches:
        defined_macros.add(m.group(1))
        
    # \def\name
    p3 = r'\\def\s*\\([a-zA-Z0-9]+)'
    matches = re.finditer(p3, content)
    for m in matches:
        defined_macros.add(m.group(1))

    # \newtheorem{name}
    p4 = r'\\newtheorem\s*\{([a-zA-Z0-9]+)\}'
    matches = re.finditer(p4, content)
    for m in matches:
        defined_macros.add(m.group(1))
        
    # \newenvironment{name} - creates Environment and endEnvironment usually, but usage is \begin{name}
    p5 = r'\\newenvironment\s*\{([a-zA-Z0-9]+)\}'
    matches = re.finditer(p5, content)
    for m in matches:
        defined_macros.add(m.group(1)) # We check for \begin{name} or \end{name}

    return defined_macros

def check_usage(defined_macros, files_to_check):
    used_macros = set()
    
    content = ""
    for file_path in files_to_check:
        with open(file_path, 'r') as f:
            content += f.read() + "\n"
            
    # Naive check: just look for the string
    # For commands: look for \name
    # For environments: look for {name} (as in \begin{name})
    
    for macro in defined_macros:
        # Construct regex to be slightly safer than 'in'
        # Check for command usage: \name inside the text
        # Or if it is an environment name, it might appear in \begin{name}
        
        # We'll just checks if the literal "\macro" is present likely for commands
        # For simple names (like from newtheorem or newenvironment), we check for "macro" inside braces or just the word?
        # Actually environments are usually \begin{env}. Theorems are \begin{thm}.
        
        # Let's try to be specific.
        # If it was defined via newtheorem or newenvironment, we look for "begin{macro}"
        
        # But my get_defined_macros didn't distinguish types.
        # Let's just look for the string in the file, but careful about substring matching.
        # However, for LaTeX, "\name" is specific enough.
        # But "name" (environment) is harder.
        
        # Heuristic:
        # If "\macro" is in content -> Used.
        # If "{macro}" is in content (for environments) -> Used.
        
        is_used = False
        
        if f"\\{macro}" in content:
            is_used = True
        elif f"{{{macro}}}" in content: # For environments/theorems \begin{macro}
             is_used = True
        
        if is_used:
            used_macros.add(macro)
            
    return used_macros

macros_file = '/Users/u1774790/Projects/Pfaffian/macros.tex'
tex_files = [
    '/Users/u1774790/Projects/Pfaffian/main.tex',
    '/Users/u1774790/Projects/Pfaffian/sections/introduction.tex',
    '/Users/u1774790/Projects/Pfaffian/sections/preliminaries.tex',
    '/Users/u1774790/Projects/Pfaffian/sections/robustness.tex',
    '/Users/u1774790/Projects/Pfaffian/sections/tubular-singular.tex',
    '/Users/u1774790/Projects/Pfaffian/sections/tubular.tex'
]

# We should NOT check usage in macros.tex itself, or self-definitions will count as usage?
# No, we want to see if they are used OUTSIDE of definitions. 
# But some macros might use other macros.
# So we should include macros.tex in the "usage check" but we need to be careful not to count the definition line as usage.
# But for safety, let's include macros.tex in the usage check, because if macro A uses macro B, and A is used in main.tex, then B is effectively used.
# If A is NOT used in main.tex, then B might be "used" by A, but seemingly A is dead code.
# This implies a dependency graph. That's too complex.
# 
# Simpler approach:
# 1. Check usage in non-macros files.
# 2. Iterate used set to see if they use other macros in macros.tex.
# 
# Let's just check usage in the PROJECT files (excluding macros.tex first).
# Then we can manually review the "unused" list to see if they are dependencies of utilized macros. 

defined = get_defined_macros(macros_file)
used = check_usage(defined, tex_files)

unused = defined - used

print("Unused macros:")
for m in sorted(unused):
    print(m)
