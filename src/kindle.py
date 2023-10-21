from pyglossary.glossary_v2 import Glossary

from infl import INFL
from util import fix_quotes, gondermeler

def kindle_glos(glos: Glossary, dictionary: list[dict[str,str]], infl_dicts: list[INFL], normalize) -> Glossary:
    entry_id_pairs: dict[str,str] = {it["madde"].strip() : f"{idx}".zfill(8) for idx, it in enumerate(dictionary, start=1)}
    def a_id_str(madde: str) -> str:
        _id = entry_id_pairs.get(madde.strip())
        if _id:
            return f'<a id="{_id}"></a>'
        return ""
    def get_id(madde: str) -> str:
        return entry_id_pairs.get(madde.strip(), "0")

    for it in dictionary:
        if not it.get("anlamlarListe"):
            continue
        entry = f'{a_id_str(it["madde"])}<p style="margin-left:1em">'
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
            anlam += f'{gondermeler(fix_quotes(a["anlam"]), entry_id_pairs)}<br/>'
            if a.get("orneklerListe"):
                for i in a.get("orneklerListe"):
                    anlam += f'<br/><span style="margin-left:1.3em;margin-right:1.3em">▪ <i>{i["ornek"]}</i></span><br/>'
                    if i.get("yazar"):
                        anlam += f'<span style="margin-left:1.3em">—{i["yazar"][0]["tam_adi"]}</span><br/>'
            anlamlar += f'{anlam}<br/>'
        entry += anlamlar
        if it.get("atasozu"):
            entry += f'<span><b>Atasözleri, Deyimler veya Birleşik Fiiller</b></span><br/><span>→ '
            atasozu = [f'<a href="#{get_id(i["madde"])}">{i["madde"]}</a>' for i in it["atasozu"]]
            entry += f'{", ".join(atasozu)} </span><br/>'
        if it.get("birlesikler"):
            entry += f'<span><b>Birleşik Kelimeler</b></span><br/><span>→ '
            birlesikler_temp = [i.strip() for i in it["birlesikler"].split(",")]
            birlesikler = [f'<a href="#{get_id(i)}">{i}</a>' for i in birlesikler_temp]
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

    return glos