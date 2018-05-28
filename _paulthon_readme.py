with open('PAULTHON_README.txt', 'r') as f:
    text = f.read()

text = text.splitlines()
text = [i for i in text if i != '']
text = [i for i in text if i[0] != ' ']

for i in range(len(text)):
    if text[i][-1] == ':':
        text[i] = text[i][:-1]
    print(text[i])

