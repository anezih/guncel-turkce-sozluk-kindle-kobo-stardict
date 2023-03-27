import argparse
import gzip
import html
import json
import os
import subprocess
import sys
import tarfile
from copy import deepcopy
from time import sleep

import requests
from pyglossary.glossary_v2 import Glossary
from pyglossary.sort_keys import namedSortKeyList

VERSION = (2, 3)
LAST_ID = 92411

class INFL:
    # https://github.com/anezih/HunspellWordForms
    def __init__(self, unmunched: str) -> None:
        try:
           with gzip.open(unmunched, "rt", encoding="utf-8") as infl:
            temp = json.load(infl)
        except:
            sys.exit("Sözcük çekimlerinin bulunduğu gzip dosyası açılamadı.\ntr_TR.json.gz dosyasının betikle aynı konumda olduğundan emin olun.")
        self.j = {}
        for it in temp:
         for key, val in it.items():
            if key in self.j.keys():
                self.j[key]["SFX"] += val["SFX"]
            else:
                self.j[key] = val

    def get_sfx(self, word: str) -> list:
        word_dict = self.j.get(word)
        if word_dict:
            return word_dict["SFX"]
        else:
            return []

def out_dir(name: str, format: str) -> str:
    folder_name = f"{name}_{format}"
    try:
        if os.path.exists(folder_name):
            return os.path.join(os.getcwd(), folder_name)
        else:
            os.mkdir(folder_name)
            return os.path.join(os.getcwd(), folder_name)
    except:
        print(f"{format} formatı için çıktı klasörü oluşturulamadı.")
        return os.getcwd()

def fix_quotes(text: str) -> str:
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

def fix_df_hws(fname: str) -> None:
    with open(fname, "r", encoding="utf-8") as df:
        _in = df.readlines()
    _out = []
    for line in _in:
        if line.startswith("@"):
            line = line.replace("\"", "'")
            _out.append(line)
        else:
            _out.append(line)
    with open(fname, "w", encoding="utf-8") as df_out:
        for out_line in _out:
            df_out.write(out_line)

def dl_new_entries(num: int) -> list[dict]:
    extra_arr = []
    s = requests.Session()
    headers = {
        "User-Agent": "APIs-Google (+https://developers.google.com/webmasters/APIs-Google.html)"
    }
    url = "https://www.sozluk.gov.tr/gts_id"
    for i in range(num+1, LAST_ID+1):
        try:
            res = s.get(url, params={"id": i}, headers=headers)
            if res.status_code == 200:
                extra_arr.append(res.json()[0])
        except:
            pass
        sleep(1.5)
    return extra_arr

def local_json(fname: str) -> list[dict]:
    arr = []
    with tarfile.open(fname, "r:gz") as f:
        _json = f.extractfile("gts.json").readlines()
    for i in _json:
        arr.append(json.loads(i))
    if (num := len(arr)) < LAST_ID:
        arr += dl_new_entries(num=num)
    return arr
    
def create_dictionaries(dictionary: list[dict], infl: INFL, stardict: bool = False, kobo: bool = False, kindle: bool = False, dictzip: bool = False, dictgen: str = ""):
    Glossary.init()
    glos = Glossary()
    glos.setInfo("title", "Güncel Türkçe Sözlük")
    glos.setInfo("author", "https://github.com/anezih")
    glos.setInfo("description", "TDK Güncel Türkçe Sözlük")
    glos.sourceLangName = "tr"
    glos.targetLangName = "tr"

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
        madde_cekimler = [madde] + infl.get_sfx(madde)
        
        glos.addEntry(
            glos.newEntry(
                word = madde_cekimler, defi=entry, defiFormat="h"
            )
        )
    named = namedSortKeyList[3] # name="stardict"
    # named._replace(name="headword:tr_TR.UTF-8")
    glos._data.setSortKey(namedSortKey=named, sortEncoding="utf-8", writeOptions={})
    glos_kobo   = deepcopy(glos)
    glos_kindle = deepcopy(glos)

    fname = f"GTSv{VERSION[0]}.{VERSION[1]}"
    if stardict:
        stardict_out = os.path.join(out_dir(fname, 'StarDict'), fname)
        glos.write(filename=stardict_out, format="Stardict", dictzip=dictzip, sort=True) # sortKeyName = "headword:tr_TR.UTF-8"
        print(f"*** {fname} StarDict dosyaları oluşturuldu.")
    if kobo:
        kobo_out = os.path.join(out_dir(fname, 'Kobo'), fname)
        glos_kobo.write(filename=kobo_out, format="Dictfile")
        fix_df_hws(kobo_out)
        print(f"*** {fname} Dictfile dosyası oluşturuldu.")
        if dictgen:
            subprocess.Popen([dictgen, kobo_out, "-o", os.path.join(out_dir(fname, 'Kobo'), "dicthtml-tr.zip")], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print(f"    *** Dictfile dosyası dicthtml-tr.zip formatına dönüştürüldü.")
    if kindle:
        print(f"*** {fname} Kindle MOBI dosyası oluşturuluyor, bu işlem biraz zaman alabilir.")
        kindle_out = os.path.join(out_dir(fname, 'Kindle'), fname)
        glos_kindle.write(filename=kindle_out, format="Mobi", kindlegen_path="kindlegen.exe")
        mobi_path = os.path.join(kindle_out, "OEBPS", "content.mobi")
        if os.path.isfile(mobi_path):
            os.rename(mobi_path, os.path.join(out_dir(fname, 'Kindle'), f"{fname}.mobi"))
            print(f"    *** {fname} Kindle MOBI dosyası oluşturuldu.")
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
    """
    https://github.com/ogun/guncel-turkce-sozluk reposunda bulunan TDK Güncel Türkçe Sözlük gts.json.tar.gz dosyasını 
    PyGlossary aracılığıyla StarDict, Kobo ve Kindle formatlarına çeviren bir Python betiği.
    """)
    parser.add_argument('--json-tar-gz-path', default="gts.json.tar.gz", 
        help="""gts.json.tar.gz konumu.""")
    parser.add_argument('--stardict', default=False, action="store_true",
        help="""StarDict çıktı formatı oluşturulsun.""")
    parser.add_argument('--kobo', default=False, action="store_true",
        help="""Kobo dicthtml.zip çıktı formatı oluşturulsun.""")
    parser.add_argument('--kindle', default=False, action="store_true",
        help="""Kindle MOBI çıktı formatı oluşturulsun.""")
    parser.add_argument('--dictzip', default=False, action="store_true",
        help="""StarDict .dict dosyasını sıkıştıracak dictzip aracı PATH'de mi?""")
    parser.add_argument('--dictgen', default="",
        help="""Kobo dicthtml-tr.zip dosyasını oluşturacak aracın (dictgen-*.exe) konumu.""")
    
    args = parser.parse_args()
    local = local_json(args.json_tar_gz_path)
    infl_obj = INFL("tr_TR.json.gz")
    create_dictionaries(dictionary=local, infl=infl_obj, stardict=args.stardict, kobo=args.kobo, kindle=args.kindle, dictzip=args.dictzip, dictgen=args.dictgen)
