# Nedir?
https://github.com/ogun/guncel-turkce-sozluk reposunda bulunan TDK Güncel Türkçe Sözlük veri tabanını biçimlendirerek StarDict sözlüğün hazırlanması için gerekli tab-delimited veya Babylon dosyaya dönüştüren bir python betiği. Ayrıca bu dosyadan elde edilen StarDict sözlüğü, Kindle ile uyumlu MOBI sözlük ve Kobo uyumlu sözlük aşağıda sunulmuştur.

StarDict arşivi: Releases kısmına bakın.  
MOBI dosyası: Releases kısmına bakın.  
Kobo dicthtml: Releases kısmına bakın.

Sözlüğün StarDict versiyonu KOReader üzerinde, MOBI versiyonu Kindle 4 üzerinde, dicthtml versiyonu Kobo Aura Edition 2 üzerinde denenmiş, bariz bir soruna rastlanılmamıştır.

# Kullanımı
`python gts_stardict.py --help`
```
usage: gts_stardict.py [-h] [--gls] [--hunspell-path HUNSPELL_PATH]

https://github.com/ogun/guncel-turkce-sozluk reposunda bulunan TDK Güncel Türkçe Sözlük veri tabanını
(gts.sqlite3.db) biçimlendirerek StarDict sözlüğün hazırlanması için gerekli tab-delimited veya Babylon GLS dosyaya
dönüştüren bir python betiği. --gls seçeneği belirtilmediği takdirde tab-delimited dosya üretilecektir. Sözcüklerin
çekimlenmiş halleri yalnızca *.gls formatında bulunmaktadır.

optional arguments:
  -h, --help            show this help message and exit
  --gls                 "Tab-delimited dosya yerine *.gls dosyası oluşturmak istiyorsanız bu seçeneği ekleyin.
                        Sözcüklerin çekimlenmiş halleri yalnızca *.gls formatında bulunmaktadır.
  --hunspell-path HUNSPELL_PATH
                        Eğer Hunspell sözlükleri betik ile aynı konumda değilse içinde tr.aff ve tr.dic bulunan
                        Hunspell sözlüklerinin olduğu dosya yolunu ekleyin.
```

- Yukarıda belirtilen repodaki `gts.sqlite3.db` sqlite veri tabanı dosyası `gts_stardict.py` betiği ile aynı konuma kaydedilir.
- \*.gls dosyası oluşturulacaksa Türkçe Hunpsell `tr.aff` ve `tr.dic` dosyaları temin edilir.
- Hunspell'i python içinden çağırmak için kullanılan wrapper'ı [burada](https://github.com/MSeal/cython_hunspell) bulabilirsiniz. **NOT**: 22 Mart 2022 itibariyle paketin Python 3.10 için derlenmiş bir pip paketi bulunmuyor. Paket sisteminizde derlenemediği takdirde Python 3.9'a geri dönmeniz gerekiyor. Yüklemek için <br/> `pip install cyhunspell`
- Yukarıdaki yardım takip edilerek istenilen dosya oluşturulur. \*.gls dosyası için örnek: <br/>`python gts_stardict.py --gls --hunspell-path C:\Users\<username>\Documents\hunspell`
- Elde edilen dosya [buradaki](https://code.google.com/archive/p/stardict-3/downloads) stardict-editor programı aracılığıyla StarDict formatına dönüştürülür. Bunun için dosya editörün `Compile` sekmesinden seçilir, dropdown menüde `.tabfile` için `Tab file` seçeneğinin, `gls` için `Babylon file` seçeneğinin seçildiğinden emin olunur ve `Compile` tuşuna basılarak işlem tamamlanır.
- Eğer tabfile dosyası elde edilmişse, HTML biçimlendirmesinin görüntüleyici programda tanınması için elde edilen 3 dosyadan biri olan `*.ifo` dosyasında `sametypesequence` parametresi `m`'den `h`'ye değiştirilmelidir.
- Elde edilen `*.dict` dosyası `dictzip` programı aracılığıyla `dictzip Guncel_Turkce_Sozluk.dict` komutuyla sıkıştırılabilir. Program çoğu Linux reposunda bulunmaktadır. Windows için derlenmiş bir versiyon [burada](https://github.com/Tvangeste/dictzip-win32) bulunabilir.
- MOBI formatına [penelope](https://github.com/pettarin/penelope) aracılığıyla aşağıdaki komutla dönüştürebilirsiniz. MOBI dosyalarının yazılabilmesi için `PATH`'inizde `kindlegen` programının olması gerekmektedir. Not: <strike>\*.gls dosyasından elde edilen stardict dosyaları `kindlegen` programının kısıtlamaları nedeniyle MOBI'ye çevrilememektedir, sadece tabfile ile üretilen stardict dosyalarını çevirmeyi deneyiniz.</strike> MOBI'ye [PyGlossary](https://github.com/ilius/pyglossary) kullanarak da çevirmeyi deneyebilirsiniz (\*.gls dosyasından elde edilmiş stardict dosyaları dahil). MOBI çıktı ayarlarında, `kindlegen` `PATH`'inizde olsa dahi çalıştırılabilir dosyanın adını ekleyin. Aksi takdirde, en azından benim denemelerimde, PyGlossary programı bulamıyor. Ayrıca, \*.ifo dosyasında, `bookname` kısmına `TR-TR` gibi kaynak ve hedef dili gösteren bir ibare eklemelisiniz. Örnek: `bookname=Güncel Türkçe Sözlük TR-TR`.

```
penelope -i GTS.zip -j stardict -f tr -t tr -p mobi -o Guncel_Turkce_Sozluk.mobi --title "Güncel Türkçe Sözlük"
```
# Kobo sözlüğünü oluşturma ve yükleme
* Tüm \*.gls dosyası içeriğini https://pgaskin.net/dictutil/examples/bgl-convert.html adresine kopyalayarak Kobo sözlük için bir ön format sayılabilecek \*.df formatını elde edebilirsiniz. 
  * Output dictfile içeriğini `[name].df` dosyasına kaydettikten sonra [dictgen](https://pgaskin.net/dictutil/dictgen/) yardımıyla \*.df dosyasını `dicthtml.zip` formatına çevirin. 
  * İsmi `dicthtml-tr.zip` olarak değiştirin. Sözlüğü `KOBOeReader/.kobo/dict` konumuna kopyalayın.
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

# TODO
- <strike>Çekimlenen sözcüklerde sonuç dönmeyebilir. Örneğin `dürtüsü` bir sonuç döndürmeyecektir. Sözcüğün anlamına bakılabilmesi için kelimenin çekimsiz halinin (`dürtü`) elle aranması gerekmektedir. Bu sorunu çözmek için tüm headword'lerin potansiyel çekimlerinin üretilip StarDict'in `*.syn` dosyasına kaydedilmesi araştırılabilir, [bkz.](https://github.com/huzheng001/stardict-3/blob/96b96d89eab5f0ad9246c2569a807d6d7982aa84/dict/doc/StarDictFileFormat#L216) Sözcüklerin çekimli hallerinin üretilmesi için [Zemberek](https://github.com/ahmetaa/zemberek-nlp/tree/master/morphology#word-generation) projesinin word generation özelliği kullanılabilir.</strike> → Hunspell yardımıyla kısmen çözümlendi ancak hala özelleşmiş bir NLP kütüphanesi daha iyi sonuçlar verebilir.
