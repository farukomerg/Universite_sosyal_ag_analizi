# Üniversite Sosyal Ağ Analizi

Ders: Yazılım Geliştirme Laboratuvarı

Bölüm: Bilişim Sistemleri Mühendisliği



Grup Üyeleri:


* 241307114 Ömer Faruk Güler (GitHub: @farukomerg)


* 231307064 Gülnihal Eruslu (GitHub: @gulni-hal)

---

## 1. Giriş

Günümüzde sosyal ağlar bireyler, kurumlar veya organizasyonlar arasındaki ilişkilerin analiz edilmesi açısından büyük önem taşımaktadır. Bu analiz sayesinde ağ içerisindeki bağlantılar, etkileşim yapıları, topluluklar ve merkezi düğümler belirlenebilir. Graf algoritmaları kullanılarak karmaşık ağ yapıları daha anlaşılır hale getirilir.

Bu projede, **üniversiteler birer düğüm (node)**, üniversiteler arasındaki **akademik iş birlikleri ise kenar (edge)** olarak modellenmiş ve bu yapı bir **graf** üzerinde ele alınmıştır. Geliştirilen uygulama ile graf üzerinde çeşitli algoritmalar çalıştırılarak ağ yapısı analiz edilmiş ve sonuçlar görsel olarak sunulmuştur.

Projenin temel amaçları aşağıda listelenmiştir:

- Graf veri yapısının uygulamalı olarak öğrenilmesi  
- BFS, DFS, Dijkstra, A*, Welsh–Powell gibi temel graf algoritmalarının gerçeklenmesi  
- Nesne yönelimli yazılım mimarisi oluşturulması  
- Görsel ve etkileşimli bir kullanıcı arayüzü geliştirilmesi  
- Algoritma test sonuçlarının görsel ve tablo halinde sunulması  

---
## 2. Nesne Yönelimli Tasarım (OOP)

Projede nesne yönelimli programlama (OOP) prensipleri esas alınmış, soyutlama (abstract) ve arayüzler (interface) kullanılarak her kavram ayrı sınıflar halinde modellenmiştir.

###  Temel Sınıflar

- **Node:**  Her bir üniversiteyi temsil eder. Üniversitenin öğrenci sayısı, kuruluş yılı, bulunduğu il ve ilçe, akademisyen sayısı ve akademik sıralama sayısal özelliklerini içerir.

- **Edge:**  İki üniversite arasındaki akademik iş birliğini temsil eder. Kenar üzerinde dinamik olarak hesaplanan ağırlık (maliyet) bilgisi tutulur.

- **Graph:**  Tüm düğüm ve kenarları yöneten ana sınıftır. Düğüm ve kenar ekleme, silme ve güncelleme işlemleri bu sınıf üzerinden gerçekleştirilir.

- **Algorithm:**  BFS, DFS, Dijkstra ve A* gibi algoritmalar için ortak bir soyut arayüz sağlar.

- **Coloring:**  Welsh–Powell graf renklendirme algoritmasını yöneten sınıftır. Birbirine komşu olan düğümlerin farklı renklerle gösterilmesini sağlar.

---

## 3. Proje Dizin Yapısı
Proje, veri dosyaları (`csv`, `json`, `data`) ve kaynak kodların (`src`) ayrıştırıldığı modüler bir hiyerarşiye sahiptir.

```mermaid
graph TD
    root[📂 Universite_sosyal_ag_analizi]

    root --> csv_dir[📂 csv_verileri]
    root --> data_dir[📂 data]
    root --> json_dir[📂 json_verileri]
    root --> src_dir[📂 src]
    
    root --> gitattr[📄 .gitattributes]
    root --> gitignore[📄 .gitignore]
    root --> readme[📄 README.md]

    csv_dir --> csv1[📄 Deneme_uni1.csv]
    data_dir --> db_main[🗄️ universite.db]

    json_dir --> json1[📄 akdeniz_iki_edge.json]
    json_dir --> json2[📄 ayni_siralama.json]
    json_dir --> json3[📄 cerrahpasa.json]
    json_dir --> json4[📄 deneme_uni.json]

    src_dir --> main_py[🐍 main.py]
    src_dir --> db_ctrl[🐍 db_control.py]

    src_dir --> core_dir[📂 core]
    src_dir --> ui_dir[📂 ui]
    src_dir --> out_dir[📂 output]
    src_dir --> rep_dir[📂 reports]

    core_dir --> algos[🐍 algorithms.py]
    core_dir --> loader[🐍 data_loader.py]
    core_dir --> edge[🐍 edge.py]
    core_dir --> exporter[🐍 exporter.py]
    core_dir --> graph[🐍 graph.py]
    core_dir --> interf[🐍 interfaces.py]
    core_dir --> node[🐍 node.py]

    ui_dir --> add_edge[🐍 add_edge_dialog.py]
    ui_dir --> add_node[🐍 add_node_dialog.py]
    ui_dir --> color_dlg[🐍 coloring_dialog.py]
    ui_dir --> canvas[🐍 graph_canvas.py]
    ui_dir --> main_win[🐍 main_window.py]
    ui_dir --> path_dlg[🐍 path_dialog.py]

    out_dir --> out1[📊 etki_analizi.csv]
    out_dir --> out2[📊 topluluk_analizi.csv]
    out_dir --> out3[📊 universite_liste_raporu.csv]
    out_dir --> out4[📊 welsh_powell_coloring.csv]

    rep_dir --> rep1[📊 merkezilik_raporu_...csv]
```

## 4. Veri Saklama ve Yükleme

Uygulama, verilerin kalıcı olarak saklanabilmesi ve tekrar yüklenebilmesi için **JSON** ve **CSV** formatlarını desteklemektedir.

- **JSON:**  Graf yapısının (düğümler ve kenarlar) kaydedilmesi için kullanılır.

- **CSV:**  Üniversitelere ait sayısal özelliklerin (öğrenci sayısı, üniversite yaşı, sıralama vb.) tutulması ve veri içe/dışa aktarımı için kullanılır.

Veri içe aktarımı sırasında hem JSON hem de CSV dosyaları kullanılarak sisteme yeni node ve edge eklenebilmektedir.

Veri dışa aktarımı işlemlerinde ise CSV formatı kullanılarak hem genel graf yapısı hem de çeşitli algoritmaların ürettiği sonuçlar dosya olarak dışa aktarılabilmektedir.

---

## 5. Dinamik Ağırlık Hesaplama

Üniversiteler arasındaki akademik iş birliği kenarlarının ağırlıkları **dinamik olarak** hesaplanmaktadır. Bu hesaplama üniversitelerin sayısal özellikleri dikkate alınarak yapılır.

Ağırlık hesaplamasında kullanılan özellikler:

- Ai: Üniversitenin **öğrenci sayısı**
- Ei: Üniversitenin **yaşı** (kuruluşundan itibaren geçen yıl sayısı)
- Bi: Üniversitenin **akademik sıralaması**

İki üniversite arasındaki kenar ağırlığı aşağıdaki formül ile hesaplanır:
Agirlik(i,j) = 1 / (1 + (Ai - Aj)² + (Ei - Ej)² + (Bi - Bj)²)

Bu hesaplama sonucunda:

- **Benzer özelliklere sahip üniversiteler** → daha yüksek ağırlık  
- **Farklı özelliklere sahip üniversiteler** → daha düşük ağırlık  

Hesaplanan bu ağırlık değerleri, tüm algoritmalarda **kenar maliyeti** olarak kullanılmaktadır.

---

## 6. Kullanılan Algoritmalar
Bu bölümde uygulama kapsamında kullanılan graf algoritmalarının çalışma mantıkları, kullanılan veri yapıları ve sistem içerisindeki işleyişleri açıklanmaktadır.

### 6.1. BFS (Breadth-First Search)
BFS, grafı katman katman keşfeden bir genişlik öncelikli arama algoritmasıdır. Başlangıç düğümüne en yakın düğümlerden başlayarak, ağ içerisindeki erişilebilir tüm düğümleri sırasıyla ziyaret eder.

**Kullanılan Veri Yapıları:**

- **Kuyruk (Queue – FIFO):**  BFS algoritması, İlk Giren İlk Çıkar (First-In, First-Out) prensibiyle çalışan bir kuyruk yapısı kullanır. Yeni keşfedilen komşu düğümler kuyruğun sonuna eklenir, işlenecek düğüm ise kuyruğun başından alınır.

- **Ziyaret Edilenler Kümesi (Visited Set):**   Algoritmanın aynı düğümü tekrar ziyaret ederek sonsuz döngüye girmesini engellemek için kullanılır. Bir düğüm kuyruğa eklenmeden önce ziyaret edilip edilmediği kontrol edilir.

**Çalışma Mantığı:** Başlangıç düğümü kuyruğa eklenir. Kuyruk boşalana kadar; kuyruğun başındaki düğüm çıkarılır, ziyaret edildi olarak işaretlenir ve bu düğümün henüz ziyaret edilmemiş tüm komşuları kuyruğa eklenir.

```mermaid
graph TD
    B1[Başla] --> B2[Kuyruk FIFO ve Ziyaret Edilenler Kümesi Oluştur]
    B2 --> B3[Başlangıç Düğümünü Kuyruğa ve Küreye Ekle]
    B3 --> B4{Kuyruk Boş mu?}
    B4 -- Hayır --> B5[Kuyruğun Başından Bir Düğüm Çıkar]
    B5 --> B6[Düğümü Ziyaret Sırasına Ekle]
    B6 --> B7[Ziyaret Edilmemiş Tüm Komşuları Bul]
    B7 --> B8[Komşuları Kuyruğa Ekle ve Ziyaret Edildi Olarak İşaretle]
    B8 --> B4
    B4 -- Evet --> B9[Ziyaret Sırasını Döndür ve Bitir]
```

### 6.2. DFS (Depth-First Search)

DFS, graf üzerinde **bir daldan mümkün olan en derin noktaya kadar ilerleyen** bir **derinlik öncelikli arama algoritmasıdır**.

**Kullanılan Veri Yapısı:**

- **Yığın (Stack – LIFO):** DFS algoritması, Son Giren İlk Çıkar (Last-In, First-Out) prensibiyle çalışan bir yığın yapısı kullanır. En son eklenen düğüm, bir sonraki adımda ilk ziyaret edilen düğüm olur.

**Çalışma Mantığı:** Başlangıç düğümü yığına eklenir. Yığın boşalana kadar; en üstteki düğüm yığından çıkarılır. Eğer düğüm daha önce ziyaret edilmemişse ziyaret listesine eklenir ve komşuları yığına itilir. Bu yapı, algoritmanın grafın derinliklerine hızlı bir şekilde inmesini sağlar.

```mermaid
graph TD
    D1[Başla] --> D2[Yığın LIFO ve Ziyaret Edilenler Kümesi Oluştur]
    D2 --> D3[Başlangıç Düğümünü Yığına Ekle]
    D3 --> D4{Yığın Boş mu?}
    D4 -- Hayır --> D5[Yığından En Üstteki Düğümü Çıkar]
    D5 --> D6{Düğüm Ziyaret Edildi mi?}
    D6 -- Evet --> D4
    D6 -- Hayır --> D7[Düğümü Ziyaret Edildi Olarak İşaretle ve Listeye Ekle]
    D7 --> D8[Ziyaret Edilmemiş Komşuları Ters Sırada Yığına Ekle]
    D8 --> D4
    D4 -- Evet --> D9[Ziyaret Sırasını Döndür ve Bitir]
```
### 6.3. Dijkstra Algoritması

Dijkstra algoritması, bir başlangıç düğümünden diğer tüm düğümlere olan **en kısa yolu (en düşük toplam maliyetli yolu)** bulan bir algoritmadır.

**Maliyet Hesaplama:** Uygulamada iki üniversite arasındaki kenar ağırlığı:  
- öğrenci sayısı,  
- akademik sıralama,  
- kuruluş yılı farkları  

göz önünde bulundurularak dinamik olarak hesaplanmaktadır.

**Çalışma Mantığı:** Algoritma başlangıçta tüm düğümlere olan mesafeyi sonsuz kabul eder. Bir **Öncelik Kuyruğu (Priority Queue)** kullanılarak her adımda mevcut en düşük maliyetli düğüm seçilir. Seçilen düğüm üzerinden komşu düğümlerin mesafeleri güncellenir.


```mermaid
graph TD
    A[Başla] --> B[Başlangıç Mesafesini 0, Diğerlerini Sonsuz Yap]
    B --> C[Öncelik Kuyruğuna Başlangıç Düğümünü Ekle]
    C --> D{Kuyruk Boş mu?}
    D -- Hayır --> E[En Küçük Mesafeli Düğümü Çıkar]
    E --> F[Düğüm Hedef mi?]
    F -- Evet --> G[Yolu Geriye Doğru Oluştur ve Döndür]
    F -- Hayır --> H[Komşuları Güncelle: Mevcut + Kenar Ağırlığı < Eski Mesafe?]
    H --> C
    D -- Evet --> I[Yol Bulunamadı]
```

### 6.4. A* (A-Star) Algoritması

A* algoritması, Dijkstra algoritmasının **hedef odaklı** ve daha verimli bir versiyonudur.

**Genel Mantık:** A* algoritması yalnızca başlangıçtan mevcut düğüme kadar olan maliyeti ($g$ skoru) değil, aynı zamanda hedef düğüme olan **tahmini mesafeyi** ($h$ skoru – heuristic) de hesaba katar.

**Sezgisel (Heuristic) Yaklaşım:** Bu projede sezgisel değer olarak, iki düğümün canvas üzerindeki koordinatları arasındaki **Öklid Mesafesi** kullanılmıştır. Bu sayede algoritma, hedefe fiziksel olarak daha yakın düğümlere öncelik vererek arama alanını daraltır ve çoğu durumda Dijkstra algoritmasına kıyasla daha hızlı sonuç üretir.

```mermaid
graph TD
    Start((Başla)) --> Init[f_score = g_score + heuristic]
    Init --> Loop{Kuyruk Boş mu?}
    Loop -- Hayır --> Select[En Düşük f_score'a Sahip Düğümü Seç]
    Select --> Goal{Hedef mi?}
    Goal -- Evet --> Success[Yolu Döndür]
    Goal -- Hayır --> Expand[Komşu g_score'larını Hesapla]
    Expand --> Loop
    Loop -- Evet --> Fail[Hata: Yol Yok]
```


### 6.5. Welsh–Powell Algoritması (Graf Renklendirme)

Welsh–Powell algoritması, grafı **komşu düğümler farklı renklerde olacak şekilde**, mümkün olan **en az sayıda renk** kullanarak boyamayı amaçlayan bir graf renklendirme algoritmasıdır.

**Çalışma Mantığı:** Öncelikle düğümler, bağlantı sayılarına (derecelerine) göre **azalan sırada** sıralanır. En yüksek dereceli düğümden başlanarak, komşularının o ana kadar kullanmadığı **en küçük renk numarası** atanır. Bu işlem tüm düğümler renklendirilene kadar devam eder.

Bu algoritma sayesinde graf içerisindeki ayrık topluluklar görsel olarak kolayca ayırt edilebilmektedir.
```mermaid
graph TD
    A[Başla] --> B[Düğümleri Derecelerine Göre Azalan Sırada Diz]
    B --> C{Tüm Düğümler Boyandı mı?}
    C -- Hayır --> D[Boyanmamış En Yüksek Dereceli Düğümü Seç]
    D --> E[Komşularının Kullanmadığı En Küçük Renk ID'sini Ata]
    E --> C
    C -- Evet --> F[Renklendirme Sözlüğünü Döndür]
    F --> G[Bitiş]
 ```

### 6.6 Ayrık Topluluk (Bağlı Bileşen) Analizi

Ayrık topluluk analizi, graf içerisindeki **birbirleriyle doğrudan veya dolaylı olarak bağlantısı olmayan alt ağları** tespit etmek amacıyla kullanılır. Bu analiz sayesinde grafın kaç farklı bağımsız bileşenden oluştuğu belirlenir.

Her ayrık topluluk, kendi içerisinde bağlantılı düğümlerden oluşurken diğer topluluklarla herhangi bir bağlantıya sahip değildir. Bu durum, ağ yapısındaki kopuklukların, izole grupların veya bağımsız alt sistemlerin analiz edilmesine olanak tanır. Elde edilen sonuçlar, graf üzerinde görsel olarak ayrık gruplar halinde gösterilerek kullanıcıya sunulur.

---

### 6.7 Degree Centrality (Derece Merkeziliği)

Degree Centrality, bir düğümün graf içerisindeki **doğrudan bağlantı sayısını** ölçen temel merkezilik metriklerinden biridir. Bir düğümün derece değeri ne kadar yüksekse, ağ içerisindeki etkileşim düzeyi ve önemi de o kadar yüksek kabul edilir.

Bu projede her düğümün sahip olduğu bağlantı sayısı hesaplanmakta ve **en yüksek dereceye sahip ilk 5 düğüm** tablo halinde kullanıcıya gösterilmektedir. Bu analiz sayesinde ağ içerisindeki en etkili, en fazla bağlantıya sahip ve merkezi konumda bulunan düğümler kolaylıkla tespit edilebilmektedir.

    
---
## 7. Kullanıcı Arayüzü

Uygulama kullanıcı dostu ve etkileşimli bir arayüze sahiptir:

- **Sol Panel:**  
  - Algoritmaları çalıştırmak için butonlar  
  - Tüm grafın çıktı alınabildiği alan  
  - Düğüm ve kenar ekleme, silme, güncelleme işlemleri  
  - CSV / JSON veri içe ve dışa aktarma bölümü  

- **Orta Panel:**  
  - Grafın canvas üzerinde görsel gösterimi  
  - Düğümler üniversiteleri, kenarlar akademik iş birliklerini temsil eder  
  - Kenarların üzerinde iki üniversite arasındaki ağırlık değeri gösterilir  

- **Sağ Panel:**  
  - Bilgi paneli  
  - Herhangi bir düğüm veya kenara tıklandığında ilgili detaylar görüntülenir  
  - Seçilen öğe için düzenleme ve silme işlemleri yapılabilir  

---

## 8. Testler ve Performans Analizi

- Küçük ölçekli (10–20 düğüm) ve orta ölçekli (50–100 düğüm) graflar oluşturulmuştur. Test sonuçları aşağıdaki tablolarda gösterilmiştir.
- Tüm algoritmalar bu graflar üzerinde test edilmiştir.
- Algoritmalar makul sürelerde çalışmakta ve sonuçlar tablo halinde raporlanmaktadır.
- Hatalı veri girişleri (aynı sıralamaya sahip üniversitenin tekrar eklenmesi, eksik bilgi girimi, self-loop vb.) sistem tarafından engellenmiştir.


### 8.1 Küçük Ölçekli Graf Testi (10–20 Düğüm)

Bu test senaryosunda küçük ölçekli bir graf üzerinde temel graf algoritmaları çalıştırılmıştır.  
Algoritmaların çalışma süreleri ölçülmüş ve sonuçlar aşağıdaki tabloda gösterilmiştir.

<img width="718" height="680" alt="Screenshot 2026-01-01 231456" src="https://github.com/user-attachments/assets/cf7f7ed9-7a96-429c-982f-76a89bfb2007" />


Küçük Ölçekli Graph

| Algoritma Adı        | Sonuç Görseli | Çalışma Süresi (sn) |
|---------------------|---------------|---------------------|
| Welsh–Powell        |       <img width="752" height="746" alt="Screenshot 2026-01-01 231524" src="https://github.com/user-attachments/assets/ef75177a-423a-4bd9-8c21-2909fe659c69" /> | 0.000084            |
| A*                  |       <img width="756" height="738" alt="Screenshot 2026-01-01 231551" src="https://github.com/user-attachments/assets/0079daee-b7fa-4e8f-bee8-d23f4bae6476" />  | 0.000290            |
| Dijkstra            |         <img width="765" height="741" alt="Screenshot 2026-01-01 231611" src="https://github.com/user-attachments/assets/3491316b-b942-4076-a691-834523f481f6" />  | 0.000205            |
| BFS                 |        <img width="720" height="727" alt="Screenshot 2026-01-01 231906" src="https://github.com/user-attachments/assets/41d1fbae-c000-4ffc-bcf4-88c733a4171f" />  | 0.000151            |
| DFS                 |        <img width="728" height="725" alt="Screenshot 2026-01-01 231922" src="https://github.com/user-attachments/assets/b146da24-be56-47eb-9d87-8489426f715d" />  | 0.000046            |
---

### 8.2 Orta Ölçekli Graf Testi (50-100 Düğüm)

Bu test senaryosunda orta ölçekli bir graf üzerinde temel graf algoritmaları çalıştırılmıştır.  
Algoritmaların çalışma süreleri ölçülmüş ve sonuçlar aşağıdaki tabloda gösterilmiştir.


<img width="1019" height="879" alt="Ekran görüntüsü 2026-01-02 114830" src="https://github.com/user-attachments/assets/95adeee4-6c00-49b4-916e-5a20e7908282" />

Orta Ölçekli Graph

| Algoritma Adı        | Sonuç Görseli | Çalışma Süresi (sn) |
|---------------------|---------------|---------------------|
| Welsh–Powell        |       <img width="974" height="885" alt="Ekran görüntüsü 2026-01-02 115015" src="https://github.com/user-attachments/assets/ee1df0cb-8f87-4140-8e2f-1eaa07bcac35" />
| 0.000220            |
| A*                  |       <img width="971" height="878" alt="Ekran görüntüsü 2026-01-02 115436" src="https://github.com/user-attachments/assets/3bd816ce-1f26-4a2b-9e35-8738ed9860a0" />
| 0.000093            |
| Dijkstra            |        <img width="971" height="878" alt="Ekran görüntüsü 2026-01-02 115436" src="https://github.com/user-attachments/assets/3bd816ce-1f26-4a2b-9e35-8738ed9860a0" />   | 0.000137            |
| BFS                 |        <img width="1003" height="880" alt="Ekran görüntüsü 2026-01-02 115825" src="https://github.com/user-attachments/assets/0c1c7375-2580-4441-be93-9b380e3656f7" />   | 0.000093            |
| DFS                 |       <img width="1003" height="880" alt="Ekran görüntüsü 2026-01-02 115825" src="https://github.com/user-attachments/assets/0c1c7375-2580-4441-be93-9b380e3656f7" />    | 0.000129            |
---

## 9.  Kullanılan Teknolojiler

- **Python 3.10**  Projenin geliştirildiği temel programlama dili.

- **PyQt5**  Grafik kullanıcı arayüzünün (GUI) oluşturulması ve etkileşimli bileşenlerin yönetimi.

- **SQLite**  Üniversite düğümleri ve aralarındaki ilişkilerin kalıcı olarak saklandığı hafif veritabanı sistemi.

- **QPainter & Canvas**  Graf yapısının, düğümlerin, kenarların ve görsel animasyonların dinamik olarak çizilmesi.

- **NetworkX**  Düğümlerin ekran üzerindeki yerleşim düzeninin (spring layout) hesaplanması ve graf düzeninin iyileştirilmesi.

- **JSON & CSV**  Veri içe/dışa aktarımı, komşuluk listelerinin raporlanması ve kalıcı veri saklama işlemleri.

- **PyCharm**  Proje geliştirme, kod düzenleme ve hata ayıklama süreçlerinde kullanılan entegre geliştirme ortamı (IDE).

## 10. Sonuç ve Tartışma

Bu proje kapsamında, üniversiteler arası akademik ilişkiler graf veri yapısı üzerinde başarıyla modellenmiş ve analiz edilmiştir. Dinamik ağırlık hesaplamaları sayesinde, özellik bakımından birbirine daha yakın üniversiteler görsel olarak daha ilişkili şekilde gösterilebilmekte, kullanıcılar bu yakınlıkları grafik üzerinde doğrudan gözlemleyebilmektedir. Ayrıca uygulanan graf algoritmaları sayesinde, üniversitelerin birbirleriyle olan ilişkileri farklı senaryolar altında test edilebilmekte ve ağ yapısı detaylı olarak analiz edilebilmektedir.

---

## 11. Olası Geliştirmeler

- Daha fazla üniversite eklenerek daha büyük ölçekli bir ağ analizi gerçekleştirilmesi
- Farklı ülkelerden üniversitelerin dahil edilerek uluslararası akademik ağların analiz edilmesi
- Yönlü graf desteği ile iş birliklerinin tek yönlü modellenebilmesi
- Programın bilgisayara kurulmasına gerek kalmadan, herkesin bir internet sitesi üzerinden kullanabileceği bir web sürümü  


---
## 12. Kaynakça

https://visjs.org/

https://visjs.github.io/vis-network/examples/

https://pythonhumanities.com/

https://www.pythonguis.com/tutorials/pyqt-basic-widgets/

https://www.pythonguis.com/tutorials/pyqt-dialogs/

https://medium.com/@enesaksoy1732/pyqt5-kullanarak-basit-bir-web-taray%C4%B1c%C4%B1s%C4%B1-olu%C5%9Fturma-540752f826c3

https://medium.com/cits-tech/python-networkx-ile-graf-teorisi-931699540e73

https://www.geeksforgeeks.org/dsa/dijkstras-shortest-path-algorithm-greedy-algo-7/

https://www.freecodecamp.org/news/graph-algorithms-in-python-bfs-dfs-and-beyond/

https://graphstream-project.org/doc/Algorithms/Welsh-Powell/
