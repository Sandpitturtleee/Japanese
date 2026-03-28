
if __name__ == "__main__":
    # Find all writing components (often called "radicals") of the character
    from jamdict import Jamdict

    jam = Jamdict()
    kanji = '喉'
    results = jam.krad[kanji]
    print(results)

    meaning = jam.lookup(kanji)
    for c in meaning.chars:
        print(c, c.meanings())

    print()
    for i in results:
        result = jam.lookup(i)
        for c in result.chars:
            print(c, c.meanings())
        print()