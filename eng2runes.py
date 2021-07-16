from collections import defaultdict
import re

# convert word from latin to runes
def latin2runes(word):
	l2r = {"a": "ᚫ", "å": "ᚪ", "b": "ᛒ", "c": "ᚳ", "d": "ᛞ", "ð": "ᚧ", "e": "ᛖ", "f": "ᚠ", "g": "ᚸ", "h": "ᚻ", "i": "ᛁ", "j": "ᚷ", "k": "ᛣ", "l": "ᛚ", "m": "ᛗ", "n": "ᚾ", "ŋ": "ᛝ", "o": "ᚩ", "p": "ᛈ", "q": "ᚢ", "r": "ᚱ", "s": "ᛋ", "t": "ᛏ", "u": "ᛇ", "v": "ᚡ", "w": "ᚹ", "ʷ": "ᚹ", "x": "ᛋᚳ", "y": "ᛄ", "ʸ": "ᛄ", "z": "ᛉ", "þ": "ᚦ", "́": "̇", "̇": "˙"}

	runes = ""
	for c in word:
		if c == "̇":
			continue
		runes += l2r[c]

	return re.sub(r"ᚢ", r"ᚤ", runes)


def lookup(in_text, dictionary):
	out_text = []
	words = in_text.split()

	prefixes = ["under", "over", "non-", "non", "un"]
	d_suffixes = ["ing", "er", "est", "ed"] # doubling
	nd_suffixes = ["ly", "es", "'s", "s"] # non-doubling

	suffixes = d_suffixes + nd_suffixes

	for word in words:
		if word in dictionary:
			out_text.append("/".join(pron for pron in dictionary[word]))

		# prefixes and suffixes
		elif word.startswith(tuple(prefixes)) or word.endswith(tuple(suffixes)):
			stem = word
			prefix = ""
			suffix = ""
			if stem.startswith(tuple(prefixes)):
				for p in prefixes:
					if stem.startswith(p):
						prefix = stem[:len(p)]
						stem = stem[len(p):]
						break

			if stem.endswith(tuple(suffixes)):
				for s in suffixes:
					if stem.endswith(s):
						if s == "'s":
							suffix = "s"
						else:
							suffix = stem[-len(s):]
						stem = stem[:-len(s)]
						# -ies
						if s == "es" and stem.endswith("i") and stem[:-1]+"y" in dictionary:
							suffix = "s"
							stem = stem[:-1]+"y"
							break
						elif s in d_suffixes:
							if stem + "e" in dictionary:
								stem = stem + "e"
							elif (stem.endswith("ck") or stem[-1] == stem[-2]) and stem[:-1] in dictionary:
								stem = stem[:-1]
							if s in ["er", "est", "ed"]:
								if stem.endswith("i") and stem[:-1]+"y" in dictionary:
									stem = stem[:-1]+"y"

			if stem not in dictionary:
				out_text.append(prefix+stem+suffix)
			else:
				out_text.append("/".join(prefix+pron+suffix for pron in dictionary[stem]))

			#print(f"prefix: {prefix}\nsuffix: {suffix}\nstem: {stem}")

		# no match in dictionary
		else:
			out_text.append(word)
	

	return " ".join(word for word in out_text)


# read dictionary
dictionary = defaultdict(list)
with open(f"dictionary.txt", "r") as f:
	for line in f:
		entry = line.strip()
		dictionary[entry.split("\t")[0]].append(latin2runes(entry.split("\t")[1]))


in_text = input("Input English: ")
print(f"{lookup(in_text.lower().strip(), dictionary)}")
print("END")