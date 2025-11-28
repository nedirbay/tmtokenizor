from tokenizers import Tokenizer
tokenizer = Tokenizer.from_file("turkmen_hf_tokenizer.json")
encoded = tokenizer.encode("Men mekdepde okaýaryn")
print(encoded.tokens)