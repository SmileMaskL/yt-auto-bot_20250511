from translate import Translator

def translate_subtitles(input_srt, output_srt, target_language):
    translator = Translator(to_lang=target_language)
    with open(input_srt, 'r', encoding='utf-8') as infile, open(output_srt, 'w', encoding='utf-8') as outfile:
        for line in infile:
            if line.strip() and not line.strip().isdigit() and '-->' not in line:
                translated = translator.translate(line.strip())
                outfile.write(translated + '\n')
            else:
                outfile.write(line)
