import json, csv

with open('words.json.completed.json', 'r') as jsonFile, open('flashcards.csv', 'w') as csvFile:
	words = json.load(jsonFile)['words']
	for word in words:
		csvFile.write(', '.join([word.encode('utf-8'),  '; '.join([x.encode('utf-8') for x in words[word]['def']]).replace(',', '--')]))
		csvFile.write('\n')
