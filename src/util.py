import json
import os
import tarfile

import requests


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

def dl_new_entries(num: int, LAST_ID: int, ignore_cache: bool = False,) -> list[dict]:
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

def local_json(fname: str, LAST_ID: int) -> list[dict]:
    arr: list[dict[str,str]] = []
    with tarfile.open(fname, "r:gz") as f:
        _json = f.extractfile("gts.json")
        if _json.read(1).decode() == "[":
            _json.seek(0,0)
            arr = json.load(_json)
        else:
            _json.seek(0,0)
            for i in _json.readlines():
                arr.append(json.loads(i))
    arr.sort(key=lambda x: int(x["madde_id"]))
    if (num := int(arr[-1]["madde_id"])) < LAST_ID:
        arr += dl_new_entries(num=num, LAST_ID=LAST_ID)
    for e in arr:
        if not e['madde']:
            arr.remove(e)
    arr.sort(key=lambda x: (x["madde"].strip().encode("utf-8").lower(), x["madde"].strip()))
    return arr