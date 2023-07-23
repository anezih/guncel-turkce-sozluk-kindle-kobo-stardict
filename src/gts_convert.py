import argparse
import gzip
import html
import json
import os
import subprocess
import sys
import tarfile
from copy import deepcopy
from datetime import datetime

import requests
from pyglossary.glossary_v2 import Glossary
from pyglossary.sort_keys import namedSortKeyList

VERSION = (2, 4)
LAST_ID = 99501
DUZELTME_IMLERI_DICT = {
    "Â" : "A", "â" : "a",
    "Û" : "U", "û" : "u",
    "Î" : "İ", "î" : "i"
}
normalize = str.maketrans(DUZELTME_IMLERI_DICT)

class INFL():
    def __init__(self, source: str) -> None:
        self.j = {}
        self.populate_dict(source=source)

    def populate_dict(self, source: str, glos_format: str = "") -> None:
        raise NotImplementedError

    def get_infl(self, word: str) -> list[str]:
        raise NotImplementedError

class Unmunched(INFL):
    def populate_dict(self, source: str) -> None:
        if source.endswith(".gz"):
            try:
                with gzip.open(source, "rt", encoding="utf-8") as f:
                    temp = json.load(f)
            except:
                sys.exit("[!] Gzip ile sıkıştırılmış tr_TR.json.gz dosyası açılamadı.\n Dosya ismini/yolunu kontrol edin.")
        else:
            try:
                with open(source, "r", encoding="utf-8") as f:
                    temp = json.load(f)
            except:
                sys.exit("[!] tr_TR.json dosyası açılamadı.\n Dosya ismini/yolunu kontrol edin.")
        for it in temp:
         for key, val in it.items():
            if key in self.j.keys():
                self.j[key]["SFX"] += val["SFX"]
            else:
                self.j[key] = val

    def get_infl(self, word: str) -> list[str]:
        afx = []
        afx_lst = self.j.get(word)
        if afx_lst:
            afx += afx_lst["SFX"]
        return afx

class GlosSource(INFL):
    def populate_dict(self, source: str) -> None:
        if not os.path.exists(source):
            sys.exit("[!] Çekimler için kaynak olarak kullanılacak sözlük bulunamadı.\n Dosya ismini/yolunu kontrol edin.")
        glos = Glossary()
        glos.directRead(filename=source)
        for entry in glos:
            if len(entry.l_word) < 2:
                continue
            hw = entry.l_word[0]
            if hw in self.j.keys():
                self.j[hw] += entry.l_word[1:]
            else:
                self.j[hw] = entry.l_word[1:]

    def get_infl(self, word: str) -> list[str]:
        return self.j.get(word, [])

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
        with open(f"{fname}_fixed", "w", encoding="utf-8") as df_out:
            for line in df.readlines():
                if line.startswith("@"):
                    line = line.replace("\"", "'")
                    df_out.write(line)
                    df_out.flush()
                else:
                    df_out.write(line)
                    df_out.flush()

def dl_new_entries(num: int, ignore_cache: bool = False) -> list[dict]:
    if os.path.exists(cache_fname := f"{num+1}_{LAST_ID}.json") and not ignore_cache:
        with open(cache_fname, "r", encoding="utf-8") as cache_in:
            return json.load(cache_in)
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
                if res.json().get("error"):
                    continue
                extra_arr.append(res.json()[0])
                print(f"Yeni girdilerden {i}/{LAST_ID} indirildi.", end="\r")
        except:
            pass
    print("\n")
    if extra_arr:
        extra_arr.sort(key=lambda x: int(x["madde_id"]))
        with open(cache_fname, "w", encoding="utf-8") as cache_out:
            json.dump(extra_arr, cache_out, ensure_ascii=False, indent=2)
    return extra_arr

def local_json(fname: str) -> list[dict]:
    arr = []
    with tarfile.open(fname, "r:gz") as f:
        _json = f.extractfile("gts.json")
        if _json.read(1).decode() == "[":
            _json.seek(0,0)
            arr = json.load(_json)
        else:
            for i in _json.readlines():
                arr.append(json.loads(i))
    arr.sort(key=lambda x: int(x["madde_id"]))
    if (num := int(arr[-1]["madde_id"])) < LAST_ID:
        arr += dl_new_entries(num=num)
    return arr

def create_dictionaries(dictionary: list[dict], infl_dicts: list[INFL], stardict: bool = False, kobo: bool = False, kindle: bool = False, dictzip: bool = False, dictgen: str = ""):
    glos = Glossary()
    glos.setInfo("title", "Güncel Türkçe Sözlük")
    glos.setInfo("author", "https://github.com/anezih")
    glos.setInfo("description", f"TDK Güncel Türkçe Sözlük | Sürüm: {VERSION[0]}.{VERSION[1]}")
    glos.setInfo("date", f"{datetime.today().strftime('%d/%m/%Y')}")
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
        madde = it["madde"].strip()

        suffixes_set = {
            _infl
            for infl_dict in infl_dicts
            for _infl in infl_dict.get_infl(word=madde)
        }

        if madde != (duzeltme_yok := madde.translate(normalize)):
            suffixes_set.add(duzeltme_yok)
        if madde in suffixes_set:
            suffixes_set.remove(madde)

        madde_cekimler = [madde] + list(suffixes_set)

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
            subprocess.Popen([dictgen, f"{kobo_out}_fixed", "-o", os.path.join(out_dir(fname, 'Kobo'), "dicthtml-tr.zip")], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print(f"    *** Dictfile dosyası dicthtml-tr.zip (Kobo) formatına dönüştürüldü.")
    if kindle:
        print(f"*** {fname} Kindle MOBI dosyası oluşturuluyor, bu işlem biraz zaman alabilir.")
        kindle_out = os.path.join(out_dir(fname, 'Kindle'), fname)
        glos_kindle.write(filename=kindle_out, format="Mobi", kindlegen_path="kindlegen.exe")
        mobi_path = os.path.join(kindle_out, "OEBPS", "content.mobi")
        if os.path.isfile(mobi_path):
            os.rename(mobi_path, os.path.join(out_dir(fname, 'Kindle'), f"{fname}.mobi"))
            print(f"    *** {fname} Kindle MOBI dosyası oluşturuldu.")

if __name__ == '__main__':
    Glossary.init()
    parser = argparse.ArgumentParser(description=
    """
    TDK Güncel Türkçe Sözlük gts.json.tar.gz dosyasını
    PyGlossary aracılığıyla StarDict, Kobo ve Kindle formatlarına çeviren bir Python betiği.
    """)
    parser.add_argument('--json-tar-gz-path', default="gts.json.tar.gz",
        help="""gts.json.tar.gz konumu.""")
    parser.add_argument('--cekim-sozlukler', default="",
        help="""Sözcük çekimleri için ek Stardict sözlüklerinin dosya yolları. Birden fazla kaynağı noktalı virgül (;) ile ayırın""")
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
    infl_dicts = []
    infl_dicts.append(Unmunched("tr_TR.json.gz"))
    if args.cekim_sozlukler:
        if ";" in args.cekim_sozlukler:
            for cekim_s in args.cekim_sozlukler.split(";"):
                infl_dicts.append(GlosSource(cekim_s))
        else:
            infl_dicts.append(GlosSource(args.cekim_sozlukler))
    create_dictionaries(dictionary=local, infl_dicts=infl_dicts, stardict=args.stardict, kobo=args.kobo, kindle=args.kindle, dictzip=args.dictzip, dictgen=args.dictgen)