import re
from collections import Counter
from pprint import pprint

def get_lines_with_imports_from_file(file_name):
    """For a given file, create a list of file lines that contain the word 'import'"""
    with open(file_name) as my_file:
        lines_with_imports = []
        
        all_lines = my_file.readlines()
        
        for line in all_lines:
            words = line.split()
            
            if 'import' in words:
                lines_with_imports.append(line)
        
        return lines_with_imports

def parse_imports_from_lines_with_imports(lines_with_imports: 'list of lines with imports'):
    """By line, search for phrases that follow the word 'import' and create one list containing all such phrases."""
    all_imports = []

    for line in lines_with_imports:
        words = line.split(' ')
        words = [word.replace('\n', '') for word in words]
        words = [word.replace(',', '') for word in words]
        
        try:
            import_index = words.index('import')
            imports = words[import_index + 1:]
            
            try:
                as_index = imports.index('as')
                imports = imports[as_index + 1:]
            except:
                pass
            
            all_imports.extend(imports)

        except:
            pass

    return all_imports

def parse_file_into_phrases(file_name):
    """For a given file, use RegEx to parse all phrases in the file into a list"""
    with open(file_name) as my_file:
        text_to_search = my_file.read()

        pattern = re.compile(r'\b[\w]+\b')
        matches = pattern.finditer(text_to_search)
        
        all_phrases = [match.group() for match in matches]
        return all_phrases

def get_sorted_count_totals(phrases: 'list of phrases', subset=None):
    """For a list of phrases, get count totals for each phrase as a list of tuples. With the optional subset parameter,  you can specify which phrases you want consider."""
    counts = Counter(phrases)
    counts = [(key,value) for (key, value) in counts.items() if key in subset]
    sorted_counts = sorted(counts, key=lambda item: item[1], reverse=True)
    return sorted_counts

def get_imports_for_python_file(file_name):
    """For a Python file, return a list of imports included in the file (usually but not necessarily at the top of the file)"""
    lines_with_imports = get_lines_with_imports_from_file(file_name)
    imports = parse_imports_from_lines_with_imports(lines_with_imports)
    return imports

def get_import_count_totals(file_name):
    """Get the count totals for the imports in a Python file"""
    file_phrases = parse_file_into_phrases(file_name)
    imports = get_imports_for_python_file(file_name)
    
    sorted_count_totals = get_sorted_count_totals(phrases=file_phrases, subset=imports)
    return sorted_count_totals

def pretty_print_import_count_totals(file_name):
    """Pretty print the count totals for the imports in a Python file. This will be used to check for imports that are not in fact used in the file and can be deleted."""
    sorted_count_totals = get_import_count_totals(file_name)
    pprint(sorted_count_totals)

file_name = '/Users/paulwainer/Paulthon/utility/finance.py'
pretty_print_import_count_totals(file_name)
