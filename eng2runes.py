from collections import defaultdict
import re
import sys
from nltk import pos_tag as pos
#from nltk.tokenize.treebank import TreebankWordTokenizer
#from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.tokenize import RegexpTokenizer

# convert word from latin to runes
def latin2runes(word):
	l2r = {"a": "ᚫ", "å": "ᚪ", "b": "ᛒ", "c": "ᚳ", "d": "ᛞ", "ð": "ᚧ", "e": "ᛖ", "f": "ᚠ", "g": "ᚸ", "h": "ᚻ", "i": "ᛁ", "j": "ᚷ", "k": "ᛣ", "l": "ᛚ", "m": "ᛗ", "n": "ᚾ", "ŋ": "ᛝ", "o": "ᚩ", "p": "ᛈ", "q": "ᚢ", "r": "ᚱ", "s": "ᛋ", "t": "ᛏ", "u": "ᛇ", "v": "ᚥ", "w": "ᚹ", "ʷ": "ᚹ", "x": "ᛋᚳ", "y": "ᛄ", "ʸ": "ᛄ", "z": "ᛉ", "þ": "ᚦ", "́": "̇", "̇": "§", "'": ""}

	runes = ""
	for c in word:
		runes += l2r[c]

	return re.sub(r"ᚢ§", r"ᚤ", runes)

# read dictionary
#dictionary = defaultdict(list)
dictionary = {}
with open(f"dictionary.txt", "r", encoding = "utf-8") as f:
	for line in f:
		entry = line.strip()
		word = entry.split("\t")[0]
		transcription = latin2runes(entry.split("\t")[1])
		#if len(word.split()) > 1:
		#	word = word.split()[0]
		dictionary[word] = transcription


def lookup(in_text, dictionary):
	out_text = []
	tokenizer = RegexpTokenizer(r"\w+(?:'\w+)?|[^\w\s]")
	words = tokenizer.tokenize(in_text)

	tagged_words = pos(words)

	print(f"Tagged words: {tagged_words}")


	dict_words = [k.split()[0] for k in dictionary.keys()]


	prefixes = ["under", "over", "non-", "non", "un"]
	d_suffixes = ["ed", "eds", "er", "ers", "est", "edly", "ing", "ings", "ingly", "able", "ability", "abilities"] # doubling
	nd_suffixes = ["s", "'s", "es", "ly", "ness", "nesses", "less", "lessly", "lessness", "lessnesses"] # non-doubling

	prefix_pron = {"under": "ᛇᚾᛞᛖᚱ", "over": "ᚩ̇ᚢᛖᚱ", "non-": "ᚾᚩᚾ", "non": "ᚾᚩᚾ", "un": "ᛇᚾ"}
	suffix_pron = {"lessnesses": "ᛚᛖᛋᚾᛖᛋᛖᛉ", "lessness": "ᛚᛖᛋᚾᛖᛋ", "lessly": "ᛚᛖᛋᛚᛖ̇", "less": "ᛚᛖᛋ", "nesses": "ᚾᛖᛋᛖᛉ", "ness": "ᚾᛖᛋ", "abilities": "ᚫᛒᛁᛚᛁᛏᛖ̇ᛉ", "ability": "ᚫᛒᛁᛚᛁᛏᛖ̇", "able": "ᚫᛒᛖᛚ", "ingly": "ᛁᛝᛚᛖ̇", "ings": "ᛁᛝᛉ", "ing": "ᛁᛝ", "ers": "ᛖᚱᛉ", "er": "ᛖᚱ", "est": "ᛖᛋᛏ", "es": "ᛖᛉ"}

	suffixes = d_suffixes + nd_suffixes
	suffixes.sort()
	suffixes.sort(key=len, reverse=True)

	cons = "bcdfghjklmnpqrstvwxz"

	adjs = ["JJ", "JJR", "JJS"]
	nouns = ["NN", "NNS", "NNP", "NNPS"]
	verbs = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]

	for word, tag in tagged_words:
		if word in ",.!?:;" or word in ["-LRB-", "-RRB-"]:
			out_text.append(word)
			continue

		if word in dictionary:
			out_text.append(dictionary[word])
			continue
			#out_text.append("/".join(pron for pron in dictionary[word]))
		
		if tag in adjs and word+" adj" in dictionary:
			out_text.append(dictionary[word+" adj"])
			continue
		elif tag in nouns and word+" n" in dictionary:
			out_text.append(dictionary[word+" n"])
			continue
		elif tag in verbs and word+" v" in dictionary:
			out_text.append(dictionary[word+" v"])
			continue
		elif tag == "VBP" and word+" (pres)" in dictionary:
			out_text.append(dictionary[word+" (pres)"])
			continue
		elif tag in ["VBD", "VBN"] and word+" (past)" in dictionary:
			out_text.append(dictionary[word+" (past)"])
			continue

		# prefixes and suffixes
		if word.startswith(tuple(prefixes)) or word.endswith(tuple(suffixes)):
			stem = word
			prefix = ""
			suffix = ""

			for p in prefixes:
				if stem.startswith(p):
					prefix = stem[:len(p)]
					stem = stem[len(p):]
					break

			print(suffixes)
			for s in suffixes:
				if stem.endswith(s):

					print(f"Current suffix: {s}")

					if s == "'s":
						suffix = "s"
					else:
						suffix = stem[-len(s):]

					stem = stem[:-len(s)]

					print(f"STEM: {stem}")

					# -(i)es
					if s == "es":
						# disambiguate -e#s and -es
						if stem + "e" in dictionary:
							stem = stem + "e"
							suffix = "s"
						# ies
						elif stem.endswith("i") and stem[:-1]+"y" in dictionary:
							suffix = "s"
							stem = stem[:-1]+"y"

					# -(i)ly
					elif s == "ly":
						if stem.endswith("i") and stem[:-1]+"y" in dictionary:
							stem = stem[:-1]+"y"

					elif s in d_suffixes:
						if stem.endswith(tuple(cons)):
							if stem + "e" in dictionary:
								stem = stem + "e"
							elif len(stem) >=2 and (stem.endswith("ck") or stem[-1] == stem[-2]) and stem[:-1] in dictionary:
								stem = stem[:-1]

						# e.g. lie --> lying
						if s in ["ingly", "ings", "ing"]:
							if stem.endswith("y") and stem[:-1]+"ie" in dictionary:
								stem = stem[:-1]+"ie"
						# -i --> -y
						elif s in ["ers", "er", "est", "edly", "eds", "ed"]:
							if stem.endswith("i") and stem[:-1]+"y" in dictionary:
								stem = stem[:-1]+"y"

					if stem in dict_words:
						break
					else:
						stem += s
						continue

			# debug
			structure = ""
			if prefix != "":
				structure += prefix + "-"
			structure += stem.upper()
			if suffix != "":
				structure += "-" + suffix
			print(f"Structure: {structure}")

			# if stem not found
			if stem not in dictionary:
				out_text.append(prefix+stem+suffix)

			else:
				if prefix in prefix_pron:
					prefix = prefix_pron[prefix]

				if suffix in suffix_pron:
					suffix = suffix_pron[suffix]
				# phonological rules for -ed and -s
				else:
					if suffix in ["edly", "eds", "ed"]:
						if dictionary[stem][-1] in "ᛞᛏ":
							suffix = "ᛖᛞ"
						elif dictionary[stem][-1] in "ᚳᚠᚻᛣᛈᛋᚦ":
							suffix = "ᛏ"
						else:
							suffix = "ᛞ"
					elif suffix in ["'s", "s"]:
						if dictionary[stem][-1] in "ᚳᚷᛋᛉ":
							suffix = "ᛖᛉ"
						elif dictionary[stem][-1] in "ᚠᚻᛣᛈᛏᚦ":
							suffix = "ᛋ"
						else:
							suffix = "ᛉ"
					elif suffix == "ly":
						if dictionary[stem][-1] == "ᛚ":
							suffix = "ᛖ̇"
						else:
							suffix = "ᛚᛖ̇"

				#out_text.append("/".join(prefix+pron+suffix for pron in dictionary[stem]))
				out_text.append(prefix+dictionary[stem]+suffix)


		# no match in dictionary
		else:
			out_text.append(word)
	
	print(out_text)

	output = " ".join(out_text)
	output = re.sub(r" - ", r"-", output)
	output = re.sub(r"\( ", r"(", output)
	output = re.sub(r" ([,.:;!\?\)])", r"\1", output)
	output = re.sub(r"\s\s+", r" ", output)

	return output


if len(sys.argv) > 1:
	output_runes = []
	filename = sys.argv[1]
	if not filename.endswith(".txt"):
		print("Please use a .txt file!")
	else:
		with open(filename, "r") as f:
			for line in f:
				output_runes.append(lookup(line.lower().strip(), dictionary))
		with open(f"{filename[:-4]}_converted.txt", "w") as f:
			f.write("\n".join(output_runes))
		print(f"Printed output to {filename[:-4]}_converted.txt")
else:
	in_text = input("Input English: ")
	print(lookup(in_text.lower().strip(), dictionary))

