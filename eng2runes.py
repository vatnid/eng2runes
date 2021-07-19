from collections import defaultdict
import re

# convert word from latin to runes
def latin2runes(word):
	l2r = {"a": "ᚫ", "å": "ᚪ", "b": "ᛒ", "c": "ᚳ", "d": "ᛞ", "ð": "ᚧ", "e": "ᛖ", "f": "ᚠ", "g": "ᚸ", "h": "ᚻ", "i": "ᛁ", "j": "ᚷ", "k": "ᛣ", "l": "ᛚ", "m": "ᛗ", "n": "ᚾ", "ŋ": "ᛝ", "o": "ᚩ", "p": "ᛈ", "q": "ᚢ", "r": "ᚱ", "s": "ᛋ", "t": "ᛏ", "u": "ᛇ", "v": "ᚥ", "w": "ᚹ", "ʷ": "ᚹ", "x": "ᛋᚳ", "y": "ᛄ", "ʸ": "ᛄ", "z": "ᛉ", "þ": "ᚦ", "́": "̇", "̇": "§", "'": ""}

	runes = ""
	for c in word:
		runes += l2r[c]

	return re.sub(r"ᚢ§", r"ᚤ", runes)

# read dictionary
dictionary = defaultdict(list)
with open(f"dictionary.txt", "r", encoding = "utf-8") as f:
	for line in f:
		entry = line.strip()
		word = entry.split("\t")[0]
		transcription = latin2runes(entry.split("\t")[1])
		if len(word.split()) > 1:
			word = word.split()[0]
		dictionary[word].append(transcription)


def lookup(in_text, dictionary):
	out_text = []
	words = in_text.split()


	prefixes = ["under", "over", "non-", "non", "un"]
	d_suffixes = ["abilities", "ability", "able", "ingly", "ings", "ing", "ers", "er", "est", "edly", "eds", "ed"] # doubling
	nd_suffixes = ["lessnesses", "lessness", "lessly", "less", "nesses", "ness", "ly", "es", "'s", "s"] # non-doubling

	prefix_pron = {"under": "ᛇᚾᛞᛖᚱ", "over": "ᚩ̇ᚢᛖᚱ", "non-": "ᚾᚩᚾ", "non": "ᚾᚩᚾ", "un": "ᛇᚾ"}
	suffix_pron = {"lessnesses": "ᛚᛖᛋᚾᛖᛋᛖᛉ", "lessness": "ᛚᛖᛋᚾᛖᛋ", "lessly": "ᛚᛖᛋᛚᛖ̇", "less": "ᛚᛖᛋ", "nesses": "ᚾᛖᛋᛖᛉ", "ness": "ᚾᛖᛋ", "abilities": "ᚫᛒᛁᛚᛁᛏᛖ̇ᛉ", "ability": "ᚫᛒᛁᛚᛁᛏᛖ̇", "able": "ᚫᛒᛖᛚ", "ingly": "ᛁᛝᛚᛖ̇", "ings": "ᛁᛝᛉ", "ing": "ᛁᛝ", "ers": "ᛖᚱᛉ", "er": "ᛖᚱ", "est": "ᛖᛋᛏ", "es": "ᛖᛉ"}

	suffixes = d_suffixes + nd_suffixes

	for word in words:
		if word in dictionary:
			out_text.append("/".join(pron for pron in dictionary[word]))

		# prefixes and suffixes
		elif word.startswith(tuple(prefixes)) or word.endswith(tuple(suffixes)):
			stem = word
			prefix = ""
			suffix = ""

			for p in prefixes:
				if stem.startswith(p):
					prefix = stem[:len(p)]
					stem = stem[len(p):]
					break

			for s in suffixes:
				if stem.endswith(s):
					if s == "'s":
						suffix = "s"
					else:
						suffix = stem[-len(s):]

					stem = stem[:-len(s)]

					# -(i)es
					if s == "es":
						# disambiguate -e#s and -es
						if stem + "e" in dictionary:
							stem = stem + "e"
							suffix = "s"
							break
						# ies
						elif stem.endswith("i") and stem[:-1]+"y" in dictionary:
							suffix = "s"
							stem = stem[:-1]+"y"
							break

					# -(i)ly
					elif s == "ly":
						if stem.endswith("i") and stem[:-1]+"y" in dictionary:
							stem = stem[:-1]+"y"
							break

					elif s in d_suffixes:
						if stem + "e" in dictionary:
							stem = stem + "e"
						elif (stem.endswith("ck") or stem[-1] == stem[-2]) and stem[:-1] in dictionary:
							stem = stem[:-1]
						# e.g. lie --> lying
						if s in ["ingly", "ings", "ing"]:
							if stem.endswith("y") and stem[:-1]+"ie" in dictionary:
								stem = stem[:-1]+"ie"
						# -i --> -y
						elif s in ["ers", "er", "est", "edly", "eds", "ed"]:
							if stem.endswith("i") and stem[:-1]+"y" in dictionary:
								stem = stem[:-1]+"y"

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
						if dictionary[stem][0][-1] in "ᛞᛏ":
							suffix = "ᛖᛞ"
						elif dictionary[stem][0][-1] in "ᚳᚠᚻᛣᛈᛋᚦ":
							suffix = "ᛏ"
						else:
							suffix = "ᛞ"
					elif suffix in ["'s", "s"]:
						if dictionary[stem][0][-1] in "ᚳᚷᛋᛉ":
							suffix = "ᛖᛉ"
						elif dictionary[stem][0][-1] in "ᚠᚻᛣᛈᛏᚦ":
							suffix = "ᛋ"
						else:
							suffix = "ᛉ"
					elif suffix == "ly":
						if dictionary[stem][0][-1] == "ᛚ":
							suffix = "ᛖ̇"
						else:
							suffix = "ᛚᛖ̇"

				out_text.append("/".join(prefix+pron+suffix for pron in dictionary[stem]))

		# no match in dictionary
		else:
			out_text.append(word)
	

	return " ".join(word for word in out_text)


in_text = input("Input English: ")
print(lookup(in_text.lower().strip(), dictionary))
print("END")