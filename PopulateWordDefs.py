import json
from wordnik import *
import time
import os

valid_parts_of_speech = set(['noun', 'adjective', 'verb', 'adverb', 'preposition'])

def log(message):
	print message

class DefinitionGetter:
	def __init__(self, apiKey, apiUrl):
		self.client = swagger.ApiClient(apiKey, apiUrl)
		self.WordApi = WordApi.WordApi(self.client)

	def GetDefinitions(self, word, partOfSpeech = None):
		if word == '':
			return ["no definitions found!"]
		total_time = 1   # seconds
		start_time = time.time()
		log('looking up {}, {}.'.format(word, partOfSpeech))
		returnObject = self.WordApi.getDefinitions(word, partOfSpeech = partOfSpeech)
		end_time = time.time()

		# make sure we're not calling the API too quickly. We don't want to anger the API.
		if end_time - start_time < total_time:
			sleep_time = total_time - (end_time - start_time)
			time.sleep(sleep_time)
			log( "slept for {} seconds!".format(sleep_time))
		if not returnObject:
			return ["No definitions found!"]
		else:
			return [definition.text for definition in returnObject]

# Get API credentials from file, hidden from git repo because they're mine.
with open('api_credentials.json', 'r') as credentials_file:
	credentials_dict = json.load(credentials_file)

apiKey, apiUrl = credentials_dict['apiKey'], credentials_dict['apiUrl']
oDefinitionGetter = DefinitionGetter(apiKey, apiUrl)

raw_file_name = 'words_raw.txt'
json_file_name = 'words.json'

# If no json file exists, make an empty one.
if not json_file_name in os.listdir(os.getcwd()):
	with open(json_file_name, 'w') as JsonFile:
		json.dump({'words':{}}, JsonFile)
		log("made a new json file.")

# Read raw words file and filled-out words file. For each word in raw file,
# if it is not in the JSON, add it, initializing the definition to None.
with open(raw_file_name, 'r') as RawFile, open(json_file_name, 'r') as JsonFile:
	lAllWords = set([line.strip() for line in RawFile])
	Json = json.load(JsonFile)
	for wordline in lAllWords:
		split_combo = wordline.split(',')
		word = split_combo[0].strip()
		partOfSpeech = None
		if len(split_combo) == 1:
			pass
		elif len(split_combo) == 2:
			partOfSpeech = split_combo[1].strip()
			if partOfSpeech == '':
				partOfSpeech = None
			elif partOfSpeech not in valid_parts_of_speech:
				raise BaseException('invalid part of speech! "{}"'.format(partOfSpeech))
		else:
			raise BaseException('more than one comma!:"{}"'.format(wordline))
		if word not in Json['words']:
			log('"{}" not in Json["words"]'.format(word))
			Json['words'][word] = {'def':None, 'partOfSpeech':partOfSpeech}
	log("finished reading raw words file and copying to json file.")

# dump json to file.
with open(json_file_name, 'w') as JsonFile:
	json.dump(Json, JsonFile)

# Write all words in sorted order to a new file.
with open(raw_file_name + '.sorted', 'w') as RawFileSorted:
	for word in sorted(lAllWords):
		RawFileSorted.write(word)
		RawFileSorted.write('\n')
	log("finished writing all words in sorted order to new file")

# For any word in the json without a definition, try pulling its definition.
json_words = Json['words']
for word in json_words:
	if json_words[word]['def'] == None:
		json_words[word]['def'] = oDefinitionGetter.GetDefinitions(word, 
			partOfSpeech = json_words[word]["partOfSpeech"])
	log('got definition for "{}". it was of length {}.'.format(word, len(json_words[word]['def'])))
	with open(json_file_name, 'w') as JsonFile:
		json.dump(Json, JsonFile)

# copy json to a special write-only file just to be safe.
with open(json_file_name + '.completed.json', 'w') as JsonFile:
	json.dump(Json, JsonFile)

