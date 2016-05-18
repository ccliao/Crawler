from gensim.corpora import WikiCorpus
inp = 'zhwiki-20160501-pages-articles-multistream.xml.bz2'

i=0
output = open('wiki.csv', 'w')
wiki = WikiCorpus(inp, lemmatize=False, dictionary={})
for text in wiki.get_texts():
    output.write(' '.join(str(text)) + "\n")
    i = i + 1
    if (i % 10000 == 0):
        print ("Saved " + str(i) + " articles")

output.close()
print ("Finished Saved " + str(i) + " articles")