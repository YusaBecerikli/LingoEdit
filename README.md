# 🌍 LingoEdit: PO Dosya Düzenleyici ve Yapay Zeka Destekli Çeviri Aracı

[![GitHub license](https://img.shields.io/badge/Lisans-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Durum-Aktif%20Geli%C5%9Ftirme-green)](https://github.com/KullaniciAdiniz/LingoEdit)

---

## 🎯 Proje Hakkında

**LingoEdit**, GetText (.po) çeviri dosyalarını düzenlemek, gözden geçirmek ve otomatik olarak çevirmek için tasarlanmış modern, açık kaynaklı bir masaüstü uygulamasıdır. CustomTkinter ile geliştirilen bu araç, çeviri iş akışınızı hızlandırır ve manuel çeviri hatalarını en aza indirir.

Uygulama, özellikle geniş kapsamlı çeviri projelerinde **hız** ve **doğruluk** sağlamak üzere optimize edilmiştir.

### ✨ Temel Özellikler

* **Modern Arayüz:** CustomTkinter ile oluşturulmuş şık, karanlık (Dark Mode) bir kullanıcı arayüzü.
* **Akıllı Otomatik Çeviri:** Boş metinleri Google Translate motorunu kullanarak hızlıca doldurur.
* **Gözden Geçirme Modu:** Otomatik çeviri yaparken, çeviriyi kaydetmeden önce her satırı düzenleyip onaylayabileceğiniz interaktif bir pencere sunar.
* **Hata Ayıklama:** Tek tıklama ile çeviri hücrelerini düzenleme imkanı.
* **İlerleme Takibi:** Otomatik çeviri sırasında kalan süreyi ve ilerlemeyi gösteren canlı durum penceresi.
* **Toplu Düzenleme:** Çevrilmemiş (boş) tüm satırları tek bir pencerede ardı ardına hızlıca çevirme imkanı.

---

## 💻 Kullanım (EXE Dosyası)

LingoEdit, Python bağımlılıklarına ihtiyaç duymadan doğrudan çalıştırılabilir bir **EXE dosyası** olarak sunulmaktadır.

1.  [**Buradan**](<Release Sayfasının Bağlantısı>) en son sürümü indirin.
2.  İndirilen `LingoEdit.exe` dosyasını çalıştırın.
3.  Uygulama içinde `Dosya Aç` butonuna tıklayarak `.po` dosyanızı seçin ve çeviriye başlayın!

---

## ⚙️ Kurulum (Geliştiriciler İçin)

Bu projeyi yerel olarak çalıştırmak ve geliştirmeye katkıda bulunmak isterseniz aşağıdaki adımları izleyin.

### Önkoşullar

* Python 3.8+

### Adımlar

1.  Projeyi klonlayın:
    ```bash
    git clone [https://github.com/KullaniciAdiniz/LingoEdit.git](https://github.com/KullaniciAdiniz/LingoEdit.git)
    cd LingoEdit
    ```

2.  Gerekli kütüphaneleri kurun:
    ```bash
    pip install customtkinter polib deep-translator
    ```

3.  Uygulamayı çalıştırın:
    ```bash
    python po_editor_app.py
    ```

### EXE Oluşturma

Projeyi tek bir çalıştırılabilir dosya haline getirmek için **PyInstaller** kullanılmıştır:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "LingoEdit" --hidden-import "customtkinter" --collect-all "customtkinter" --icon "lingoedit_icon.ico" po_editor_app.py
