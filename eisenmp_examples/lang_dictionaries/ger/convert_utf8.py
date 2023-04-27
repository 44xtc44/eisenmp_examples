path_in = r'/home/osboxes/PycharmProjects/eisenmp_examples/eisenmp_examples/lang_dictionaries/ger/german.dic'
path_out = r'/home/osboxes/PycharmProjects/eisenmp_examples/eisenmp_examples/lang_dictionaries/ger/german_utf8.dic'
with open(path_in, 'r', encoding='cp1252') as reader:
    words = reader.read()

print(len(words))

with open(path_out, 'w', encoding='utf-8') as writer:
    writer.write(words)
