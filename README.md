# Nedir?
https://github.com/ogun/guncel-turkce-sozluk reposunda bulunan TDK Güncel Türkçe Sözlük gts.json.tar.gz dosyasını
PyGlossary aracılığıyla StarDict, Kobo ve Kindle formatlarına çeviren bir Python betiği.

# Kullanımı
`python gts_convert.py --help`
```
usage: gts_convert.py [-h] [--json-tar-gz-path JSON_TAR_GZ_PATH] [--stardict] [--kobo] [--kindle] [--dictzip]
                      [--dictgen DICTGEN]

https://github.com/ogun/guncel-turkce-sozluk reposunda bulunan TDK Güncel Türkçe Sözlük gts.json.tar.gz dosyasını
PyGlossary aracılığıyla StarDict, Kobo ve Kindle formatlarına çeviren bir Python betiği.

options:
  -h, --help            show this help message and exit
  --json-tar-gz-path JSON_TAR_GZ_PATH
                        gts.json.tar.gz konumu.
  --stardict            StarDict çıktı formatı oluşturulsun.
  --kobo                Kobo dicthtml.zip çıktı formatı oluşturulsun.
  --kindle              Kindle MOBI çıktı formatı oluşturulsun.
  --dictzip             StarDict .dict dosyasını sıkıştıracak dictzip aracı PATH'de mi?
  --dictgen DICTGEN     Kobo dicthtml-tr.zip dosyasını oluşturacak aracın (dictgen-*.exe) konumu.
```
Yukarıda belirtilen repodan gts.json.tar.gz dosyasını gts_convert.py betiğinin yanına indirin. Sözcüklerin çekim bilgilerinin yer aldığı tr_TR.json.gz dosyasının betik ile aynı konumda olduğundan emin olun. (Bu dosyanın nasıl oluşturulduğunu merak ediyorsanız [bağlantıyı](https://gist.github.com/anezih/5e0fc6d68c9166fe2ea3ffc05bc68476) takip edin. Üretilen json dosyasının [kaynak Hunspell dosyaları](https://github.com/titoBouzout/Dictionaries/blob/master/Turkish.txt).)

Tüm formatları üretmek için betiği şu şekilde çağırın:

`python gts_convert.py --stardict --kobo --kindle --dictzip --dictgen "dictgen-windows.exe"`

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
* Kaynak ve detaylı açıklama için [buraya](https://pgaskin.net/dictutil/dicthtml/install.html) başvurun.

# V1 Ekran Görüntüleri

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
