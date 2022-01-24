from hunspell import Hunspell
import argparse
import csv
import os
import sqlite3
import sys

sql ="""SELECT  t_madde.madde, lisan, telaffuz, t_anlam.anlam, cogul_mu, ozel_mi, fiil, t_ornek.ornek,  t_yazar.tam_adi, t_ozellik.tam_adi as tur   
FROM madde t_madde INNER JOIN
	 anlam t_anlam USING(madde_id) INNER JOIN
	 anlam_ozellik t_anlam_ozellik USING(anlam_id) LEFT OUTER JOIN
	 ozellik t_ozellik USING(ozellik_id) LEFT OUTER JOIN
	 atasozu t_atasozu USING(madde_id) LEFT OUTER JOIN
	 ornek t_ornek USING(anlam_id) LEFT OUTER JOIN
	 yazar t_yazar USING(yazar_id)
     order by t_madde.madde asc
     """

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

def create_tabfile():
    conn = sqlite3.connect("gts.sqlite3.db")
    conn.row_factory = sqlite3.Row
    with open("temp.tabfile", "w", encoding="utf-8") as f:
        for it in conn.execute(sql):
            entry = f'{it["madde"]}\t<p style="margin-left:1em">'
            right_hs_headword = f''
            if it['tur']:
                right_hs_headword += f'<span style="color:#696969"><i>{it["tur"]}</i></span><br/>'
            if it['telaffuz']:
                right_hs_headword += f'<span style="color:#696969">/{it["telaffuz"]}/</span><br/>'
            if it['lisan']:
                right_hs_headword += f'<span style="color:#696969"> Orijin:</span> {it["lisan"]}<br/>'
            if len(right_hs_headword) > 1:
                entry += f"{right_hs_headword}<br/>"
            plural_proper_verb = f''
            if it['cogul_mu']:
                plural_proper_verb += f'<span style="color:#696969">[ÇOĞUL]</span>' 
            if it['ozel_mi']:
                plural_proper_verb += f'<span style="color:#696969">[ÖZEL]</span>'
            if it['fiil']:
                plural_proper_verb += f'<span style="color:#696969">[FİİL]</span>'
            if len(plural_proper_verb) > 1:
                entry += f"{plural_proper_verb} "
            entry += f'{fix_quotes(it["anlam"])}<br/>'
            if it['ornek']:
                entry += f'<br/><span style="margin-left:1.3em;margin-right:1.3em"><span style="color:#FF0000">▪</span> <i>{it["ornek"]}</i></span><br/>'
                if it['tam_adi']:
                    entry += f'<span style="margin-left:1.3em">—{it["tam_adi"]}</span>'
            entry += f"</p>\n"
            f.write(entry)
    conn.close()

def de_dup(tabfile):
    d = dict()
    with open(tabfile, "r", encoding='utf-8') as tabf:
        tab_reader = csv.reader(tabf, delimiter='\t')
        for row in tab_reader:
            if row[0] in d.keys():
                d[row[0]] = f'{d[row[0]]}<p style="text-align:center">————</p>{row[1]}'
            else:
                d[row[0]] = row[1]
    return d

def write_unique_tabfile(dic):
    fname = "Guncel_Turkce_Sozluk.tabfile"
    with open(fname, "w", encoding="utf-8", newline="") as f:
        for k,v in dic.items():
           f.write(f"{k}\t{v}\n")
    print(f"Created {fname}")

def create_gls(hunspell_dir=None):
    if hunspell_dir and os.path.exists(os.path.join(hunspell_dir, "tr.dic")):
        h = Hunspell('tr', hunspell_data_dir=hunspell_dir)
    else:
        try:
            h = Hunspell('tr', hunspell_data_dir=os.getcwd())
        except Exception as e:
            print(f"\nHunspell dosyaları bulunamadı! Dosyaların betikle aynı konumda olup olmadığını veya girdiğiniz dosya yolunu kontrol ediniz.\n{e}\n")
            sys.exit(1)
    conn = sqlite3.connect("gts.sqlite3.db")
    conn.row_factory = sqlite3.Row
    with_dups = dict()
    wo_dups = dict()
    for it in conn.execute(sql):
        entry = f'<p style="margin-left:1em">'
        right_hs_headword = f''
        if it['tur']:
            right_hs_headword += f'<span style="color:#696969"><i>{it["tur"]}</i></span><br/>'
        if it['telaffuz']:
            right_hs_headword += f'<span style="color:#696969">/{it["telaffuz"]}/</span><br/>'
        if it['lisan']:
            right_hs_headword += f'<span style="color:#696969"> Orijin:</span> {it["lisan"]}<br/>'
        if len(right_hs_headword) > 1:
            entry += f"{right_hs_headword}<br/>"
        plural_proper_verb = f''
        if it['cogul_mu']:
            plural_proper_verb += f'<span style="color:#696969">[ÇOĞUL]</span>' 
        if it['ozel_mi']:
            plural_proper_verb += f'<span style="color:#696969">[ÖZEL]</span>'
        if it['fiil']:
            plural_proper_verb += f'<span style="color:#696969">[FİİL]</span>'
        if len(plural_proper_verb) > 1:
            entry += f"{plural_proper_verb} "
        entry += f'{fix_quotes(it["anlam"])}<br/>'
        if it['ornek']:
            entry += f'<br/><span style="margin-left:1.3em;margin-right:1.3em"><span style="color:#FF0000">▪</span> <i>{it["ornek"]}</i></span><br/>'
            if it['tam_adi']:
                entry += f'<span style="margin-left:1.3em">—{it["tam_adi"]}</span>'
        entry += f"</p>\n"
        with_dups[it["madde"]] = entry
    conn.close()

    for k,v in with_dups.items():
        if k in wo_dups.keys():
            wo_dups[k] = f'{wo_dups[k]}<p style="text-align:center">————</p>{v}'
        else:
            wo_dups[k] = v
    
    fname = "Guncel_Turkce_Sozluk.gls"
    with open(fname, "w", encoding="utf-8", newline="") as f:
        f.write("\n#stripmethod=keep\n#sametypesequence=h\n#bookname=Güncel Türkçe Sözlük\n#author=https://github.com/anezih\n\n")
        for k,v in wo_dups.items():
            if (stem := h.stem(k)) and k == stem[0] and (suffixes := h.suffix_suggest(k)):
                hw = f"{k}|"
                hw += "|".join(suffixes)
                f.write(f"{hw}\n{v}\n")
            else:
                f.write(f"{k}\n{v}\n")
    print(f"Created {fname}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
    """
    https://github.com/ogun/guncel-turkce-sozluk reposunda bulunuan TDK Güncel Türkçe Sözlük veri tabanını (gts.sqlite3.db) 
    biçimlendirerek StarDict sözlüğün hazırlanması için gerekli tab-delimited veya Babylon GLS dosyaya dönüştüren bir python betiği.
    --gls seçeneği belirtilmediği takdirde tab-delimited dosya üretilecektir. Sözcüklerin çekimlenmiş halleri yalnızca *.gls formatında bulunmaktadır.
    """)
    parser.add_argument('--gls', action='store_true', 
        help=""""Tab-delimited dosya yerine *.gls dosyası oluşturmak 
        istiyorsanız bu seçeneği ekleyin. Sözcüklerin çekimlenmiş halleri yalnızca *.gls formatında bulunmaktadır.""")
    parser.add_argument('--hunspell-path', 
        help="""Eğer Hunspell sözlükleri betik ile aynı konumda değilse 
        içinde tr.aff ve tr.dic bulunan Hunspell sözlüklerinin olduğu dosya yolunu ekleyin. """)
    args = parser.parse_args()
    
    if args.gls:
        if p := args.hunspell_path:
            create_gls(p)
        else:
            create_gls()
    else:
        create_tabfile()
        write_unique_tabfile(de_dup("temp.tabfile"))
        if os.path.exists("temp.tabfile"):
            os.remove("temp.tabfile")
