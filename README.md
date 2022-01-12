# Nedir?
https://github.com/ogun/guncel-turkce-sozluk reposunda bulunuan TDK Güncel Türkçe Sözlük veri tabanını biçimlendirerek StarDict sözlüğün hazırlanması için gerekli tab-delimited dosyaya dönüştüren bir python betiği. Ayrıca bu dosyadan elde edilen StarDict sözlüğü ve Kindle ile uyumlu MOBI sözlük aşağıda sunulmuştur.

StarDict arşivi: [Güncel Türkçe Sözlük](dicts/GTS.zip)  
MOBI dosyası: [Güncel Türkçe Sözlük](dicts/Guncel_Turkce_Sozluk.mobi)

Sözlüğün StarDict versiyonu KOReader üzerinde, MOBI versiyonu Kindle 4 üzerinde denenmiş, bariz bir soruna rastlanılmamıştır. Sözlüğe eklenen HTML tagları Kobo'nun kendi sözlük formatında düzgün görüntülenemediğinden sözlüğün dicthtml versiyonuna burada yer verilmemiştir.

# Kullanımı

- Yukarıda belirtilen repodaki `gts.sqlite3.db` sqlite veritabanı dosyası `gts_stardict.py` betiği ile aynı konuma kaydedilir.
- `python gts_stardict.py` komut satırında çalıştırılır. Bunun sonucunda `Guncel_Turkce_Sozluk.tabfile` isminde bir dosya elde edilecektir.
- Dosya [buradaki](https://code.google.com/archive/p/stardict-3/downloads) stardict-editor programı aracılığıyla StarDict formatına dönüştürülür. Bunun için dosya editörün `Compile` sekmesinden seçilir, dropdown menüde `Tab file` seçeneğinin seçildiğinden emin olunur ve `Compile` tuşuna basılarak işlem tamamlanır.
- HTML biçimlendirmesinin görüntüleyici programda tanınması için elde edilen 3 dosyadan biri olan `*.ifo` dosyasında `sametypesequence` parametresi `m`'den `h`'ye değiştirilmelidir.
- Elde edilen `*.dict` dosyası `dictzip` programı aracılığıyla `dictzip Guncel_Turkce_Sozluk.dict` komutuyla sıkıştırılabilir. Program çoğu Linux reposunda bulunmaktadır. Windows için derlenmiş bir versiyon [burada](https://github.com/Tvangeste/dictzip-win32) bulunabilir.
- MOBI formatına [penelope](https://github.com/pettarin/penelope) aracılığıyla aşağıdaki komutla dönüştürebilirsiniz. MOBI dosyalarının yazılabilmesi için `PATH`'inizde `kindlegen` programının olması gerekmektedir.

```
penelope -i GTS.zip -j stardict -f tr -t tr -p mobi -o Guncel_Turkce_Sozluk.mobi --title "Güncel Türkçe Sözlük"
```

# Ekran Görüntüleri
<p float="left">
<img src="https://github.com/anezih/gts_stardict_mobi/raw/main/img/Reader_2022-01-11_203535.png" width="300px">
<img src="https://github.com/anezih/gts_stardict_mobi/raw/main/img/Reader_2022-01-12_010753.png" width="300px">
<img src="https://github.com/anezih/gts_stardict_mobi/raw/main/img/screen_shot-25906.gif" width="300px">
<img src="https://github.com/anezih/gts_stardict_mobi/raw/main/img/screen_shot-25907.gif" width="300px">
<img src="https://github.com/anezih/gts_stardict_mobi/raw/main/img/screen_shot-25904.gif" width="300px">
</p>

# TODO
- Çekimlenen sözcüklerde sonuç dönmeyebilir. Örneğin `dürtüsü` bir sonuç döndürmeyecektir. Sözcüğün anlamına bakılabilmesi için kelimenin çekimsiz halinin (`dürtü`) elle aranması gerekmektedir. Bu sorunu çözmek için tüm headword'lerin potansiyel çekimlerinin üretilip StarDict'in `*.syn` dosyasına kaydedilmesi araştırılabilir, [bkz.](https://github.com/huzheng001/stardict-3/blob/96b96d89eab5f0ad9246c2569a807d6d7982aa84/dict/doc/StarDictFileFormat#L216) Sözcüklerin çekimli hallerinin üretilmesi için [Zemberek](https://github.com/ahmetaa/zemberek-nlp/tree/master/morphology#word-generation) projesinin word generation özelliği kullanılabilir.
