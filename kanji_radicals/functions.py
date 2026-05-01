import pandas as pd
import re
import tkinter as tk
from tkinter import scrolledtext
from jamdict import Jamdict

kana_set = set()
kana_set.update(chr(code) for code in range(0x3040, 0x30A0))  # Hiragana
kana_set.update(chr(code) for code in range(0x30A0, 0x3100))  # Katakana
jam = Jamdict()


def filter_kana(s):
    """Remove hiragana and katakana from input string."""
    return ''.join(c for c in s if c not in kana_set)


def clean_text(s):
    if isinstance(s, str):
        s = s.lower().replace('+', '').replace(',', '')
        s = re.sub(r'\s+', ' ', s).strip()
    return s


def read_xlsx():
    df = pd.read_excel('kanji_radicals.xlsx')
    for col in ['Meaning', 'Radicals']:
        df[col] = df[col].apply(clean_text)
    kanji_dict = df.set_index('Kanji')[['Meaning', 'Radicals']].to_dict(orient='index')
    return kanji_dict


def search_jamdict(kanji):
    result = ""
    kanji_entry = jam.lookup(kanji)
    c = kanji_entry.chars[0]
    result += f"{c} {' '.join(c.meanings())}\n"

    radicals_ids = jam.krad[kanji]
    radical_names = []
    for radical in radicals_ids:
        radical_entry = jam.lookup(radical)
        for c in radical_entry.chars:
            if c.text == radical:
                radical_names.append(c.meanings()[0])
                break
        else:
            if radical_entry.chars:
                radical_names.append(radical_entry.chars[0].meanings()[0])
    result += " ".join(radical_names)
    return result


def search_kanji(kanji_dict, input_text):
    result = ""
    input_text = filter_kana(input_text)
    for k in input_text:
        if k in kanji_dict:
            result += f"{k} {kanji_dict[k]['Meaning']}\n"
            result += f"{kanji_dict[k]['Radicals']}\n"
        else:
            result += f"{search_jamdict(k)}\n"
    return result


def radicals_main():
    kanji_dict = read_xlsx()

    def on_search(event=None):  # Accept optional event parameter for key binding
        entered = entry.get()
        output.delete("1.0", tk.END)
        result = search_kanji(kanji_dict, entered)
        output.insert("1.0", result)

    root = tk.Tk()
    root.title("Kanji Search")
    root.attributes('-fullscreen', True)  # Make full screen
    root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))  # Exit full screen with Es

    label_font = ("Arial", 28)
    entry_font = ("Arial", 28)
    button_font = ("Arial", 24)
    output_font = ("Arial", 30)

    tk.Label(root, text="Enter kanji:", font=label_font).pack(pady=12)
    entry = tk.Entry(root, font=entry_font)
    entry.pack(fill=tk.X, padx=20, pady=10)
    entry.bind("<Return>", on_search)  # Bind Enter key to call on_search
    tk.Button(root, text="Search", font=button_font, command=on_search).pack(pady=10)
    output = scrolledtext.ScrolledText(root, width=60, height=20, font=output_font)
    output.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    root.mainloop()
