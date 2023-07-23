# Nedir?
TDK Güncel Türkçe Sözlük gts.json.tar.gz dosyasını PyGlossary aracılığıyla StarDict, Kobo ve Kindle formatlarına çeviren bir Python betiği.

# Kullanımı
`python gts_convert.py --help`
```
usage: gts_convert.py [-h] [--json-tar-gz-path JSON_TAR_GZ_PATH] [--cekim-sozlukler CEKIM_SOZLUKLER] [--stardict]
                      [--kobo] [--kindle] [--dictzip] [--dictgen DICTGEN]

TDK Güncel Türkçe Sözlük gts.json.tar.gz dosyasını PyGlossary aracılığıyla StarDict, Kobo ve Kindle formatlarına
çeviren bir Python betiği.

options:
  -h, --help            show this help message and exit
  --json-tar-gz-path JSON_TAR_GZ_PATH
                        gts.json.tar.gz konumu.
  --cekim-sozlukler CEKIM_SOZLUKLER
                        Sözcük çekimleri için ek Stardict sözlüklerinin dosya yolları. Birden fazla kaynağı noktalı
                        virgül (;) ile ayırın
  --stardict            StarDict çıktı formatı oluşturulsun.
  --kobo                Kobo dicthtml.zip çıktı formatı oluşturulsun.
  --kindle              Kindle MOBI çıktı formatı oluşturulsun.
  --dictzip             StarDict .dict dosyasını sıkıştıracak dictzip aracı PATH'de mi?
  --dictgen DICTGEN     Kobo dicthtml-tr.zip dosyasını oluşturacak aracın (dictgen-*.exe) konumu.
```
gts.json.tar.gz dosyasının ve sözcüklerin çekim bilgilerinin yer aldığı tr_TR.json.gz dosyasının betik ile aynı konumda olduğundan emin olun. (tr_TR.json.gz dosyasının nasıl oluşturulduğunu merak ediyorsanız [bağlantıyı](https://github.com/anezih/HunspellWordForms) takip edin. Üretilen json dosyasının [kaynak Hunspell dosyaları](https://github.com/titoBouzout/Dictionaries/blob/master/Turkish.txt).) (NOT: 2.4 versiyonu öncesinde kaynak olarak kullanılan gts.json.tar.gz dosyasına [buradan](https://github.com/ogun/guncel-turkce-sozluk) ulaşabilirsiniz)

Tüm formatları üretmek için betiği şu şekilde çağırın:

`python gts_convert.py --stardict --kobo --kindle --dictzip --dictgen "dictgen-windows.exe"`

`--cekim-sozlukler` parametresi, var olan sözcük çekim bilgilerini hazırlanan sözlüğe ekleyebilmenizi sağlar. Bu parametreye çekim bilgileri olan StarDict sözlüklerinin yollarını gösterin. Birden fazla sözlük kullanılacaksa bunları noktalı virgül (;) ile ayırın. Örnek:
```
python gts_convert.py --cekim-sozlukler "D:\sozlukler\kaynak_1.ifo;D:\sozlukler\kaynak_2.ifo" --stardict --kobo --kindle --dictzip --dictgen "dictgen-windows.exe"
```

`--dictzip` anahtarı, kullanıldığında dictzip çalıştırılabilir dosyasının PATH'de olduğunu belirtir. (Windows'a yüklemek için: https://github.com/Tvangeste/dictzip-win32)

`--dictgen` parametresi Dictfile dosyasını Kobo dicthtml.zip formatına dönüştüren çalıştırılabilir dosyanın konumunu gösterir. Sisteminiz için uygun dictgen-* programını https://github.com/pgaskin/dictutil adresinden edinebilirsiniz.

# Gerekli paketler
```
pip install pyglossary==4.6.1
pip install requests
```
# Kobo sözlüğünü yükleme
* Sözlüğü `KOBOeReader/.kobo/dict` konumuna kopyalayın.
* `KOBOeReader/.kobo/Kobo/Kobo eReader.conf` dosyasında `ApplicationPreferences` kısmının altına `ExtraLocales=tr` seçeneğini ekleyin.
* Veya sözlüğü doğrudan `KOBOeReader/.kobo/custom-dict` konumuna kopyalayın.
* Kaynak ve detaylı açıklama için [buraya](https://pgaskin.net/dictutil/dicthtml/install.html) başvurun.


<details>
<summary><h1>Ekran Görüntüleri</h1></summary>
<h2>V1</h2>

|                                                          |                                                           |
|:--------------------------------------------------------:|:---------------------------------------------------------:|
|<img src="img/Reader_2022-01-11_203535.png" width="300px">|<img src="img/Reader_2022-01-12_010753.png" width="300px"> |
|KOReader üzerinde Stardict/1                              |KOReader üzerinde Stardict/2                               |
|<img src="img/screen_shot-25906.gif" width="300px">       |<img src="img/screen_shot-25907.gif" width="300px">        |
|Kindle 4 sözlük ön izleme penceresi                       |Kindle 4 sözlük detaylı görünüm                            |
|<img src="img/screen_shot-25904.gif" width="300px">       |                                                           |
|Kindle 4 yüklü Türkçe sözlükler listesi                   |                                                           |

<h2>V2</h2>

**Çekimlenmiş sözcük aransa dahi kök sözcük görüntüleniyor.**

|                                             |                                                   |
|:-------------------------------------------:|:-------------------------------------------------:|
|<img src="img/v2/yapit_v2.png" width="300px">|<img src="img/v2/kobo_yapit_v2.png" width="300px"> |
|V2 - KOReader üzerinde Stardict              |V2 - Kobo                                          |

<h2>V2.1 - Girdilerin Eksik Tanımları Eklendi, Kindle için MOBI dosyası üretildi</h2>

|                                                                  |                                                                              |
|:----------------------------------------------------------------:|:----------------------------------------------------------------------------:|
|<img src="img/v2_1/v2_Reader_2022-03-21_221439.png" width="300px">|<img src="img/v2_1/v2_page1_FileManager_2022-03-21_232914.png" width="300px"> |
|**V2 - Eksik tanımlı bir girdi**                                  |**V2.1 - Girdinin eksik tanımları eklendi/1**                                 |
|<img src="img/v2_1/v2_page2_FileManager_2022-03-21_232924.png" width="300px">|<img src="img/v2_1/v2_page3_FileManager_2022-03-21_232929.png" width="300px">|
|**V2.1 - Girdinin eksik tanımları eklendi/2**                     |**V2.1 - Girdinin eksik tanımları eklendi/3**                                 |
|<img src="img/v2_1/screen_shot-20980.gif" width="300px">|<img src="img/v2_1/screen_shot-20981.gif" width="300px">|
|**V2.1 PyGlossary aracılığıyla Kindle için derlendi,<br/> çekimlenmiş sözcüklerde sonuç dönüyor**| **Kindle üzerinde tanımın detaylı görünümü**|

</details>
