# 🇹🇲 Türkmen BPE Tokenizer (Byte-Pair Encoding)

Türkmen diliniň textini token'lere bölen intelligent tokenizer. Bu proje Byte-Pair Encoding (BPE) algoritmini Türkmen diline özel adaptasiýa bilen durmuşa geçirýär.

## 📋 Mazmun

- [Aýratynlyklar](#aýratynlyklar)
- [Tehnologiýa](#tehnologiýa)
- [Ýüklemek we Ulanmak](#ýüklemek-we-ulanmak)
- [Tokenizer Komponenti](#tokenizer-komponenti)
- [Mysallary](#mysallary)
- [Parametrler we Sazlamalar](#parametrler-we-sazlamalar)

---

## ✨ Aýratynlyklar

### 1. **Byte-Pair Encoding (BPE) Algoritmi**

- Täze söz kitaby (vocabulary) öwrenýär
- Iň ýygy token jübütlerini birleşdirerek token sany optimallaşdyrýar
- 10,000 token çenli ýygyn texti geçirmäge unyýan

### 2. **Türkmen Diline Özel Terjimeler**

- **Harfsız Harplary Goldaýan**: `ä`, `ň`, `ö`, `ş`, `ü`, `ý`, `ž` - guramotory Türkmen dialektasy tarapyndan ulanylýan aýratyn nyşanlar
- **Türkmen Goşulmalarynyň Analizi**: Sözleriň `laryň`, `syzlyk`, `darlyk`, `maly` we beýleki goşulmalary aýratynlaýar
- **Geografik Nämeleri Goldaýan**:
  - 30+ Türkmenistan şäher we welaýat
  - 50+ täze atlarynyň (erkek, aýal)
  - 20+ daşary ýurt atlary

### 3. **Adaty Atlar Klassifikasiýasy**

Tokenizer aşakdaky at görnüşlerini ilenip saýlaýar:

- **Adam Atlary** (şahsy): 60+ erkek atly, 30+ aýal atly
- **Şäher Atlary**: Aşgabat, Daşoguz, Balkanabat, Mary, Tejen we başgalar
- **Ýurt Atlary**: Türkiýe, Eýran, Russiýa, Hytaý we başgalar
- **Möhüm Sözler**: "Türkmenistan", "Prezident", "Halk", "Garaşsyzlyk"

### 4. **Aýratyn Tokenler**

Modelleme üçin 13 aýratyn token:

```
<pad>      - Doldurgyç
<unk>      - Tanyşsyz token
<bos>      - Sentensiýa başy
<eos>      - Sentensiýa soňy
<mask>     - Maskir (MLM üçin)
<cls>      - Klassifikasiýa başy
<sep>      - Ayyryjy
<name>     - Adam ady
<city>     - Şäher ady
<country>  - Ýurt ady
<num>      - Sany
<url>      - Web salgysy
<email>    - E-poçta
```

### 5. **Teksti Normallaşdyrma**

- NFKC unicode normallaşdyrylyşy
- Kesgitlenen ýalňyş kodlanylşlar düzetmek
- Artykmaç boşluklary aýyrmak
- Lowecase'e öwürme

### 6. **Goşulmany Bölüp Ayyrma**

Sözleriň soňundaky Türkmen goşulmasyny intellektual bilen aýratynlaýar:

- `mekdepde` → `mekdep` + `de`
- `kitaplarym` → `kitap` + `lar` + `ym`
- `gözelliksiž` → `gözelli` + `k` + `siž`

---

## 🛠 Tehnologiýa

### Asasy Python Kitaphanasy

- `collections` - Counter we defaultdict üçin
- `unicodedata` - Unicode normallaşdyrylyşy
- `json` - Tokenizer saklamak we ýüklemek
- `regex (re)` - Pattern matching we tokenlaşdyrma
- `typing` - Tipleri barlamak

### Isteglere gora kitaphanalar

- `tokenizers` (Hugging Face) - Export üçin

---

## 🚀 Ýüklemek we Ulanmak

### 1. Corpus'da Öwretmek

```python
from bpetokenizer import TurkmenBPETokenizer

# Tokenizer döret (10,000 token iş sayy)
tokenizer = TurkmenBPETokenizer(vocab_size=10000)

# Corpus'da öwret
tokenizer.train("dataset_AB_220524.txt", verbose=True)

# Saklama
tokenizer.save("turkmen_tokenizer.json")
```

### 2. Teksti Tokenlaşdyrma

```python
# Tokenlere böl
text = "Ahmet Aşgabatda işleýär"
tokens = tokenizer.tokenize(text)
print(tokens)
# Netije: ['ahmet</w>', 'aşgabat</w>', 'da', 'işle', 'ýär</w>']

# Token ID-lerine öwür (Model girişi üçin)
token_ids = tokenizer.encode(text)
print(token_ids)
# Netije: [245, 128, 82, 439, 521]

# ID-lerden tekste öwür (Model çykyşy üçin)
decoded = tokenizer.decode(token_ids)
print(decoded)
# Netije: "ahmet aşgabat da işle ýär"
```

### 3. Tokenizer Ýüklemek

```python
# Öwrenilen tokenizer-i ýükle
tokenizer = TurkmenBPETokenizer()
tokenizer.load("turkmen_tokenizer.json")

# Derrew ulan
tokens = tokenizer.tokenize("Oguljan Mary şäherinden geldi")
```

### 4. Hugging Face Formatyna Geçirmek

```python
# Uly modeller (BERT, GPT) bilen ulanmak üçin
tokenizer.export_to_huggingface("turkmen_hf_tokenizer.json")
```

---

## 🔧 Tokenizer Komponenti

### Esasy Klasslar we Metodlar

#### **`__init__(vocab_size: int = 10000)`**

Tokenizer başlatýar. Türkmen diliniň aýratyn nyşanlaryny, at toplumlary we goşulmalary başlangyç sazlaýar.

**Parametrler:**

- `vocab_size`: Maksimal token sany (default: 10,000)

---

#### **`normalize_text(text: str) -> str`**

Teksti normallaşdyrýar: Unicode NFKC, ýalňyş kod düzeltmeleri, artykmaç boşluk aýyrylyşy.

**Mysaly:**

```python
text = "  AHMET   aşGABAT  "
normalized = tokenizer.normalize_text(text)
# "ahmet aşgabat"
```

---

#### **`aggressive_suffix_split(word: str) -> str`**

Sözleriň soňundaky Türkmen goşulmasyny aýratynlaýar.

**Mysaly:**

```python
result = tokenizer.aggressive_suffix_split("mekdepde")
# "mekdep de"
```

---

#### **`pre_tokenize(text: str) -> List[Tuple[str, str]]`**

Teksti sözlere we nyşanlara bölüp, at görnüşini belleýär.

**Netije Format:**

```python
[
    ("ahmet", "name"),           # Adam ady
    ("aşgabat", "city"),         # Şäher ady
    ("da", "word"),              # Ady söz
    ("işle", "word"),            # Ady söz
    ("ýär", "word")              # Ady söz
]
```

---

#### **`is_proper_noun(word: str) -> Tuple[bool, str]`**

Söziň adaty at bardygyny barlaýar.

**Netije:**

```python
(is_proper, noun_type)
# Meselem: (True, 'name'), (False, None)
```

---

#### **`train(corpus_path: str, verbose: bool = True)`**

Corpus'dan tokenizer öwredýär. BPE algoritmi ulanýar.

**Işleme Tahminawy:**

1. Aýratyn tokenleri goş
2. Sözleriň ýygylyklaryny hasapla
3. Başlangyç harp toplumy döret
4. Adaty atlary goş
5. BPE birleşdirmelerini ýerine ýet
6. Söz kitabyny finallaşdyr

---

#### **`tokenize(text: str) -> List[str]`**

Teksti tokenlere bölýär.

**Mysaly:**

```python
text = "Turkmenistan we Türkiýe dostlukly ýurtlar"
tokens = tokenizer.tokenize(text)
# Netije: ['turkmenistan</w>', 've</w>', 'türk', 'iýe</w>', 'do', 'st', 'luk', 'ly</w>', 'ýurt', 'lar</w>']
```

---

#### **`encode(text: str) -> List[int]`**

Teksti token ID-lerine öwürýär (ML model girişi).

**Mysaly:**

```python
token_ids = tokenizer.encode("Ahmet işleýär")
# [245, 82, 439, 521]
```

---

#### **`decode(token_ids: List[int]) -> str`**

Token ID-lerini tekste öwürýär (ML model çykyşy).

**Mysaly:**

```python
decoded = tokenizer.decode([245, 82, 439, 521])
# "ahmet işle ýär"
```

---

#### **`save(filepath: str)`** / **`load(filepath: str)`**

Tokenizerini JSON faýlynda saklaýar we ýükleýär.

**JSON Toplam:**

```json
{
  "vocab": {...},
  "merges": [...],
  "vocab_size": 10000,
  "special_tokens": {...},
  "male_names": [...],
  "female_names": [...],
  "cities": [...],
  "countries": [...],
  "important_words": [...]
}
```

---

#### **`add_names(names: List[str], gender: str = 'male')`**

Öwrenişden soň täze atlary goşýar.

**Mysaly:**

```python
tokenizer.add_names(['Serdar', 'Döwlet'], gender='male')
tokenizer.add_names(['Maral', 'Leýla'], gender='female')
```

---

#### **`add_cities(cities: List[str])`**

Täze şäher atlaryny goşýar.

**Mysaly:**

```python
tokenizer.add_cities(['Tejen', 'Baýramaly'])
```

---

#### **`export_to_huggingface(save_path: str = "turkmen_hf_tokenizer.json")`**

Tokenizerini Hugging Face formatyna geçirerek saklaýar. BERT, GPT we beýleki uly modeller bilen ulanmak üçin ideal.

**Mizady:**

```python
tokenizer.export_to_huggingface("my_hf_tokenizer.json")
```

---

## 📊 Teksti Analizi we At Klassifikasiýasy

Tokenizer, teksti tokenlaşdyrmagynyň bilen hasada şu analyti berýär:

```python
text = "Magtymguly Aşgabatda Prezidentligiň bürosynda işleýärdi"
typed_tokens = tokenizer.pre_tokenize(text)

# Netije:
# [
#     ("magtymguly", "name"),
#     ("aşgabat", "city"),
#     ("da", "word"),
#     ...
# ]
```

**Klassifikasion Görnüşleri:**

- `name` - Adam ady
- `city` - Şäher ady
- `country` - Ýurt ady
- `important` - Möhüm söz
- `word` - Ady söz

---

## 📝 Mysallary

### Synag 1: Adam Atlary

```python
text = "Ahmet Muhammet we Oguljan Aşgabatda"
tokens = tokenizer.tokenize(text)
# Netije: ['ahmet</w>', 'muhammet</w>', 've</w>', 'oguljan</w>', 'aşgabat</w>', 'da']
```

### Synag 2: Geografik Atlary

```python
text = "Türkiýe Russiýa Eýran we Hytaý"
tokens = tokenizer.tokenize(text)
# Netije: ['türkiýe</w>', 'russiýa</w>', 'eýran</w>', 've</w>', 'hytaý</w>']
```

### Synag 3: Goşulmaly Sözler

```python
text = "mekdepde kitaplarym"
tokens = tokenizer.tokenize(text)
# Netije: ['mekdep', 'de', 'kitap', 'lar', 'ym</w>']
```

### Synag 4: Kompleks Söz Kompleksi

```python
text = "Türkmenistan Prezidentligiň Portaly"
tokens = tokenizer.tokenize(text)
encoded = tokenizer.encode(text)
decoded = tokenizer.decode(encoded)

print("Asly:", text)
print("Tokenler:", tokens)
print("ID-ler:", encoded)
print("Görnüş:", decoded)
```

---

## ⚙️ Parametrler we Sazlamalar

### Başlangyç Sazlamalar

```python
class TurkmenBPETokenizer:
    def __init__(self, vocab_size: int = 10000):
        self.vocab_size = 10000          # Maksimal token sany
        self.vocab = {}                  # Token -> ID sözlügi
        self.merges = []                 # BPE birleşdirme taryhy
        self.word_freqs = {}             # Söz ýygylygy
        # ... beýlekiler
```

### Türkmen Harplary

```python
self.turkmen_chars = set('äňöşüýž')
```

### Aýratyn Tokenler ID-leri

| Token       | ID  | Häsiýeti        |
| ----------- | --- | --------------- |
| `<pad>`     | 0   | Doldurgyç       |
| `<unk>`     | 1   | Tanyşsyz        |
| `<bos>`     | 2   | Sentensiýa başy |
| `<eos>`     | 3   | Sentensiýa soňy |
| `<mask>`    | 4   | Maskir          |
| `<cls>`     | 5   | Klassifikasiýa  |
| `<sep>`     | 6   | Ayyryjy         |
| `<name>`    | 7   | Adam ady        |
| `<city>`    | 8   | Şäher ady       |
| `<country>` | 9   | Ýurt ady        |
| `<num>`     | 10  | Sany            |
| `<url>`     | 11  | Web salgysy     |
| `<email>`   | 12  | E-poçta         |

---

## 📊 Öwreniş Prosesi (Training Process)

BPE algoritmi aşakdaky ädimler bilen işleýär:

### 1. **Başlangyç Sazlama**

- Aýratyn tokenleri goş (13 token)
- Corpus'dan sözleriň ýygylyklaryny hasapla
- Her sözi harplaryna böl: `mekdep` → `m`, `e`, `k`, `d`, `e`, `p</w>`

### 2. **Jübüt Ýygylygy Hasaplama**

İýlişik harplar jübütleriniň ýygylygyny tapýar.

### 3. **İň Ýygy Jübüt Birleşdirmek**

Iň ýygy jübüti birleşdirip, täze token döredýär.

### 4. **Tekrarlama**

`vocab_size - len(initial_tokens)` saýy üçin 2-3 ädim tekrarlanyňar.

### 5. **Finallaşdyrma**

Söz kitaby (vocabulary) döredilýär we saklanýar.

---

## 💾 Faýllary Düşünmek

### `bpetokenizer.py`

Esasy `TurkmenBPETokenizer` klassy we ähli metodlar.

### `usetokenizer.py`

Tokenizerini praktikal ulanyş mysallary.

### `dataset_AB_220524.txt`

Öwrenişi üçin corpus (A we B toplumlary birleşdirilen).

### `turkmen_tokenizer.json`

Saklandy tokenizer (öwrenişden soň döredilýär).

### `turkmen_hf_tokenizer.json`

Hugging Face formatyndaky tokenizer.

---

## 🎯 Ulanyş Senaryiyleri

### 1. **Teksti Önü Işlemek**

Klassifikasiýa, teňdeme, atlar nomini tapma üçin.

```python
tokenizer = TurkmenBPETokenizer()
tokenizer.load("turkmen_tokenizer.json")
tokens = tokenizer.tokenize(my_text)
```

### 2. **Uly Dil Modeli Öwretmek**

BERT, GPT, T5 modelleri üçin Türkmen texti hazyrlamak.

```python
tokenizer.export_to_huggingface()
# Soňra Hugging Face 'transformers' kitaphanasy bilen ulan
```

### 3. **Sorag Jogap Sistemi**

Soraq we jogapty tokenlaşdyrmak.

```python
question = "Türkmenistan'yň paýtagty nedi?"
answer = "Aşgabat"
q_tokens = tokenizer.tokenize(question)
a_tokens = tokenizer.tokenize(answer)
```

### 4. **Teksti Klassifikasiýa**

Habary, şygryýety, surat ýe-de teksti görnüşlerine bölmek.

---

## 🔍 Teknikaýy Detallary

### BPE Algoritmi Kompleksligini

- **Zaman Kompleksligini**: O(n \* vocab_size), bu ýerde n - corpus ozmak
- **Ýaly Kompleksligini**: O(vocab_size)
- **Öwreniş Sede**: 500 söz Corpus üçin ~30 sekunt (vocab_size=10,000)

### Tokenizersizligi

```
Başlangyç Harp Sany: ~100
Birleşdirmeler: 9,887
Jemi Tokenler: ~10,000
Öwrenilen Atlary: ~150+ (erkek, aýal, şäher)
```

---

## 🤝 Şerik Olunasy

Täze atlary, şäherleri ýa-da goşulmalary goşmak üçin:

```python
# Täze atlary goşma
tokenizer.add_names(['Beiki', 'Täçberdi'], gender='male')

# Täze şäherleri goşma
tokenizer.add_cities(['Tejen', 'Kaka'])

# Corpus'dan täze modeli ýarata
tokenizer.train("new_corpus.txt")
```

---

## 📞 Haýyş we Meseleleri

Problemaňyz bar ýa-da teklipňiz bar bolsa, mesele açyň!

---

## 📄 Litsenziya

Bu proje Açyk Çeşme Döwlet Bolyp işleýär.
