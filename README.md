# Nedir?
https://github.com/ogun/guncel-turkce-sozluk reposunda bulunuan TDK Güncel Türkçe Sözlük veri tabanını biçimlendirerek StarDict sözlüğün hazırlanması için gerekli tab-delimited veya Babylon dosyaya dönüştüren bir python betiği. Ayrıca bu dosyadan elde edilen StarDict sözlüğü, Kindle ile uyumlu MOBI sözlük ve Kobo uyumlu sözlük aşağıda sunulmuştur.

StarDict arşivi: Releases kısmına bakın, v1 için: [Güncel Türkçe Sözlük](dicts/GTS.zip)  
MOBI dosyası: [Güncel Türkçe Sözlük](dicts/Guncel_Turkce_Sozluk.mobi)  
Kobo dicthtml: Releases kısmına bakın.

Sözlüğün StarDict versiyonu KOReader üzerinde, MOBI versiyonu Kindle 4 üzerinde, dicthtml versiyonu Kobo Aura Edition 2 üzerinde denenmiş, bariz bir soruna rastlanılmamıştır.

# Kullanımı
`python gts_stardict.py --help`
```
usage: gts_stardict.py [-h] [--gls] [--hunspell-path HUNSPELL_PATH]

https://github.com/ogun/guncel-turkce-sozluk reposunda bulunuan TDK Güncel Türkçe Sözlük veri tabanını
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

- Yukarıda belirtilen repodaki `gts.sqlite3.db` sqlite veritabanı dosyası `gts_stardict.py` betiği ile aynı konuma kaydedilir.
- \*.gls dosyası oluşturulacaksa Türkçe Hunpsell `tr.aff` ve `tr.dic` dosyaları temin edilir.
- Hunspell'i python içinden çağırmak için kullanılan wrapper'ı [burada](https://github.com/MSeal/cython_hunspell) bulabilirsiniz. Yüklemek için <br/> `pip install cyhunspell`
- Yukarıdaki yardım takip edilerek istenilen dosya oluşturulur. \*.gls dosyası için örnek: <br/>`python gts_stardict.py --gls --hunspell-path C:\Users\<username>\Documents\hunspell`
- Elde edilen dosya [buradaki](https://code.google.com/archive/p/stardict-3/downloads) stardict-editor programı aracılığıyla StarDict formatına dönüştürülür. Bunun için dosya editörün `Compile` sekmesinden seçilir, dropdown menüde `.tabfile` için `Tab file` seçeneğinin, `gls` için `Babylon file` seçeneğinin seçildiğinden emin olunur ve `Compile` tuşuna basılarak işlem tamamlanır.
- Eğer tabfile dosyası elde edilmişse, HTML biçimlendirmesinin görüntüleyici programda tanınması için elde edilen 3 dosyadan biri olan `*.ifo` dosyasında `sametypesequence` parametresi `m`'den `h`'ye değiştirilmelidir.
- Elde edilen `*.dict` dosyası `dictzip` programı aracılığıyla `dictzip Guncel_Turkce_Sozluk.dict` komutuyla sıkıştırılabilir. Program çoğu Linux reposunda bulunmaktadır. Windows için derlenmiş bir versiyon [burada](https://github.com/Tvangeste/dictzip-win32) bulunabilir.
- MOBI formatına [penelope](https://github.com/pettarin/penelope) aracılığıyla aşağıdaki komutla dönüştürebilirsiniz. MOBI dosyalarının yazılabilmesi için `PATH`'inizde `kindlegen` programının olması gerekmektedir. Not: \*.gls dosyasından elde edilen stardict dosyasları `kindlegen` programının kısıtlamaları nedeniyle MOBI'ye çevrilememektedir, sadece tabfile ile üretilen stardict dosyalarını çevirmeyi deneyiniz. 

```
penelope -i GTS.zip -j stardict -f tr -t tr -p mobi -o Guncel_Turkce_Sozluk.mobi --title "Güncel Türkçe Sözlük"
```
# Kobo sözlüğünü oluşturma ve yükleme
* Tüm \*.gls dosyası içeriğini https://pgaskin.net/dictutil/examples/bgl-convert.html adresine kopyalayarak Kobo sözlük için bir ön format sayılabilecek \*.df formatını elde edebilirsiniz. 
  * Output dictfile içeriğini `[name].df` dosyasına kaydettikten sonra [dictgen](https://pgaskin.net/dictutil/dictgen/) yardımıyla \*.df dosyasını `dicthtml.zip` formatına çevirin. 
  * İsmi `dicthtml-tr.zip` olarak değiştirin. Sözlüğü `KOBOeReader/.kobo/dict` konumuna kopyalayın.
  * `KOBOeReader/.kobo/Kobo/Kobo eReader.conf` dosyasında `ApplicationPreferences` kısmının altına `ExtraLocales=tr` seçeneğini ekleyin.
  * Kaynak ve detaylı açıklama için [buraya](https://pgaskin.net/dictutil/dicthtml/install.html) başvurun.

# Ekran Görüntüleri
<p float="left">
<img src="https://github.com/anezih/gts_stardict_mobi/raw/main/img/Reader_2022-01-11_203535.png" width="300px">
<img src="https://github.com/anezih/gts_stardict_mobi/raw/main/img/Reader_2022-01-12_010753.png" width="300px">
<img src="https://github.com/anezih/gts_stardict_mobi/raw/main/img/screen_shot-25906.gif" width="300px">
<img src="https://github.com/anezih/gts_stardict_mobi/raw/main/img/screen_shot-25907.gif" width="300px">
<img src="https://github.com/anezih/gts_stardict_mobi/raw/main/img/screen_shot-25904.gif" width="300px">
</p>
<h2>V2</h2>
<p float="left">
<img src="https://github.com/anezih/gts_stardict_mobi/raw/main/img/v2/yapit_v2.png" width="300px">
<img src="https://github.com/anezih/gts_stardict_mobi/raw/main/img/v2/kobo_yapit_v2.png" width="300px">
</p>

# TODO
- <strike>Çekimlenen sözcüklerde sonuç dönmeyebilir. Örneğin `dürtüsü` bir sonuç döndürmeyecektir. Sözcüğün anlamına bakılabilmesi için kelimenin çekimsiz halinin (`dürtü`) elle aranması gerekmektedir. Bu sorunu çözmek için tüm headword'lerin potansiyel çekimlerinin üretilip StarDict'in `*.syn` dosyasına kaydedilmesi araştırılabilir, [bkz.](https://github.com/huzheng001/stardict-3/blob/96b96d89eab5f0ad9246c2569a807d6d7982aa84/dict/doc/StarDictFileFormat#L216) Sözcüklerin çekimli hallerinin üretilmesi için [Zemberek](https://github.com/ahmetaa/zemberek-nlp/tree/master/morphology#word-generation) projesinin word generation özelliği kullanılabilir.</strike> → Hunspell yardımıyla kısmen çözümlendi ancak hala özelleşmiş bir NLP kütüphanesi daha iyi sonuçlar verebilir.
