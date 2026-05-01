import re
import pandas as pd
import tkinter as tk
from tkinter import scrolledtext
from jamdict import Jamdict

jam = Jamdict()
kana_set = set()
kana_set.update(chr(code) for code in range(0x3040, 0x30A0))  # Hiragana
kana_set.update(chr(code) for code in range(0x30A0, 0x3100))  # Katakana


def filter_kana(s):
    """Remove hiragana and katakana from input string (based on global kana_set)."""
    return ''.join(c for c in s if c not in kana_set)


def read_xlsx():
    def keep_only_kana(text):
        if not isinstance(text, str):
            return ""
        return ''.join(c for c in text if c in kana_set)

    xls = pd.ExcelFile('anki.xlsx')
    japanese_sheet = next(name for name in xls.sheet_names if name.startswith("Japanese"))
    kaishi_sheet = next(name for name in xls.sheet_names if name.startswith("Kaishi"))

    df_jap = pd.read_excel(xls, sheet_name=japanese_sheet)
    df_kaishi = pd.read_excel(xls, sheet_name=kaishi_sheet)

    df_jap['Furigana'] = df_jap['Furigana'].apply(keep_only_kana)
    df_kaishi['Word Reading'] = df_kaishi['Word Reading'].apply(keep_only_kana)

    jap_dict = df_jap.rename(
        columns={'Word': 'word', 'Furigana': 'furigana'}
    )[['word', 'furigana']].to_dict(orient='records')

    kaishi_dict = df_kaishi.rename(
        columns={'Word': 'word', 'Word Reading': 'furigana', 'Word Meaning': 'meaning'}
    )[['word', 'furigana', 'meaning']].to_dict(orient='records')

    merged = jap_dict + kaishi_dict

    return merged


def lookup_meaning(word):
    res = jam.lookup_iter(word)
    first_entry = next(iter(res.entries), None)
    if first_entry:
        entry_str = str(first_entry)
        # Use regex to capture text between ':' and '(('
        match = re.search(r':(.*?)\(\(', entry_str)
        if match:
            meaning = match.group(1).strip()
            # Remove numbering like "1. ", "2. ", etc.
            meaning = re.sub(r'(?:^|[;/])\s*\d+\.\s*', lambda m: m.group(0)[0] if m.group(0)[0] in ';/ ' else '',
                             meaning)
            return meaning.strip()
    return ""


def search_words(merged_dict, input_text):
    result = ""
    kanji_only_text = filter_kana(input_text)
    seen_kanji = set()
    for k in kanji_only_text:
        if k in seen_kanji:
            continue
        seen_kanji.add(k)
        found = [entry for entry in merged_dict if k in entry['word']]
        if found:
            word_width = max(len(entry.get('word', "")) for entry in found)
            furi_width = max([0] + [len(entry.get('furigana', "")) for entry in found])
            meaning_width = max([0] + [len(entry.get('meaning', "")) for entry in found])
            # Kanji header
            result += f"{k}\n"
            for entry in found:
                word = entry.get('word', "")
                furigana = entry.get('furigana', "")
                meaning = entry.get('meaning', "")

                # If meaning is missing, attempt to look it up
                if not meaning:
                    meaning = lookup_meaning(word)
                    entry['meaning'] = meaning  # Optionally update the dictionary

                full = " ".join([word, furigana, meaning]).strip()
                full = f"({full})"
                result += (
                    f"{word.ljust(word_width)}   "
                    f"{furigana.ljust(furi_width)}   "
                    f"{meaning.ljust(meaning_width)}   "
                    f"{full}\n"
                )
            result += f"\n"
        else:
            result += f"{k} NOT FOUND\n\n"
    return result


def leaches_main():
    kanji_dict = read_xlsx()

    def on_search(event=None):  # Accept optional event parameter for key binding
        entered = entry.get()
        output.delete("1.0", tk.END)
        result = search_words(kanji_dict, entered)
        output.insert("1.0", result)

    root = tk.Tk()
    root.title("Kanji Leach Search")
    root.attributes('-fullscreen', True)  # Make full screen
    root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))  # Exit full screen with Es

    label_font = ("Arial", 28)
    entry_font = ("Arial", 28)
    button_font = ("Arial", 24)
    output_font = ("Arial", 25)

    tk.Label(root, text="Enter word:", font=label_font).pack(pady=12)
    entry = tk.Entry(root, font=entry_font)
    entry.pack(fill=tk.X, padx=20, pady=10)
    entry.bind("<Return>", on_search)  # Bind Enter key to call on_search
    tk.Button(root, text="Search", font=button_font, command=on_search).pack(pady=10)
    output = scrolledtext.ScrolledText(root, width=60, height=20, font=output_font)
    output.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    root.mainloop()
