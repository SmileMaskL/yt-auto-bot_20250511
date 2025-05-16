from translate import Translator

def translate_subtitles(text, target_lang='ko'):
    translator = Translator(to_lang=target_lang)
    return translator.translate(text)
