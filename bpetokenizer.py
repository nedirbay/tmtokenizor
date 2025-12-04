"""
Türkmen Dili üçin BPE (Byte Pair Encoding) Tokenizer
Grammatik düzümleri, adaty atlary we geografik atlary göz öňünde tutýar
"""

import re
import json
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Set
import unicodedata

class TurkmenBPETokenizer:
    def __init__(self, vocab_size: int = 10000):
        self.vocab_size = vocab_size
        self.vocab = {}
        self.merges = []
        self.word_freqs = {}
        
        # Türkmen diliniň aýratyn harplary
        self.turkmen_chars = set('äňöşüýžç')
        
        # Türkmen erkek atlary
        self.male_names = {
            'ahmet', 'muhammet', 'döwlet', 'berdi', 'gurban', 'oraz', 'serdar',
            'atamyrat', 'baýram', 'gurbanguly', 'görogly', 'käkä', 'magtymguly',
            'oguz', 'saparmyrat', 'täçmyrat', 'wepa', 'ýagmyr', 'ýolaman',
            'merdan', 'rustam', 'nurmuhammet', 'kerim', 'jumamyrat', 'annamuhammet',
            'sapar', 'rejep', 'amanmyrat', 'myrat', 'guwanç', 'arslan',
            'batyr', 'gökhan', 'hudaýberdi', 'mämmet', 'nazim', 'şöhrat',
            'ýagşy', 'ýusup', 'ýusupmyrat', 'ýusupguly', 'ýusupgurly',
            'anna', 'muhammetmyrat', 'muhammetguly', 'muhammetnur', 'muhammetöwez',
            'muhammetrahman', 'muhammetserdar', 'muhammettaýly', 'muhammetýusup',
            'myrat', 'nurmyrat', 'öwezmyrat', 'rahmanmyrat', 'serdarmyrat', 'täçmyrat',
            'taýlymyrat', 'annamyrat', 'amanmyrat', 'gurbangulymyrat', 'guwançmyrat',
            'hudaýberdimyrat', 'kerimmyrat', 'nazimmyrat', 'rejepmyrat', 'saparmyrat',
            'şöhratmyrat', 'wepamyrat', 'ýagşymyrat', 'ýusupmyrat', 'ýusupgulymyrat',
        }
        
        # Türkmen zenan atlary
        self.female_names = {
            'aýna', 'oguljan', 'mahri', 'jennet', 'güllü', 'günä', 'güzel',
            'lale', 'maýa', 'ogulnabat', 'sähet', 'soltan', 'aýgözel',
            'aýjemal', 'bibigül', 'bibi', 'gülbahar', 'gülnara', 'jahan',
            'leýla', 'maral', 'nazargül', 'rowaýat', 'şaýgül', 'täçgül',
            'ýyldyz', 'zeýnep', 'gülşat', 'mahym', 'ogulnaz'
        }
        
        self.regions = {
            'aşgabat', 'ahal', 'balkan', 'daşoguz', 'lebap', 'mary', 'arkadag'
        }
        # Türkmenistanyň şäherleri we welaýatlary
        self.cities = {
            # Paýtagt we Döwlet ähmiýetli şäherler
            'aşgabat', 'arkadag',
            
            # Welaýat merkezleri
            'anew', 'änew',             # Ahal
            'balkanabat', 'nebitdag',   # Balkan (Köne ady: Nebitdag)
            'daşoguz', 'daşhowuz',      # Daşoguz
            'türkmenabat', 'çärjew',    # Lebap (Köne ady: Çärjew)
            'mary',                     # Mary
            
            # Balkan welaýaty şäherleri
            'türkmenbaşy', 'krasnowodsk',
            'hazar', 'çeleken',
            'gumdag',
            'bereked', 'bereket', 'gazanjyk',
            'gyzylarbat', 'serdar',     # Serdar şäheriniň ady Gyzylarbat boldy, ýöne ikisem gerek
            'magtymguly', 'garrygala',
            
            # Daşoguz welaýaty şäherleri
            'köneürgenç',
            'akdepe',
            'boldumsaz',
            'gubadag',
            'görogly', 'tagta',
            
            # Lebap welaýaty şäherleri
            'kerki', 'atamyrat',        # Atamyrat ady ýatyryldy, ýöne tekstlerde köp
            'gazojak',
            'magdanly', 'gowurdak',
            'seýdi', 'neftezawodsk',
            'dänew', 'galkynyş',
            'darganata', 'birata',
            
            # Mary welaýaty şäherleri
            'baýramaly',
            'ýolöten',
            'murgap',
            'serhetabat', 'guşgy',
            'şatlyk',
            
            # Ahal welaýaty & Aşgabat düzümi (öňki şäherler)
            'tejen',
            'kaka', 'kaahka',
            'sarahs',
            'bäherden', 'baharly',
            'gökdepe',
            'abadan', 'büzmeýin',       # Häzir Aşgabadyň etraplary, ýöne şäher hökmünde duşýar
            'arçabil'
        }

        self.districts = {
            # --- Aşgabat şäheriniň etraplary ---
            'bagtyýarlyk',
            'berkararlyk',
            'büzmeýin',
            'köpetdag',
            # Ýatyrylan ýa-da birleşdirilen etraplar (taryhy tekstler üçin gerek)
            'arçabil', 'çandybil', 'abadan', 'ruhabat',

            # --- Arkadag şäheriniň etraplary ---
            'kyarizek', 'kärizek',
            'gorjaw',

            # --- Ahal welaýaty ---
            'ak bugdaý', 'akbugdaý',
            'babadaýhan',
            'bäherden', 'baharly',
            'gökdepe',
            'kaka', 'kaahka',
            'sarahs',
            'tejen',

            # --- Balkan welaýaty ---
            'bereket', 'gazanjyk',
            'etrek', 'gyzyletrek',
            'esenguly',
            'magtymguly', 'garrygala',
            'gyzylarbat', 'serdar',
            'türkmenbaşy',

            # --- Daşoguz welaýaty ---
            'akdepe',
            'boldumsaz',
            'görogly', 'tagta',
            'gubadag',
            'köneürgenç',
            'ruhubelent',
            's.a.nyýazow', 'nyýazow',
            'saparmyrat türkmenbaşy', 's.türkmenbaşy',

            # --- Lebap welaýaty ---
            'çärjew', 'serdarabat',     # Serdarabat etraby Çärjew boldy
            'darganata', 'birata',
            'dänew', 'galkynyş',
            'halaç',
            'hojambaz',
            'kerki', 'atamyrat',
            'köýtendag', 'çarşaňňy',
            'saýat',
            # Ýatyrylan ýa-da birleşen etraplar (tokenizer üçin saklamak peýdaly)
            'döwletli', 'farap', 'garashsyzlyk', 'garaşsyzlyk', 'sakar', 'beýik türkmenbaşy',

            # --- Mary welaýaty ---
            'baýramaly',
            'garagum',
            'mary',
            'murgap',
            'oguzhan', 'oguz han',
            'sakarçäge',
            'serhetabat', 'guşgy',
            'tagtabazar',
            'türkmengala',
            'wekilbazar',
            'ýolöten',
            # Ýatyrylanlar
            'altyn sähra'
        }
        
        # Geografik atlar (daşary ýurt)
        self.countries = {
            'türkiýe', 'eýran', 'russiýa', 'gazagystan', 'özbegistan',
            'täjigistan', 'owganystan', 'hytaý', 'hindistan', 'pakistan',
            'azerbaýjan', 'gyrgyzystan', 'germaniýa', 'fransiýa', 'angliýa',
            'amerika', 'kanada', 'braziliýa', 'awstraliýa', 'amerikanyň birleşen ştatlary'
        }
        
        # Beýleki möhüm sözler (ýokary ýygylykly)
        self.important_words = {
            'türkmenistan', 'türkmen', 'türkmenistanyň', 'türkmenleriň',
            'garaşsyzlyk', 'bitaraplyk', 'prezident', 'halk', 'watan',
            'döwlet', 'respublika', 'mejlis', 'ministr', 'ministrligi'
        }
        
        # Türkmen diliniň esasy goşulmalary (suffixes)
        self.common_suffixes = [
            # --- 4 Harp we uzynrak ---
            'laryň', 'leriň', 'syzlyk', 'sizlik', 'darlyk', 'derlik',
            'çylyk', 'çilik', 'kärlik', 'gerlik', 
            'jakdyr', 'jekdir', 'maly', 'meli',
            'ýarka', 'ýärkä', 'ýaka', 'ýäkä',
            'madyk', 'medik', 'maly', 'meli',
            
            # --- 3 Harplylar ---
            'lar', 'ler', 'dan', 'den', 'tan', 'ten',
            'nyň', 'niň', 'nuň', 'nüň', # Eýelik düşüm (genitive) - Siziň sanawyňyzda ýokdy
            'daş', 'deş', # Meselem: watan-daş
            'lyk', 'lik', 'luk', 'lük', # At ýasaýjylar: gözellik
            'syz', 'siz', # Sypat ýasaýjylar
            'dar', 'gir', 'gor', # Meselem: bergidar
            'ýar', 'ýär', 'ýor', 'ýör', # Häzirki zaman
            'jak', 'jek', # Geljek zaman
            'myş', 'miş', # Eşidilen geçen zaman
            'dyr', 'dir', 'dur', 'dür', # Habar goşulmasy (Predicative)
            'man', 'män', # Hal işlik (gelmän)
            'maz', 'mez', # Inkär geljek zaman
            'mak', 'mek', # Işlik düýbi (infinitive)
            'yjy', 'iji', 'ujy', 'üji', # At ýasaýjy: oka-yjy
            
            # --- 2 Harplylar ---
            'ny', 'ni', # Tabşyryş düşüm
            'da', 'de', 'ta', 'te', # Wagt-orun düşüm
            'ym', 'im', 'um', 'üm', # Meniň (I)
            'yň', 'iň', 'uň', 'üň', # Seniň (II) we Eýelik düşüm gysgalan görnüşi
            'sy', 'si', # Onuň (III)
            'ka', 'kä', # Sorag/güman: barmyka?
            'my', 'mi', # Sorag: barmy?
            'ma', 'me', # Inkär: gelme
            'yp', 'ip', 'up', 'üp', # Hal işlik: gelip
            'an', 'en', # Sypat işlik: gelen
            'dy', 'di', # Şaýatly geçen zaman
            'çy', 'çi', # Kär aňladýan: balykçy
            
            # --- 1 Harplylar (Bular iň soňunda bolmaly) ---
            'a', 'e', 'ä', # Gönükdirilen düşüm
            'y', 'i', # Tabşyryş düşüm gysgalan
        ]
        self.common_suffixes = sorted(list(set(self.common_suffixes)), key=len, reverse=True)
        # Aýratyn tokenler
        self.special_tokens = {
            # Standart tokenler
            '<pad>': 0,    # Padding (Doldurgyç - uzynlygy deňlemek üçin)
            '<unk>': 1,    # Unknown (Nätanyş söz)
            '<bos>': 2,    # Beginning of Sentence (Sentensiýa başy - GPT üçin)
            '<eos>': 3,    # End of Sentence (Sentensiýa soňy - GPT üçin)
            
            '<mask>': 4,   # Masked Language Modeling (MLM) üçin. Meselem: "Men <mask> gidýärin."
            '<cls>': 5,    # Classification (Tekst klassifikasiýasy üçin başy)
            '<sep>': 6,    # Separator (Iki sözlemi bölmek üçin. Meselem: Sorag <sep> Jogap)
            
            '<name>': 7,   
            '<city>': 8,   
            '<country>': 9,
            '<num>': 10,   # Sanlary bellemek üçin (islege görä)
            '<url>': 11,   # Linkleri bellemek üçin
            '<email>': 12  # E-poçtalary bellemek üçin
        }
        
    def is_proper_noun(self, word: str) -> Tuple[bool, str]:
        """
        Söziň adaty at (proper noun) bardygyny barlaýar
        Gaýtaryş: (haýsy_at_bolsa, at_görnüşi)
        """
        word_lower = word.lower()
        
        # Adam atlary
        if word_lower in self.male_names or word_lower in self.female_names:
            return True, 'name'
        
        # Şäher atlary
        if word_lower in self.cities:
            return True, 'city'
        
        # Ýurt atlary
        if word_lower in self.countries:
            return True, 'country'
        
        # Möhüm sözler
        if word_lower in self.important_words:
            return True, 'important'
        
        return False, None
    
    def normalize_text(self, text: str) -> str:
        text = unicodedata.normalize("NFKC", text)
        # 2. Türkmen dilindäki ýygy duş gelýän ýalňyşlary düzetmek
        replacements = {
            "ÿ": "ý", "¥": "ý",  # Ýalňyş kodlanan ý-ler
            "ə": "ä",            # Azeri/Tatar klawiaturasyndan galanlar
            "ş": "ş", "s": "ş",  # Käwagt ş ýerine s ýazylýar (muňa seresap bolmaly)
            "“": '"', "”": '"', "’": "'", "‘": "'", # Dürli dyrnaklar
            "\u00ad": "",        # Soft hyphen (görünmeýän kese çyzyk)
            "&nbsp;": " "        # HTML boşluk
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        # 3. Artykmaç boşluklary aýyrmak
        text = re.sub(r'\s+', ' ', text)
        return text.strip().lower()

    def aggressive_suffix_split(self, word: str) -> str:
        """
        Sözleriň soňundaky goşulmalary bölýär. 
        Meselem: "mekdepde" -> "mekdep de"
        """
        # Gysga sözlere degmeýäris (ýalňyş bölmezlik üçin)
        if len(word) < 4:
            return word
            
        # Goşulmalary uzynlygyna görä tertipleýäris (uzynlar öňde)
        sorted_suffixes = sorted(self.common_suffixes, key=len, reverse=True)
        
        for suffix in sorted_suffixes:
            if word.endswith(suffix):
                # Kök söz gaty gysga bolmaly däl (meselem: 'ada' -> 'a da' bolmazlygy üçin)
                stem = word[:-len(suffix)]
                if len(stem) >= 2:
                    return f"{stem} {suffix}"
        return word

    # 2-NJI ÄDIM: pre_tokenize funksiýasyny täzeläň (köne koduny öçürip, şuny goýuň)
    def pre_tokenize(self, text: str) -> List[Tuple[str, str]]:
        """
        Teksti sözlere we nyşanlara bölýär, at görnüşini hem belleýär.
        Goşulmalary hem aýratynlaýar.
        """
        text_lower = text.lower()
        
        # Regex pattern
        pattern = r"[a-zäňöşüýžçа-я]+|[0-9]+|[^\w\s]+"
        raw_tokens = re.findall(pattern, text_lower)
        
        typed_tokens = []
        for token in raw_tokens:
            # Ilki bilen adaty atdygyny barla
            is_proper, proper_type = self.is_proper_noun(token)
            
            if is_proper:
                typed_tokens.append((token, proper_type))
            else:
                # Eger adaty at däl bolsa, goşulmany barlap gör
                # Meselem: "mekdepde" -> "mekdep" "de"
                split_version = self.aggressive_suffix_split(token)
                
                if split_version != token:
                    # Eger söz bölünen bolsa (mekdep de)
                    parts = split_version.split()
                    for part in parts:
                        typed_tokens.append((part, 'word'))
                else:
                    # Bölünmedik bolsa
                    typed_tokens.append((token, 'word'))
        
        return typed_tokens

    def get_word_frequencies(self, corpus: List[str]) -> Dict[str, int]:
        """
        Sözleriň ýygylyklaryny hasaplaýar
        """
        word_freqs = Counter()
        
        for text in corpus:
            tokens = self.pre_tokenize(text)
            # Diňe söz bölekleri al, at görnüşini aýyr
            words = [token for token, _ in tokens]
            word_freqs.update(words)
        
        return dict(word_freqs)
    
    def get_character_vocab(self, word_freqs: Dict[str, int]) -> Set[str]:
        """
        Başlangyç harp toplumyny döredýär
        """
        chars = set()
        for word in word_freqs.keys():
            chars.update(list(word))
        return chars
    
    def split_word_to_chars(self, word: str) -> List[str]:
        """
        Sözi harp tokenlerine bölýär, soňky harpa "</w>" goşýar
        """
        if len(word) == 0:
            return []
        chars = list(word[:-1])
        chars.append(word[-1] + '</w>')
        return chars
    
    def get_pair_frequencies(self, splits: Dict[str, List[str]], 
                            word_freqs: Dict[str, int]) -> Dict[Tuple[str, str], int]:
        """
        Goňşy token jübütleriniň ýygylyklaryny hasaplaýar
        """
        pair_freqs = defaultdict(int)
        
        for word, freq in word_freqs.items():
            split = splits[word]
            if len(split) < 2:
                continue
            
            for i in range(len(split) - 1):
                pair = (split[i], split[i + 1])
                pair_freqs[pair] += freq
        
        return dict(pair_freqs)
    
    def merge_pair(self, pair: Tuple[str, str], splits: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Iň ýygy jübüti birleşdirýär
        """
        new_splits = {}
        
        for word, split in splits.items():
            if len(split) < 2:
                new_splits[word] = split
                continue
            
            new_split = []
            i = 0
            
            while i < len(split):
                if i < len(split) - 1 and (split[i], split[i + 1]) == pair:
                    new_split.append(split[i] + split[i + 1])
                    i += 2
                else:
                    new_split.append(split[i])
                    i += 1
            
            new_splits[word] = new_split
        
        return new_splits
    
    def add_proper_nouns_to_vocab(self, vocab: List[str]) -> List[str]:
        """
        Adaty atlary söz kitabyna goşýar
        """
        # Adam atlary
        for name in self.male_names | self.female_names:
            if name not in vocab:
                vocab.append(name + '</w>')
        
        # Şäher atlary
        for city in self.cities:
            if city not in vocab:
                vocab.append(city + '</w>')
        
        # Ýurt atlary
        for country in self.countries:
            if country not in vocab:
                vocab.append(country + '</w>')
        
        # Möhüm sözler
        for word in self.important_words:
            if word not in vocab:
                vocab.append(word + '</w>')
        
        return vocab
    
    def train(self, corpus_path: str, verbose: bool = True):
        def corpus_generator():
            with open(corpus_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        yield line.strip()
        """
        Korpusda BPE tokenizerini öwredýär
        """
        if verbose:
            print("🇹🇲 Türkmen BPE Tokenizer öwrenişi başlanýar...")
        
        # 1. Aýratyn tokenleri goş
        vocab = list(self.special_tokens.keys())
        if verbose:
            print(f"✓ {len(self.special_tokens)} aýratyn token goşuldy")
        
        # 2. Sözleriň ýygylyklaryny hasapla
        self.word_freqs = self.get_word_frequencies(corpus_generator())
        if verbose:
            print(f"✓ {len(self.word_freqs)} üýtgeşik söz tapyldy")
        
        # 3. Başlangyç harp toplumyny döret
        chars = self.get_character_vocab(self.word_freqs)
        vocab.extend(list(chars) + ['</w>'])
        if verbose:
            print(f"✓ Başlangyç harp toplumy: {len(chars)} simwol")
        
        # 4. Adaty atlary goş
        vocab = self.add_proper_nouns_to_vocab(vocab)
        if verbose:
            print(f"✓ Adaty atlar goşuldy (adam, şäher, ýurt atlary)")
            print(f"  - Adam atlary: {len(self.male_names | self.female_names)}")
            print(f"  - Şäher atlary: {len(self.cities)}")
            print(f"  - Ýurt atlary: {len(self.countries)}")
        
        # 5. Sözleri harplara böl
        splits = {word: self.split_word_to_chars(word) 
                 for word in self.word_freqs.keys()}
        
        # 6. BPE birleşdirmeleri
        num_merges = self.vocab_size - len(vocab)
        
        if verbose:
            print(f"\n🔄 BPE birleşdirmeleri başlanýar ({num_merges} gezek)...")
        
        for i in range(num_merges):
            # Jübüt ýygylyklary
            pair_freqs = self.get_pair_frequencies(splits, self.word_freqs)
            
            if not pair_freqs:
                if verbose:
                    print(f"⚠ {i} birleşdirmeden soň täze jübüt tapylmady")
                break
            
            # Iň ýygy jübüt
            best_pair = max(pair_freqs, key=pair_freqs.get)
            
            # Birleşdir
            splits = self.merge_pair(best_pair, splits)
            self.merges.append(best_pair)
            
            # Täze tokeni goş
            new_token = best_pair[0] + best_pair[1]
            vocab.append(new_token)
            
            if verbose and (i + 1) % 500 == 0:
                print(f"  {i + 1}/{num_merges} birleşdirme tamamlandy - "
                      f"Iň soňky: {best_pair[0]} + {best_pair[1]} = {new_token}")
        
        # Söz kitabyny döret
        self.vocab = {token: idx for idx, token in enumerate(vocab)}
        
        # Aýratyn tokenler ID-lerini täzele
        for token, idx in self.special_tokens.items():
            if token in self.vocab:
                # Aýratyn tokenleriň ID-lerini üýtget
                old_idx = self.vocab[token]
                self.vocab[token] = idx
                # Beýleki tokenleriň ID-lerini düzet
                for t in list(self.vocab.keys()):
                    if self.vocab[t] == idx and t != token:
                        self.vocab[t] = old_idx
        
        if verbose:
            print(f"\n✅ Öwreniş tamamlandy! Jemi {len(self.vocab)} token")
            self._print_statistics()
    
    def _print_statistics(self):
        """
        Tokenizer statistikasyny görkezýär
        """
        print("\n📊 Statistika:")
        print(f"  - Jemi tokenler: {len(self.vocab)}")
        print(f"  - Jemi birleşdirmeler: {len(self.merges)}")
        print(f"  - Aýratyn tokenler: {len(self.special_tokens)}")
        
        # Adam atlary
        name_count = sum(1 for name in (self.male_names | self.female_names) 
                        if (name + '</w>') in self.vocab)
        print(f"  - Adam atlary: {name_count}/{len(self.male_names | self.female_names)}")
        
        # Şäher atlary
        city_count = sum(1 for city in self.cities 
                        if (city + '</w>') in self.vocab)
        print(f"  - Şäher atlary: {city_count}/{len(self.cities)}")
        
        # Ýurt atlary
        country_count = sum(1 for country in self.countries 
                           if (country + '</w>') in self.vocab)
        print(f"  - Ýurt atlary: {country_count}/{len(self.countries)}")
        
        # Türkmen goşulmalarynyň ýagdaýy
        suffix_count = 0
        for suffix in self.common_suffixes:
            for token in self.vocab.keys():
                if suffix in token and token != suffix:
                    suffix_count += 1
                    break
        
        print(f"  - Türkmen goşulmalaryny öz içine alýan tokenler: {suffix_count}")
    
    def tokenize(self, text: str) -> List[str]:
        """
        Teksti tokenlere bölýär
        """
        tokens = []
        typed_words = self.pre_tokenize(text)
        
        for word, word_type in typed_words:
            # Eger adaty at bolsa we söz kitabynda bar bolsa, tutuş söz hökmünde goş
            full_word_token = word + '</w>'
            if word_type != 'word' and full_word_token in self.vocab:
                tokens.append(full_word_token)
                continue
            
            # Harplardan başla
            word_tokens = self.split_word_to_chars(word)
            
            # Birleşdirmeleri ulan
            for merge in self.merges:
                i = 0
                while i < len(word_tokens) - 1:
                    if (word_tokens[i], word_tokens[i + 1]) == merge:
                        word_tokens[i] = word_tokens[i] + word_tokens[i + 1]
                        word_tokens.pop(i + 1)
                    else:
                        i += 1
            
            tokens.extend(word_tokens)
        
        return tokens
    
    def encode(self, text: str) -> List[int]:
        """
        Teksti token ID-lerine öwürýär
        """
        tokens = self.tokenize(text)
        return [self.vocab.get(token, self.special_tokens['<unk>']) for token in tokens]
    
    def decode(self, token_ids: List[int]) -> str:
        """
        Token ID-lerini tekste öwürýär
        """
        # ID-den token-e geçiş
        id_to_token = {idx: token for token, idx in self.vocab.items()}
        tokens = [id_to_token.get(id, '<unk>') for id in token_ids]
        
        # Aýratyn tokenleri aýyr
        tokens = [t for t in tokens if t not in self.special_tokens]
        
        # Tokenleri birleşdir we </w> aýyr
        text = ''.join(tokens).replace('</w>', ' ')
        return text.strip()
    
    def save(self, filepath: str):
        """
        Tokenizerini faýla saklaýar
        """
        data = {
            'vocab': self.vocab,
            'merges': self.merges,
            'vocab_size': self.vocab_size,
            'special_tokens': self.special_tokens,
            'male_names': list(self.male_names),
            'female_names': list(self.female_names),
            'cities': list(self.cities),
            'countries': list(self.countries),
            'important_words': list(self.important_words)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Tokenizer '{filepath}' faýlyna saklandy")
    
    def load(self, filepath: str):
        """
        Tokenizerini faýldan ýükleýär
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.vocab = data['vocab']
        self.merges = [tuple(merge) for merge in data['merges']]
        self.vocab_size = data['vocab_size']
        self.special_tokens = data.get('special_tokens', self.special_tokens)
        self.male_names = set(data.get('male_names', []))
        self.female_names = set(data.get('female_names', []))
        self.cities = set(data.get('cities', []))
        self.countries = set(data.get('countries', []))
        self.important_words = set(data.get('important_words', []))
        
        print(f"✓ Tokenizer '{filepath}' faýlyndan ýüklendi")
    
    def add_names(self, names: List[str], gender: str = 'male'):
        """
        Täze atlary goşmak (öwrenişden soň ulanmak üçin)
        """
        if gender == 'male':
            self.male_names.update([n.lower() for n in names])
        else:
            self.female_names.update([n.lower() for n in names])
        
        # Söz kitabyna goş
        for name in names:
            name_token = name.lower() + '</w>'
            if name_token not in self.vocab:
                self.vocab[name_token] = len(self.vocab)
        
        print(f"✓ {len(names)} täze at goşuldy")
    
    def add_cities(self, cities: List[str]):
        """
        Täze şäher atlaryny goşmak
        """
        self.cities.update([c.lower() for c in cities])
        
        for city in cities:
            city_token = city.lower() + '</w>'
            if city_token not in self.vocab:
                self.vocab[city_token] = len(self.vocab)
        
        print(f"✓ {len(cities)} täze şäher ady goşuldy")
    
    def export_to_huggingface(self, save_path: str = "turkmen_hf_tokenizer.json"):
        """
        Hugging Face 'tokenizers' formatyna geçirýär we saklaýar.
        Uly modeller (BERT, GPT) bilen ulanmak üçin.
        """
        try:
            from tokenizers import Tokenizer, models, pre_tokenizers, decoders
        except ImportError:
            print("❌ Bu funksiýa üçin 'tokenizers' kitaphanasy gerek.")
            print("Haýyş, 'pip install tokenizers' buýrugyny ýerine ýetiriň.")
            return

        print("🔄 Hugging Face formatyna geçirilýär...")
        
        # Vocab (sozluk) dict formatyndan list formatyna geçirmek zerur bolup biler, 
        # ýöne HF BPE modeli göni dict kabul edýär (token -> id).
        # Biziň 'merges' listimiz tuple (a, b), ýöne HF string "a b" isleýär.
        
        hf_merges = [f"{p[0]} {p[1]}" for p in self.merges]
        
        # Täze tokenizer döretmek
        # Unknown token hökmünde <unk> ulanýarys
        hf_tokenizer = Tokenizer(models.BPE(vocab=self.vocab, merges=hf_merges, unk_token="<unk>"))
        
        # Tokenizer sazlamalary (Pre-tokenizer)
        # Biziň Python kodumyzda edýän whitespace bölmegimizi gaýtalamaly
        hf_tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
        
        # Saklamak
        hf_tokenizer.save(save_path)
        print(f"✅ Hugging Face tokenizer '{save_path}' faýlyna saklandy!")


# Ulanyş mysaly
if __name__ == "__main__":

    print("=" * 60)
    tokenizer = TurkmenBPETokenizer(vocab_size=1000)
    tokenizer.train("dataset_AB_220524.txt", verbose=True)
    
    # Synaglary geçir
    print("\n" + "=" * 60)
    print("🧪 SYNAG MYSALLARY")
    print("=" * 60)
    
    test_texts = [
        "Ahmet Aşgabatda işleýär",
        "Oguljan Mary şäherinden geldi",
        "Türkmenistan we Türkiýe dostlukly ýurtlar",
        "Serdar Daşoguzdan Türkmenabada bardy",
        "Magtymguly Pyragynyň şygryýeti"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Synag {i}:")
        print(f"Giriş: {text}")
        
        tokens = tokenizer.tokenize(text)
        print(f"Tokenler: {tokens}")
        print(f"Token sany: {len(tokens)}")
        
        encoded = tokenizer.encode(text)
        print(f"Kodlanan: {encoded}")
        
        decoded = tokenizer.decode(encoded)
        print(f"Dekodlanan: {decoded}")
        
        # At analizi
        typed_tokens = tokenizer.pre_tokenize(text)
        names = [t for t, typ in typed_tokens if typ == 'name']
        cities = [t for t, typ in typed_tokens if typ == 'city']
        
        if names:
            print(f"🧑 Adam atlary: {names}")
        if cities:
            print(f"🏙️ Şäher atlary: {cities}")
    
    # Sakla
    print("\n" + "=" * 60)
    tokenizer.save("turkmen_tokenizer.json")
    tokenizer.export_to_huggingface("turkmen_hf_tokenizer.json")

    # Täze atlar goşmak mysaly
    print("\n" + "=" * 60)