import gzip
import json
import os
import sys

from pyglossary.glossary_v2 import Glossary


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