import argparse
import html
import os
import subprocess
from copy import deepcopy
from datetime import datetime

from pyglossary.glossary_v2 import Glossary

from infl import INFL, GlosSource, Unmunched
from kindle import kindle_glos
from util import fix_df_hws, fix_quotes, gondermeler, local_json, out_dir

VERSION = (2, 4, 2)
LAST_ID = 99501
DUZELTME_IMLERI_DICT = {
    "Â" : "A", "â" : "a",
    "Û" : "U", "û" : "u",
    "Î" : "İ", "î" : "i"
}
NORMALIZE = str.maketrans(DUZELTME_IMLERI_DICT)

def create_dictionaries(dictionary: list[dict[str,str]], infl_dicts: list[INFL], stardict: bool = False,
                        kobo: bool = False, kindle: bool = False, dictzip: bool = False, dictgen: str = ""):
    glos = Glossary()
    glos_kindle = None
    glos_kobo   = None
    glos.setInfo("title", "Güncel Türkçe Sözlük")
    glos.setInfo("author", "https://github.com/anezih")
    glos.setInfo("description", f"TDK Güncel Türkçe Sözlük | Sürüm: {'.'.join(map(str, VERSION))}")
    glos.setInfo("date", f"{datetime.today().strftime('%d/%m/%Y')}")
    glos.sourceLangName = "tr"
    glos.targetLangName = "tr"

    if kindle:
        glos_kindle = kindle_glos(deepcopy(glos), dictionary, infl_dicts, normalize=NORMALIZE)

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
            anlam += f'{gondermeler(fix_quotes(a["anlam"]))}<br/>'
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

        if madde != (duzeltme_yok := madde.translate(NORMALIZE)):
            suffixes_set.add(duzeltme_yok)
        if madde in suffixes_set:
            suffixes_set.remove(madde)

        madde_cekimler = [madde] + list(suffixes_set)

        glos.addEntry(
            glos.newEntry(
                word = madde_cekimler, defi=entry, defiFormat="h"
            )
        )

    if kobo:
        glos_kobo = deepcopy(glos)

    fname = f"GTSv{'.'.join(map(str, VERSION))}"
    if stardict:
        stardict_out = os.path.join(out_dir(fname, 'StarDict'), fname)
        glos.write(filename=stardict_out, format="Stardict", dictzip=dictzip)
        print(f"*** {fname} StarDict dosyaları oluşturuldu.")
    if kobo:
        kobo_out = os.path.join(out_dir(fname, 'Kobo'), fname)
        glos_kobo.write(filename=kobo_out, format="Dictfile")
        fix_df_hws(kobo_out)
        print(f"*** {fname} Dictfile dosyası oluşturuldu.")
        if dictgen:
            subprocess.Popen([dictgen, f"{kobo_out}_fixed", "-o", os.path.join(out_dir(fname, 'Kobo'),
                            "dicthtml-tr.zip")], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print(f"    *** Dictfile dosyası dicthtml-tr.zip (Kobo) formatına dönüştürüldü.")
    if kindle:
        print(f"*** {fname} Kindle MOBI dosyası oluşturuluyor, bu işlem biraz zaman alabilir.")
        kindle_out = os.path.join(out_dir(fname, 'Kindle'), fname)
        glos_kindle.write(filename=kindle_out, format="Mobi", kindlegen_path="kindlegen")
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
    local = local_json(args.json_tar_gz_path, LAST_ID=LAST_ID)
    infl_dicts = []
    infl_dicts.append(Unmunched("tr_TR.json.gz"))
    if args.cekim_sozlukler:
        if ";" in args.cekim_sozlukler:
            for cekim_s in args.cekim_sozlukler.split(";"):
                infl_dicts.append(GlosSource(cekim_s))
        else:
            infl_dicts.append(GlosSource(args.cekim_sozlukler))
    create_dictionaries(dictionary=local, infl_dicts=infl_dicts, stardict=args.stardict, kobo=args.kobo,
                        kindle=args.kindle, dictzip=args.dictzip, dictgen=args.dictgen
    )