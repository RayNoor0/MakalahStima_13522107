from googletrans import Translator
from multiprocessing.pool import ThreadPool as Pool
import threading

# copied from Translator
LANGUAGES = {
    'af': 'afrikaans',
    'sq': 'albanian',
    'am': 'amharic',
    'ar': 'arabic',
    'hy': 'armenian',
    'az': 'azerbaijani',
    'eu': 'basque',
    'be': 'belarusian',
    'bn': 'bengali',
    'bs': 'bosnian',
    'bg': 'bulgarian',
    'ca': 'catalan',
    'ceb': 'cebuano',
    'ny': 'chichewa',
    'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)',
    'co': 'corsican',
    'hr': 'croatian',
    'cs': 'czech',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'eo': 'esperanto',
    'et': 'estonian',
    'tl': 'filipino',
    'fi': 'finnish',
    'fr': 'french',
    'fy': 'frisian',
    'gl': 'galician',
    'ka': 'georgian',
    'de': 'german',
    'el': 'greek',
    'gu': 'gujarati',
    'ht': 'haitian creole',
    'ha': 'hausa',
    'haw': 'hawaiian',
    'iw': 'hebrew',
    'he': 'hebrew',
    'hi': 'hindi',
    'hmn': 'hmong',
    'hu': 'hungarian',
    'is': 'icelandic',
    'ig': 'igbo',
    'id': 'indonesian',
    'ga': 'irish',
    'it': 'italian',
    'ja': 'japanese',
    'jw': 'javanese',
    'kn': 'kannada',
    'kk': 'kazakh',
    'km': 'khmer',
    'ko': 'korean',
    'ku': 'kurdish (kurmanji)',
    'ky': 'kyrgyz',
    'lo': 'lao',
    'la': 'latin',
    'lv': 'latvian',
    'lt': 'lithuanian',
    'lb': 'luxembourgish',
    'mk': 'macedonian',
    'mg': 'malagasy',
    'ms': 'malay',
    'ml': 'malayalam',
    'mt': 'maltese',
    'mi': 'maori',
    'mr': 'marathi',
    'mn': 'mongolian',
    'my': 'myanmar (burmese)',
    'ne': 'nepali',
    'no': 'norwegian',
    'or': 'odia',
    'ps': 'pashto',
    'fa': 'persian',
    'pl': 'polish',
    'pt': 'portuguese',
    'pa': 'punjabi',
    'ro': 'romanian',
    'ru': 'russian',
    'sm': 'samoan',
    'gd': 'scots gaelic',
    'sr': 'serbian',
    'st': 'sesotho',
    'sn': 'shona',
    'sd': 'sindhi',
    'si': 'sinhala',
    'sk': 'slovak',
    'sl': 'slovenian',
    'so': 'somali',
    'es': 'spanish',
    'su': 'sundanese',
    'sw': 'swahili',
    'sv': 'swedish',
    'tg': 'tajik',
    'ta': 'tamil',
    'te': 'telugu',
    'th': 'thai',
    'tr': 'turkish',
    'uk': 'ukrainian',
    'ur': 'urdu',
    'ug': 'uyghur',
    'uz': 'uzbek',
    'vi': 'vietnamese',
    'cy': 'welsh',
    'xh': 'xhosa',
    'yi': 'yiddish',
    'yo': 'yoruba',
    'zu': 'zulu',
}

translated_words = []
counter = 0

def get_words():
    res = []
    file = open("english_words.txt", "r")
    cnt = 0
    for x in file:
        if(cnt == 0):
            res.append(x)
        cnt+=1
        cnt%=10
        
    return res

def translate_text(text, src_lang, dest_lang):
    translator = Translator()
    try:
        translated = translator.translate(text, src=src_lang, dest=dest_lang)
        if(translated.pronunciation == None):
            return translated.text
        else:
            return translated.pronunciation
    except Exception as e:
        print(e)
    
def levenshteinDP(s1, s2):
    m = len(s1)
    n = len(s2)
 
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]
 
    # basis
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
 
    # rekurens
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i][j - 1], dp[i - 1][j], dp[i - 1][j - 1])
    return dp[m][n]

POOL_SIZE = 20
lock = threading.Lock()

def worker(word, src_lang, dest_lang_1, dest_lang_2):
    try:
        translated_text_one = translate_text(word, src_lang, dest_lang=dest_lang_1)

        translated_text_two = translate_text(word, src_lang, dest_lang=dest_lang_2)

        translated_texts = [src_lang, translated_text_one, translated_text_two]
        print(translated_texts)

        lock.acquire()
        try:
            translated_words.append(translated_texts)
            global counter
            counter+=1
            print(counter)
        finally:
            lock.release()

    except Exception as e:
        raise e

pool = Pool(POOL_SIZE)


if __name__ == "__main__":
    if(str.lower(str(input("Apakah kamu ingin melihat daftar kode bahasa?(Y/N)")))=="y"):
        print(LANGUAGES)

    source_language = "en"
    language_1 = str(input("\nMasukkan kode bahasa pertama:"))
    language_2 = str(input("\nMasukkan kode bahasa kedua:"))


    words = get_words()
    for word in words:
        param = [word, source_language, language_1, language_2]
        pool.apply_async(worker, args=param)

    pool.close()
    pool.join()

    result = []

    for translated_tuple in translated_words:
        try:
            distance = levenshteinDP(translated_tuple[1],translated_tuple[2])
            if(distance < (len(translated_tuple[1])+len(translated_tuple[2]))/3):
                result.append([translated_tuple[0], translated_tuple[1], translated_tuple[2],distance])
        finally:
            continue

    print(f"ditemukan {len(result)} yang mirip yakni:")
    cnt = 1
    for calculated_tuple in result:
        print(f"{cnt}.\nKata dalam bahasa pertama: {calculated_tuple[1]}\nKata dalam bahasa kedua: {calculated_tuple[2]}\nJarak: {calculated_tuple[3]}")
        cnt+=1
    