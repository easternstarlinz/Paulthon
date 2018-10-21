import re
from collections import Counter
from pprint import pprint

# Create list of all imports based on imports.txt phrase
def get_lines_with_imports_from_file(file_name):
    """Create alist of lines that contain the word 'import'"""
    with open(file_name) as my_file:
        lines_with_imports = []
        
        lines = my_file.readlines()
        
        for line in lines:
            words = line.split()
            if 'import' in words:
                lines_with_imports.append(line)
        
        return lines_with_imports

def parse_imports_from_lines_with_imports(lines_with_imports):
    """Create list of imports by searching by line, words that come after 'import'"""
    all_imports = []

    for line in lines_with_imports:
        words = line.split(' ')
        
        try:
            import_index = words.index('import')
            
            imports = words[import_index + 1:]
            imports = [word.replace('\n', '') for word in imports]
            imports = [word.replace(',', '') for word in imports]
            imports = [word for word in imports if word not in {'as'}]
            
            all_imports.extend(imports)

        except:
            pass

    return all_imports

def create_vim_search_string(phrases: 'list of imports'):
    """Create string to use for multiple search criteria in Vim"""
    search_string = '/\\v'

    for word in phrases[:-1]:
        search_string += word + '|'

    search_string += phrases[-1]
    return search_string

# Create list of all phrases in the file
def parse_file_into_phrases(file_name):
    """Use RegEx to parse all phrases in the file into a list"""
    with open(file_name) as my_file:
        text_to_search = my_file.read()

        pattern = re.compile(r'\b\w+\b')
        matches = pattern.finditer(text_to_search)
        
        all_phrases = [match.group() for match in matches]
        return all_phrases

def get_sorted_count_totals(phrases, subset=None):
    counts = Counter(phrases)
    counts = [(key,value) for (key, value) in counts.items() if key in subset]
    sorted_counts = sorted(counts, key=lambda item: item[1], reverse=True)
    return sorted_counts
   


file_name = 'GetVolMC.py'

#print(search_string)

def get_imports_for_python_file(file_name):
    lines_with_imports = get_lines_with_imports_from_file(file_name)
    imports = parse_imports_from_lines_with_imports(lines_with_imports)
    return imports

def get_search_string_for_python_imports(file_name):
    imports = get_imports_for_python_file(file_name):
    search_string = create_vim_search_string(imports)
    return search_string

def get_search_string_for_python_imports(file_name):
    lines_with_imports = get_lines_with_imports_from_file(file_name)
    imports = parse_imports_from_lines_with_imports(lines_with_imports)
    search_string = create_vim_search_string(imports)
    return search_string

def pretty_print_import_count_totals(file_name):
    lines_with_imports = get_lines_with_imports_from_file(file_name)
    imports = parse_imports_from_lines_with_imports(lines_with_imports)
    
    file_phrases = parse_file_into_phrases(file_name)
    sorted_count_totals = get_sorted_count_totals(phrases=file_phrases, subset=imports)
    pprint(sorted_count_totals)
    return sorted_count_totals

sorted_count_totals = pretty_print_import_count_totals('GetVolMC.py')
