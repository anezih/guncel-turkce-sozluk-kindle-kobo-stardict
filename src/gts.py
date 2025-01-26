import argparse
import gzip
import html
import json
import re
import subprocess
import tarfile
from datetime import datetime
from enum import Enum
from functools import cached_property
from itertools import zip_longest
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template
from pyglossary.glossary_v2 import Glossary
from spylls.hunspell.data.aff import Aff
from spylls.hunspell.data.dic import Word
from spylls.hunspell.dictionary import Dictionary

SURUM = (2, 4, 3)
BETIK_DY = Path(__file__).resolve().parent

def html_escape(metin: str) -> str:
    return html.escape(metin)

# https://github.com/anezih/add_inflections/blob/c58b98de4b65eff357427849533bb05139481806/add_inflections.py#L43
class InflBase:
    def __init__(self, source_path: str, glos_format: str = "") -> None:
        self.source_path = source_path
        self.glos_format = glos_format

    @cached_property
    def path(self) -> Path:
        return Path(self.source_path).resolve()

    @cached_property
    def InflDict(self) -> dict[str,list[str]]:
        raise NotImplementedError

    def get_infl(self, word: str, pfx: bool = False, cross: bool = False) -> set[str]:
        raise NotImplementedError

class Unmunched(InflBase):
    @cached_property
    def InflDict(self) -> dict[str,dict[str,list[str]]]:
        if not self.path.exists():
            raise FileNotFoundError(f"Couldn't find Unmunched dictionary at: {self.source_path}")
        temp: list[dict[str,dict[str,list[str]]]] = list()
        if self.path.name.endswith(".gz"):
            try:
                with gzip.open(self.path, "rt", encoding="utf-8") as f:
                    temp: list[dict[str,dict[str,list[str]]]] = json.load(f)
            except:
                raise Exception("[!] Couldn't open gzipped json file. Check the filename/path.")
        elif self.path.name.endswith(".json"):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    temp: list[dict[str,dict[str,list[str]]]] = json.load(f)
            except:
                raise Exception("[!] Couldn't open json file. Check the filename/path.")
        _infl_dict: dict[str,dict[str, list[str]]] = dict()
        for it in temp:
            for key, val in it.items():
                if key in _infl_dict.keys():
                    _infl_dict[key]["PFX"]   += val["PFX"]
                    _infl_dict[key]["SFX"]   += val["SFX"]
                    _infl_dict[key]["Cross"] += val["Cross"]
                else:
                    _infl_dict[key] = val
        return _infl_dict

    def get_infl(self, word: str, pfx: bool = False, cross: bool = False) -> set[str]:
        afx = set()
        afx_dict = self.InflDict.get(word)
        if afx_dict:
            afx.update(afx_dict["SFX"])
            if pfx:
                afx.update(afx_dict["PFX"])
            if cross:
                afx.update(afx_dict["Cross"])
        return afx

class InflGlosSource(InflBase):
    @cached_property
    def InflDict(self) -> dict[str,set[str]]:
        if not self.path.exists():
            raise FileNotFoundError(f"Couldn't find InflGlosSource dictionary at: {self.source_path}")
        glos = Glossary()
        if self.glos_format:
            glos.directRead(filename=str(self.path), format=self.glos_format)
        else:
            glos.directRead(filename=str(self.path))
        _infl_dict: dict[str,set[str]] = dict()
        for entry in glos:
            if len(entry.l_word) > 1:
                headword = entry.l_word[0]
                if headword in _infl_dict.keys():
                    _infl_dict[headword].update(entry.l_word[1:])
                else:
                    _infl_dict[headword] = set(entry.l_word[1:])
        return _infl_dict

    def get_infl(self, word: str, pfx: bool = False, cross: bool = False) -> set[str]:
        return self.InflDict.get(word, set())

class HunspellDic(InflBase):
    # Taken from: https://gist.github.com/zverok/c574b7a9c42cc17bdc2aa396e3edd21a
    def unmunch(self, word: Word, aff: Aff) -> dict[str,dict[str,set[str]]]:
        result = {
            word.stem : {
                "PFX"   : set(),
                "SFX"   : set(),
                "Cross" : set()
            }
        }

        if aff.FORBIDDENWORD and aff.FORBIDDENWORD in word.flags:
            return result

        suffixes = [
            suffix
            for flag in word.flags
            for suffix in aff.SFX.get(flag, [])
            if suffix.cond_regexp.search(word.stem)
        ]
        prefixes = [
            prefix
            for flag in word.flags
            for prefix in aff.PFX.get(flag, [])
            if prefix.cond_regexp.search(word.stem)
        ]

        for suffix in suffixes:
            root = word.stem[0:-len(suffix.strip)] if suffix.strip else word.stem
            suffixed = root + suffix.add
            if not (aff.NEEDAFFIX and aff.NEEDAFFIX in suffix.flags):
                result[word.stem]["SFX"].add(suffixed)

            secondary_suffixes = [
                suffix2
                for flag in suffix.flags
                for suffix2 in aff.SFX.get(flag, [])
                if suffix2.cond_regexp.search(suffixed)
            ]
            for suffix2 in secondary_suffixes:
                root = suffixed[0:-len(suffix2.strip)] if suffix2.strip else suffixed
                result[word.stem]["SFX"].add(root + suffix2.add)

        for prefix in prefixes:
            root = word.stem[len(prefix.strip):]
            prefixed = prefix.add + root
            if not (aff.NEEDAFFIX and aff.NEEDAFFIX in prefix.flags):
                result[word.stem]["PFX"].add(prefixed)

            if prefix.crossproduct:
                additional_suffixes = [
                    suffix
                    for flag in prefix.flags
                    for suffix in aff.SFX.get(flag, [])
                    if suffix.crossproduct and not suffix in suffixes and suffix.cond_regexp.search(prefixed)
                ]
                for suffix in suffixes + additional_suffixes:
                    root = prefixed[0:-len(suffix.strip)] if suffix.strip else prefixed
                    suffixed = root + suffix.add
                    result[word.stem]["Cross"].add(suffixed)

                    secondary_suffixes = [
                        suffix2
                        for flag in suffix.flags
                        for suffix2 in aff.SFX.get(flag, [])
                        if suffix2.crossproduct and suffix2.cond_regexp.search(suffixed)
                    ]
                    for suffix2 in secondary_suffixes:
                        root = suffixed[0:-len(suffix2.strip)] if suffix2.strip else suffixed
                        result[word.stem]["Cross"].add(root + suffix2.add)
        return result

    @cached_property
    def InflDict(self) -> dict[str,dict[str,list[str]]]:
        if not self.path.exists():
            raise FileNotFoundError(f"Couldn't find Hunspell dictionary at: {self.source_path}")
        base_name = self.path.parent / self.path.stem
        hunspell_dictionary = Dictionary.from_files(str(base_name))
        aff: Aff = hunspell_dictionary.aff
        all_words: list[Word] = hunspell_dictionary.dic.words
        results: list[dict[str,dict[str,set[str]]]] = list()
        for word in all_words:
            unmunched = self.unmunch(word, aff)
            if any([unmunched[word.stem]["SFX"], unmunched[word.stem]["PFX"], unmunched[word.stem]["Cross"]]):
                results.append(unmunched)

        _infl_dict: dict[str,dict[str, set[str]]] = dict()
        for it in results:
            for key, val in it.items():
                if key in _infl_dict.keys():
                    _infl_dict[key]["PFX"].update(val["PFX"])
                    _infl_dict[key]["SFX"].update(val["SFX"])
                    _infl_dict[key]["Cross"].update(val["Cross"])
                else:
                    _infl_dict[key] = val
        return _infl_dict

    def get_infl(self, word: str, pfx: bool = False, cross: bool = False) -> set[str]:
        afx = set()
        afx_dict = self.InflDict.get(word)
        if afx_dict:
            afx.update(afx_dict["SFX"])
            if pfx:
                afx.update(afx_dict["PFX"])
            if cross:
                afx.update(afx_dict["Cross"])
        return afx

class CekimSozlukleri:
    def __init__(self, sozlukler: list[InflBase]) -> None:
        self.sozlukler = sozlukler

    def __call__(self, sozcuk: str) -> set[str]:
        cikti: set[str] = set()
        for cekim_sozluk in self.sozlukler:
            cikti.update(cekim_sozluk.get_infl(sozcuk))
        if sozcuk in cikti:
            cikti.remove(sozcuk)
        return cikti

class DuzeltmeImi:
    def __init__(self) -> None:
        self.tablo = str.maketrans(
            {
                "Â" : "A", "â" : "a",
                "Û" : "U", "û" : "u",
                "Î" : "İ", "î" : "i"
            }
        )

    def __call__(self, metin: str) -> str:
        return metin.translate(self.tablo)

class Ornek:
    def __init__(self, ornek_sozluk: dict) -> None:
        self.ornek_sozluk = ornek_sozluk

    @cached_property
    def ornek_sira(self) -> int:
        return int(self.ornek_sozluk["ornek_sira"])

    @cached_property
    def ornek(self) -> str:
        return self.ornek_sozluk["ornek"]

    @cached_property
    def yazar(self) -> str:
        if _yazar:=self.ornek_sozluk.get("yazar"):
            return _yazar[0]["tam_adi"]

class Anlam:
    def __init__(self, anlam_sozluk: dict, bStarDict: bool = False) -> None:
        self.anlam_sozluk = anlam_sozluk
        self.bStarDict = bStarDict

    @cached_property
    def anlam_sira(self) -> int:
        return int(self.anlam_sozluk["anlam_sira"])

    @cached_property
    def fiil(self) -> bool:
        if self.anlam_sozluk["fiil"] == "1":
            return True
        return False

    @cached_property
    def ozelliklerListe(self) -> list[str]:
        ozellikler: list[str] = list()
        if _ozelliklerListe:=self.anlam_sozluk.get("ozelliklerListe"):
            for o in _ozelliklerListe:
                ozellikler.append(o["tam_adi"])
        return ozellikler

    @cached_property
    def orneklerListe(self) -> list[Ornek]:
        ornekler: list[Ornek] = list()
        if _ornekler:=self.anlam_sozluk.get("orneklerListe"):
            ornekler = [Ornek(x) for x in _ornekler]
            ornekler.sort(key=lambda x: x.ornek_sira)
        return ornekler

    @cached_property
    def anlam(self) -> str:
        return self.anlam_sozluk["anlam"].strip()

    @cached_property
    def anlam_gonderme_baglantili(self) -> str:
        baglanti_simge = "↗" if self.bStarDict else ""
        res = re.search(r"(?:;|►|bk\.)\s?([^.:]+)", self.anlam)
        if not res:
            return self.anlam
        yeni_tanim = f"{self.anlam}"
        gonderme_yapilanlar_temp = [sozcuk.strip() for sozcuk in res.group(1).split(",")]
        gonderme_yapilanlar = []
        for i in gonderme_yapilanlar_temp:
            if " (" in i:
                gonderme_yapilanlar.append(i[:i.index(" (")])
            else:
                gonderme_yapilanlar.append(i)
        gonderme_yapilanlar.sort(
            key = lambda x: len(x),
            reverse = True
        )
        for j in gonderme_yapilanlar:
            yeni_tanim = yeni_tanim.replace(
                j,
                f'{baglanti_simge} <a href="bword://{html.escape(j)}">{j}</a>',
                1
            ).replace("► ","")
        return yeni_tanim

class Girdi:
    def __init__(self, json_girdisi: dict[str,str], duzeltme_imi: DuzeltmeImi,
                 cekim_sozlukleri: CekimSozlukleri, tpl: Template, bStarDict: bool = False) -> None:
        self.json_girdisi = json_girdisi
        self.duzeltme_imi = duzeltme_imi
        self.cekim_sozlukleri = cekim_sozlukleri
        self.tpl = tpl
        self.bStarDict = bStarDict

    @property
    def anlam_html(self) -> str:
        html = self.tpl.render({"Girdi" : self}).replace("\n","")
        html = re.sub(r"\s{2,}", " ", html)
        return html

    @property
    def diger_bicimler(self) -> set[str]:
        cikti: set[str] = set()
        cikti.update([*self.cekim_sozlukleri(self.madde), *self.cekim_sozlukleri(self.madde_imsiz)])
        cikti.add(self.madde_imsiz)
        if self.madde in cikti:
            cikti.remove(self.madde)
        return cikti

    @property
    def l_word(self) -> list[str]:
        cikti = [self.madde, *self.diger_bicimler]
        return cikti

    @cached_property
    def on_taki(self) -> str:
        return self.json_girdisi["on_taki"].strip()

    @cached_property
    def taki(self) -> str:
        return self.json_girdisi["taki"].strip()

    @cached_property
    def madde(self) -> str:
        return self.json_girdisi["madde"].strip()

    @cached_property
    def madde_imsiz(self) -> str:
        return self.duzeltme_imi(self.madde)

    @cached_property
    def cogul_mu(self) -> bool:
        if self.json_girdisi["cogul_mu"] == "1":
            return True
        return False

    @cached_property
    def ozel_mi(self) -> bool:
        if self.json_girdisi["ozel_mi"] == "1":
            return True
        return False

    @cached_property
    def lisan(self) -> str:
        if dil:=self.json_girdisi["lisan"]:
            return dil.strip()

    @cached_property
    def telaffuz(self) -> str:
        return self.json_girdisi["telaffuz"].strip()

    @cached_property
    def birlesikler(self) -> list[str]:
        cikti: list[str] = list()
        if _birlesikler:=self.json_girdisi["birlesikler"]:
            cikti = [
                x.strip()
                for x in _birlesikler.split(",")
            ]
        return cikti

    @cached_property
    def atasozu(self) -> list[str]:
        cikti: list[str] = list()
        if a:=self.json_girdisi.get("atasozu"):
            cikti = [
                x["madde"].strip()
                for x in a
            ]
        return cikti

    @cached_property
    def anlam(self) -> list[Anlam]:
        cikti: list[Anlam] = list()
        if _anlamlarListe:=self.json_girdisi.get("anlamlarListe"):
            cikti = [Anlam(_anlamlar, self.bStarDict) for _anlamlar in _anlamlarListe]
            cikti.sort(key=lambda x: x.anlam_sira)
        return cikti

class CiktiSecenegi(Enum):
    StarDict = 1
    StarDictWebKit = 2
    Kobo = 3
    Kindle = 4

class GTS:
    def __init__(self, gts_json: Path, cekim_sozlukleri: list[str],
                 cekim_sozlukleri_bicimleri: list[str],
                 hunspell_sozlukleri: list[str], cikti_secenegi: int) -> None:
        self.gts_json = gts_json
        self.cekim_sozlukleri = cekim_sozlukleri
        self.cekim_sozlukleri_bicimleri = cekim_sozlukleri_bicimleri
        self.hunspell_sozlukleri = hunspell_sozlukleri
        self.cikti_secenegi = CiktiSecenegi(cikti_secenegi)

    @cached_property
    def bStarDict(self) -> bool:
        if self.cikti_secenegi == CiktiSecenegi.StarDict:
            return True
        return False

    @cached_property
    def InflDicts(self) -> list[InflBase]:
        infl_dicts: list[InflBase] = list()
        infl_dicts.append(Unmunched(BETIK_DY / "tr_TR.json.gz"))
        if self.cekim_sozlukleri:
            for c,cb in zip_longest(self.cekim_sozlukleri, self.cekim_sozlukleri_bicimleri):
                infl_dicts.append(
                    InflGlosSource(c,cb)
                )
        if self.hunspell_sozlukleri:
            for hu in self.hunspell_sozlukleri:
                infl_dicts.append(
                    HunspellDic(hu)
                )
        return infl_dicts

    @cached_property
    def CekimSozlukleri(self) -> CekimSozlukleri:
        return CekimSozlukleri(self.InflDicts)

    @cached_property
    def DuzeltmeImi(self) -> DuzeltmeImi:
        return DuzeltmeImi()

    @cached_property
    def GtsJSON(self) -> dict:
        dizi: list[dict[str,str]] = list()
        with tarfile.open(self.gts_json, "r:gz") as f:
            _json = f.extractfile("gts.json")
            if _json.read(1).decode() == "[":
                _json.seek(0,0)
                dizi = json.load(_json)
            else:
                _json.seek(0,0)
                for i in _json.readlines():
                    dizi.append(json.loads(i))
        cikarilacaklar = list()
        for e in dizi:
            if not e['madde']:
                cikarilacaklar.append(e)
        for c in cikarilacaklar:
            dizi.remove(c)
        dizi.sort(key=lambda x: (x["madde"].strip().encode("utf-8").lower(), x["madde"].strip()))
        return dizi

    @cached_property
    def tpl(self) -> Template:
        env = Environment(loader=FileSystemLoader(BETIK_DY / "tpl"),
                          trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=False)
        env.filters["HtmlEscape"] = html_escape
        match self.cikti_secenegi:
            case CiktiSecenegi.StarDict:
                return env.get_template("stardict.html.j2")
            case CiktiSecenegi.StarDictWebKit:
                return env.get_template("stardict_webkit.html.j2")
            case CiktiSecenegi.Kobo:
                return env.get_template("inline.html.j2")
            case CiktiSecenegi.Kindle:
                return env.get_template("inline.html.j2")

    def bos_glossary(self) -> Glossary:
        glossary = Glossary()
        glossary.setInfo("title", "Güncel Türkçe Sözlük")
        glossary.setInfo("author", "https://github.com/anezih")
        glossary.setInfo("description", f"TDK Güncel Türkçe Sözlük | Sürüm: {'.'.join(map(str, SURUM))}")
        glossary.setInfo("date", f"{datetime.today().strftime('%d/%m/%Y')}")
        glossary.sourceLangName = "tr"
        glossary.targetLangName = "tr"
        return glossary

    def css_ekle(self, glossary: Glossary) -> None:
        def ekle(css_path: Path):
            glossary.addEntry(
                glossary.newDataEntry(
                    css_path.name, css_path.read_bytes()
                )
            )
        match self.cikti_secenegi:
            case CiktiSecenegi.StarDict:
                return ekle(BETIK_DY / "tpl" / "stardict_bicem.css")
            case CiktiSecenegi.StarDictWebKit:
                return ekle(BETIK_DY / "tpl" / "stardict_webkit_bicem.css")
            case _:
                return

    def glossary(self) -> Glossary:
        glos = self.bos_glossary()
        girdiler = [
            Girdi(
                json_girdisi=x,
                duzeltme_imi=self.DuzeltmeImi,
                cekim_sozlukleri=self.CekimSozlukleri,
                tpl=self.tpl,
                bStarDict=self.bStarDict
            )
            for x in self.GtsJSON
        ]
        for girdi in girdiler:
            glos.addEntry(
                glos.newEntry(
                    word=girdi.l_word,
                    defi=girdi.anlam_html,
                    defiFormat="h"
                )
            )
        self.css_ekle(glos)
        return glos

    @cached_property
    def cikti_klasoru_ismi(self) -> str:
        surum_str = '.'.join(map(str, SURUM))
        match self.cikti_secenegi:
            case CiktiSecenegi.StarDict:
                return f"GTSv{surum_str}_Stardict"
            case CiktiSecenegi.StarDictWebKit:
                return f"GTSv{surum_str}_StardictWebKit"
            case CiktiSecenegi.Kobo:
                return f"GTSv{surum_str}_Kobo"
            case CiktiSecenegi.Kindle:
                return f"GTSv{surum_str}_Kindle"

    def stardict(self) -> None:
        glossary = self.glossary()
        klasor = BETIK_DY / self.cikti_klasoru_ismi
        dosya_ismi = klasor / self.cikti_klasoru_ismi
        if not klasor.exists():
            klasor.mkdir()
        glossary.write(str(dosya_ismi), "Stardict", dictzip=False)
        # koreader res/ klasöründeki css dosyasını okuyamıyor.
        css_path = klasor / "res" / "stardict_bicem.css"
        css_uste = klasor / f"{dosya_ismi.name}.css"
        css_uste.write_text(css_path.read_text("utf-8"), "utf-8")
        # boox res/ klasöründeki css dosyasını okuyamıyor, css ismini aynı tutarak üst klasöre kopyalayalım.
        (klasor / css_path.name).write_text(css_path.read_text("utf-8"), "utf-8")

    def stardict_webkit(self) -> None:
        glossary = self.glossary()
        klasor = BETIK_DY / self.cikti_klasoru_ismi
        dosya_ismi = klasor / self.cikti_klasoru_ismi
        if not klasor.exists():
            klasor.mkdir()
        glossary.write(str(dosya_ismi), "Stardict", dictzip=False)

    def kobo(self) -> None:
        glossary = self.glossary()
        klasor = BETIK_DY / self.cikti_klasoru_ismi
        dosya_ismi = klasor / f"{self.cikti_klasoru_ismi}.df"
        if not klasor.exists():
            klasor.mkdir()
        glossary.write(str(dosya_ismi), "Dictfile")
        df_satirlar = dosya_ismi.read_text(encoding="utf-8").split("\n")
        df_satirlar_yeni: list[str] = list()
        for satir in df_satirlar:
            if satir.startswith("@"):
                df_satirlar_yeni.append(satir.replace("\"", "'"))
            else:
                df_satirlar_yeni.append(satir)
        dosya_ismi.write_text("\n".join(df_satirlar_yeni), encoding="utf-8")
        subprocess.Popen(["dictgen-windows.exe", str(dosya_ismi),
                          "-o", str(klasor / "dicthtml-tr.zip")],
                          stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def kindle(self) -> None:
        glossary = self.glossary()
        klasor = BETIK_DY / self.cikti_klasoru_ismi
        dosya_ismi = klasor / self.cikti_klasoru_ismi
        if not klasor.exists():
            klasor.mkdir()
        glossary.write(str(dosya_ismi), "Mobi", kindlegen_path="kindlegen")
        mobi_dosya_yolu = dosya_ismi / "OEBPS" / "content.mobi"
        if mobi_dosya_yolu.exists():
            mobi_dosya_yolu.replace(klasor / f"{self.cikti_klasoru_ismi}.mobi")

    def main(self) -> None:
        match self.cikti_secenegi:
            case CiktiSecenegi.StarDict:
                self.stardict()
            case CiktiSecenegi.StarDictWebKit:
                self.stardict_webkit()
            case CiktiSecenegi.Kobo:
                self.kobo()
            case CiktiSecenegi.Kindle:
                self.kindle()

class ArgparseNS:
    gts_json: Path|str = BETIK_DY / "gts.json.tar.gz"
    cekim_sozlukleri: list[str] = list()
    cekim_sozlukleri_bicimleri: list[str] = list()
    hunspell_sozlukleri: list[str] = list()
    cikti_secenegi: int = 1

if __name__ == '__main__':
    Glossary.init()
    parser = argparse.ArgumentParser(description=
    """
    TDK Güncel Türkçe Sözlük gts.json.tar.gz dosyasını
    PyGlossary aracılığıyla StarDict, Kobo ve Kindle formatlarına çeviren bir Python betiği.
    """)
    parser.add_argument("-j", "--json-tar-gz-path", default=BETIK_DY / "gts.json.tar.gz",
                        help="gts.json.tar.gz konumu.", dest="gts_json")
    parser.add_argument("--cekim-sozlukleri", help="""Sözcük çekimleri için kullanılacak ek sözlüklerin
                        yolları. Birden fazla dosya yolunu boşluk ile ayırın.""", nargs="+",
                        dest="cekim_sozlukleri")
    parser.add_argument("--cekim-sozlukleri-bicimleri", help="""--cekim-sozlukleri seçeneğinde kullanılan
                        kaynakların biçimleri, birden fazla kaynak biçimini boşluk ile ayırın.""", nargs="+",
                        dest="cekim_sozlukleri_bicimleri")
    parser.add_argument("--hunspell-sozlukleri", help="""Çekim bilgilerinin alınacağı Hunspell
                        dosyalarından .aff ve .dic dosyasının konumu. Birden fazla dosya yolunu boşluk ile ayırın.""",
                        nargs="+", dest="hunspell_sozlukleri")
    parser.add_argument("-b", "--cikti-bicimi", help="""Çıktı biçimi. StarDict = 1, StarDict (WebKit) = 2,
                        Kobo = 3, Kindle = 4. StarDict biçimini Webkit tabanlı bir görüntüleyicide
                        kullanacaksanız (GoldenDict gibi) 2'yi seçin.""", type=int, choices=[1,2,3,4], dest="cikti_secenegi")
    args = parser.parse_args(namespace=ArgparseNS)
    gts = GTS(
        gts_json=args.gts_json,
        cekim_sozlukleri=args.cekim_sozlukleri,
        cekim_sozlukleri_bicimleri=args.cekim_sozlukleri_bicimleri,
        hunspell_sozlukleri=args.hunspell_sozlukleri,
        cikti_secenegi=args.cikti_secenegi
    )
    gts.main()