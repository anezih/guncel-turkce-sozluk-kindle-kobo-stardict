from hunspell import Hunspell
import argparse
import html
import json
import os
import sys
    
def fix_quotes(text):
    text = text.replace("'","’")
    out = []
    is_first_found = False
    for char in text:
        if char == '`':
            new_char = '‘' if not is_first_found else '’ '
            is_first_found = True
        else:
            new_char = char
        out.append(new_char)
    return ''.join(out).strip()
    
def local_json(fname):
    arr = []
    with open(fname, "r", encoding="utf-8") as f:
        for i in f:
            arr.append(json.loads(i))
    return arr
    
def create_gls(dictionary, hunspell_1_dir, hunspell_2_dir):
    if hunspell_1_dir and os.path.exists(os.path.join(hunspell_1_dir, "tr_TR.dic")):
        h1 = Hunspell('tr_TR', hunspell_data_dir=hunspell_1_dir)
    else:
        try:
            h1 = Hunspell('tr_TR', hunspell_data_dir=os.getcwd())
        except Exception as e:
            print(f"\nHunspell dosyaları bulunamadı! Dosyaların betikle aynı konumda olup olmadığını veya girdiğiniz dosya yolunu kontrol ediniz.\n{e}\n")
            sys.exit(1)
    if hunspell_2_dir and os.path.exists(os.path.join(hunspell_2_dir, "tr_TR.dic")):
        h2 = Hunspell('tr_TR', hunspell_data_dir=hunspell_2_dir)
    
    fname = "Guncel_Turkce_Sozluk.gls"
    f = open(fname, "w", encoding="utf-8", newline="")
    f.write("\n#stripmethod=keep\n#sametypesequence=h\n#bookname=Güncel Türkçe Sözlük\n#author=https://github.com/anezih\n#description=TDK Güncel Türkçe Sözlük\n\n")
    
    for it in dictionary:
        if not it.get("anlamlarListe"):
            continue
        entry = f'<p style="margin-left:1em">'
        features = f''
        if it["telaffuz"]:
            features += f'<span style="color:#696969">/{it["telaffuz"]}/</span>'
        if it["lisan"]:
            features += f'{"<br/>" if len(features) > 1 else ""}<span style="color:#696969"> Orijin:</span> {it["lisan"]}'
        if it["cogul_mu"] == "1":
            features += f'{"<br/>" if len(features) > 1 else ""}<span style="color:#696969">[ÇOĞUL]</span>' 
        if it["ozel_mi"] == "1":
            features += f'{"<br/>" if "[ÇOĞUL]" not in features else ""}<span style="color:#696969">[ÖZEL]</span>'
        if len(features) > 1:
            entry += f"{features}<br/><br/>"
        anlamlar = f''
        on_taki = ""
        taki = ""
        if it["on_taki"]:
            on_taki = f'{it["on_taki"]} '
        if it["taki"]:
            taki = f', -{it["taki"]}'
        if on_taki or taki:    
            anlamlar += f'<b>{on_taki}{it["madde"]}{taki}</b><br/>'
        for idx, a in enumerate(it["anlamlarListe"], start=1):
            anlam = f''
            if len(it["anlamlarListe"]) > 1:
                anlam += f'<span>{idx}) </span>'
            if a.get("fiil") == "1":
                anlam += f'<span style="color:#696969">[FİİL] </span>'
            if a.get("ozelliklerListe"):
                ozellikler = ""
                for i in a.get("ozelliklerListe"):
                    ozellikler += f'<i>{i["tam_adi"]}{", " if i != a["ozelliklerListe"][-1] else ""}</i>'
                if len(ozellikler) > 1:
                    anlam += f'<span style="color:#696969">[{ozellikler}]</span> '
            anlam += f'{fix_quotes(a["anlam"])}<br/>'
            if a.get("orneklerListe"):
                for i in a.get("orneklerListe"):
                    anlam += f'<br/><span style="margin-left:1.3em;margin-right:1.3em">▪ <i>{i["ornek"]}</i></span><br/>'
                    if i.get("yazar"):
                        anlam += f'<span style="margin-left:1.3em">—{i["yazar"][0]["tam_adi"]}</span><br/>'
            anlamlar += f'{anlam}<br/>'
        entry += anlamlar
        if it.get("atasozu"):
            entry += f'<span><b>Atasözleri, Deyimler veya Birleşik Fiiller</b></span><br/><span>→ '
            atasozu = [f'<a href="bword://{html.escape(i["madde"])}">{i["madde"]}</a>' for i in it["atasozu"]]
            entry += f'{", ".join(atasozu)} </span><br/>'
        if it.get("birlesikler"):
            entry += f'<span><b>Birleşik Kelimeler</b></span><br/><span>→ '
            birlesikler_temp = [i.strip() for i in it["birlesikler"].split(",")]
            birlesikler = [f'<a href="bword://{html.escape(i)}">{i}</a>' for i in birlesikler_temp]
            entry += f'{", ".join(birlesikler)} </span><br/>'
        entry += f"</p>"
        madde = it["madde"]
        suffixes = h1.suffix_suggest(madde)
        if hunspell_2_dir:
            suffixes += h2.suffix_suggest(madde)
            suffixes = list(set(suffixes))
        if suffixes:
            hw = f"{madde}|"
            hw += "|".join(suffixes)
            f.write(f"{hw}\n{entry}\n\n")
        else:
            f.write(f"{madde}\n{entry}\n\n")
    f.close()
    print(f"Created {fname}")    
                 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
    """
    https://github.com/ogun/guncel-turkce-sozluk reposunda bulunan TDK Güncel Türkçe Sözlük json dosyasını (gts.json) 
    biçimlendirerek StarDict sözlüğün hazırlanması için gerekli Babylon GLS dosyaya dönüştüren bir python betiği.
    """)
    parser.add_argument('--json-path', default="gts.json", 
        help="""json dosyasının ismi. Varsayılan isim: gts.json""")
    parser.add_argument('--hunspell-path', default=None, 
        help="""Eğer Hunspell sözlükleri betik ile aynı konumda değilse 
        içinde tr_TR.aff ve tr_TR.dic bulunan Hunspell sözlüklerinin olduğu dosya yolunu ekleyin.""")
    parser.add_argument('--extra-hunspell-path', default=None,
        help="""İkinci bir Hunspell sözlüğünün dosya yolu.""")
    
    args = parser.parse_args()
    local = local_json(args.json_path)
    create_gls(local, args.hunspell_path, args.extra_hunspell_path)