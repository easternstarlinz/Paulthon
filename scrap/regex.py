import re

# MetaCharacters (Need to be escaped):
# .^$*+?{}[]\|()

print(r'\tTab')

text_to_search = 'Hi my name is Paul. My favorite tennis player is Roger Federer.'

pattern = re.compile(r'\.')

matches = pattern.finditer(text_to_search)

for match in matches:
    print(match)


