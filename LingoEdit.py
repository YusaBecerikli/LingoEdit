# Gerekli Kütüphaneler
# pip install customtkinter polib deep-translator

import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import polib
from deep_translator import GoogleTranslator
import threading
import time

class ProgressDialog(ctk.CTkToplevel):
    def __init__(self, parent, total_entries):
        super().__init__(parent)
        self.transient(parent)
        self.title("Otomatik Çeviri İlerlemesi")
        self.geometry("400x200")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.lift(); self.attributes("-topmost", True)
        
        self.cancelled = False
        self.start_time = time.time()
        self.total = total_entries

        self.grid_columnconfigure(0, weight=1)
        
        # Başlık
        ctk.CTkLabel(self, text="Çeviri Devam Ediyor...", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=20, pady=(15, 5))

        # İlerleme Çubuğu (Global olanı değil, burada yeni bir tane)
        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate")
        self.progress_bar.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)

        # Durum Etiketi
        self.status_label = ctk.CTkLabel(self, text="0 / 0 çevrildi | Kalan süre: Hesapla...")
        self.status_label.grid(row=2, column=0, padx=20, pady=5)
        
        # İptal Butonu
        ctk.CTkButton(self, text="İptal Et", command=self.cancel_translation, fg_color="red", hover_color="darkred").grid(row=3, column=0, pady=15)
        
    def update_progress(self, current_count):
        """Ana thread'den çağrılır."""
        if self.cancelled: return

        # 1. İlerleme Çubuğu
        progress_value = current_count / self.total
        self.progress_bar.set(progress_value)
        
        # 2. Kalan Süre Hesaplama
        elapsed_time = time.time() - self.start_time
        entries_per_second = current_count / elapsed_time if elapsed_time > 0 else 0.01
        
        remaining_entries = self.total - current_count
        if entries_per_second > 0:
            remaining_time = remaining_entries / entries_per_second
            time_str = self._format_time(remaining_time)
        else:
            time_str = "Hesaplanıyor..."

        # 3. Durum Etiketi
        self.status_label.configure(text=f"{current_count} / {self.total} çevrildi | Kalan süre: {time_str}")

    def _format_time(self, seconds):
        """Saniyeyi okunabilir formata çevirir."""
        if seconds < 60:
            return f"{int(seconds)} saniye"
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        if minutes < 60:
            return f"{minutes} dakika {seconds} saniye"
        
        hours = int(minutes // 60)
        minutes = int(minutes % 60)
        return f"{hours} saat {minutes} dakika"


    def cancel_translation(self):
        self.cancelled = True
        self.on_close()

    def on_close(self):
        # Eğer kullanıcı pencereyi kapatırsa ve henüz iptal etmediyse, yine de iptal et
        self.cancelled = True
        self.destroy()

# --- Gözden Geçirme Penceresi (İsteklerinize Göre Düzenlendi) ---
class ReviewDialog(ctk.CTkToplevel):
    def __init__(self, parent, original_text, translated_text, position=None):
        super().__init__(parent)
        self.transient(parent)
        self.parent = parent # Ana uygulamaya referans
        self.title("Çeviriyi Düzenle ve Onayla")
        
        # DÜZENLEME 3: Pencere konumunu hatırla
        if position:
            self.geometry(f"600x450+{position[0]}+{position[1]}")
        else:
            self.geometry("600x450")

        self.lift(); self.attributes("-topmost", True); self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.result = None

        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1); self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(self, text="Orijinal Metin (msgid)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")
        original_textbox = ctk.CTkTextbox(self, height=100); original_textbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        original_textbox.insert("1.0", original_text); original_textbox.configure(state="disabled")

        ctk.CTkLabel(self, text="Çeviri (Doğrudan düzenleyebilirsiniz)", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=10, pady=(10,0), sticky="w")
        self.translated_textbox = ctk.CTkTextbox(self, height=100); self.translated_textbox.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        self.translated_textbox.insert("1.0", translated_text); self.translated_textbox.focus()

        # DÜZENLEME 2: Gözden geçirme ekranında Enter tuşu ile onay
        self.translated_textbox.bind("<Return>", self.handle_enter_key)
        
        button_frame = ctk.CTkFrame(self, fg_color="transparent"); button_frame.grid(row=4, column=0, pady=15)
        ctk.CTkButton(button_frame, text="Kaydet ve Devam Et", command=self.on_confirm, width=180, fg_color="green", hover_color="darkgreen").pack()
        
        self.wait_window(self)

    def handle_enter_key(self, event):
        if event.state & 0x0001: return # Shift+Enter ise yeni satır ekle
        self.on_confirm()
        return "break" 

    def on_confirm(self):
        self.save_position()
        self.result = self.translated_textbox.get("1.0", "end-1c").strip()
        self.destroy()

    def on_cancel(self):
        self.save_position()
        self.result = None
        self.destroy()

    def save_position(self):
        # DÜZENLEME 3: Kapanmadan önce pozisyonu ana uygulamaya kaydet
        self.parent.last_review_dialog_pos = (self.winfo_x(), self.winfo_y())

# --- Manuel Çeviri Penceresi ("Boşları Getir") (Değişiklik Yok) ---
class ManualTranslateWindow(ctk.CTkToplevel):
    def __init__(self, parent, entries_to_translate):
        # ... (Bu sınıfın içeriği öncekiyle aynı, değişiklik yok) ...
        super().__init__(parent)
        self.parent = parent; self.entries = entries_to_translate
        self.current_index = 0; self.total_count = len(self.entries)
        self.title("Boş Çevirileri Doldur"); self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close); self.lift(); self.attributes("-topmost", True)
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(2, weight=1); self.grid_rowconfigure(4, weight=1)
        self.counter_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14)); self.counter_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkLabel(self, text="Orijinal Metin (msgid)", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=20, pady=(10,0), sticky="w")
        self.source_text = ctk.CTkTextbox(self, wrap="word"); self.source_text.grid(row=2, column=0, padx=20, pady=5, sticky="nsew"); self.source_text.configure(state="disabled")
        ctk.CTkLabel(self, text="Çeviri (msgstr) - Sonraki için Enter'a basın", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, padx=20, pady=(10,0), sticky="w")
        self.translation_entry = ctk.CTkTextbox(self, wrap="word"); self.translation_entry.grid(row=4, column=0, padx=20, pady=5, sticky="nsew")
        self.translation_entry.bind("<Return>", self.handle_enter_key)
        self.next_button = ctk.CTkButton(self, text="İleri", command=self.save_and_next, width=150); self.next_button.grid(row=5, column=0, padx=20, pady=20)
        self.display_current_entry(); self.translation_entry.focus()
    def handle_enter_key(self, event):
        if event.state & 0x0001: return
        self.save_and_next(); return "break"
    def display_current_entry(self):
        if self.current_index < self.total_count:
            entry = self.entries[self.current_index]; self.counter_label.configure(text=f"Çeviri: {self.current_index + 1} / {self.total_count}")
            self.source_text.configure(state="normal"); self.source_text.delete("1.0", "end"); self.source_text.insert("1.0", entry.msgid); self.source_text.configure(state="disabled")
            self.translation_entry.delete("1.0", "end"); self.translation_entry.focus()
    def save_and_next(self):
        if self.current_index < self.total_count:
            translated_text = self.translation_entry.get("1.0", "end-1c").strip()
            if translated_text: self.entries[self.current_index].msgstr = translated_text
            self.current_index += 1
            if self.current_index < self.total_count: self.display_current_entry()
            else: self.finish_translation()
    def finish_translation(self): messagebox.showinfo("Bitti", "Tüm boş çeviriler tamamlandı!", parent=self); self.on_close()
    def on_close(self): self.parent.refresh_data_display(); self.destroy()

# --- Ana Uygulama Penceresi (Son Hali) ---
class POEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PO Dosya Düzenleyici (Final Versiyon)")
        self.geometry("1200x800")

        self.po_file = None; self.file_path = None
        self.all_entries = []; self.iid_map = {}
        self.last_review_dialog_pos = None # DÜZENLEME 3: Pencere pozisyonunu tutacak değişken
        self.progress_dialog = None 
        
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1)

        top_frame = ctk.CTkFrame(self, height=50); top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(top_frame, text="Dosya Aç", command=self.open_file).pack(side="left", padx=5)
        self.save_button = ctk.CTkButton(top_frame, text="Kaydet", command=self.save_file, state="disabled"); self.save_button.pack(side="left", padx=5)
        self.manual_translate_button = ctk.CTkButton(top_frame, text="Boşları Getir", command=self.start_manual_translation, state="disabled"); self.manual_translate_button.pack(side="left", padx=5)
        self.auto_translate_button = ctk.CTkButton(top_frame, text="Otomatik Çevir", command=self.start_auto_translate, state="disabled"); self.auto_translate_button.pack(side="left", padx=5)
        self.review_mode_check = ctk.CTkCheckBox(top_frame, text="Gözden Geçir"); self.review_mode_check.pack(side="left", padx=10); self.review_mode_check.select()

        style = ttk.Style(self); style.theme_use("default")
        style.configure("Treeview", rowheight=40, fieldbackground="#2B2B2B", background="#2B2B2B", foreground="white")
        style.configure("Treeview.Heading", font=('Calibri', 10,'bold'), background="#2B2B2B", foreground="white", relief="flat")
        style.map('Treeview', background=[('selected', '#1F6AA5')]); style.map('Treeview.Heading', relief=[('active','flat')])

        tree_frame = ctk.CTkFrame(self); tree_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew"); tree_frame.grid_rowconfigure(0, weight=1); tree_frame.grid_columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(tree_frame, columns=('msgid', 'msgstr'), show='headings'); self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.heading('msgid', text='Orijinal Metin (msgid)'); self.tree.heading('msgstr', text='Çeviri (msgstr) - Düzenlemek için tek tıkla')
        self.tree.column('msgid', width=500); self.tree.column('msgstr', width=500)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=scrollbar.set); scrollbar.grid(row=0, column=1, sticky="ns")
        
        # DÜZENLEME 1: Çift tıklama yerine tek tıklama ile düzenleme
        self.tree.bind("<Button-1>", self.on_tree_click)

        self.status_bar = ctk.CTkLabel(self, text="Lütfen bir .po dosyası açın.", anchor="w"); self.status_bar.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("PO Files", "*.po")]);
        if not path: return
        try:
            self.file_path = path; self.po_file = polib.pofile(self.file_path, encoding='utf-8', wrapwidth=1024)
            self.refresh_data_display()
            self.save_button.configure(state="normal"); self.manual_translate_button.configure(state="normal"); self.auto_translate_button.configure(state="normal")
        except Exception as e: messagebox.showerror("Hata", f"Dosya açılamadı: {e}")
            
    def refresh_data_display(self):
        self.tree.delete(*self.tree.get_children())
        self.all_entries = [e for e in self.po_file if not e.obsolete]
        self.iid_map = {}
        for i, entry in enumerate(self.all_entries):
            iid = str(i); self.tree.insert('', 'end', iid=iid, values=(entry.msgid, entry.msgstr)); self.iid_map[iid] = i
        self.status_bar.configure(text=f"Açık dosya: {self.file_path}  |  {len(self.all_entries)} satır yüklendi.")

    # DÜZELTME A: Tek tıkla düzenleme mantığı ve Treeview ile uyumlu widget kullanımı
    def on_tree_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item: return

        column = self.tree.identify_column(event.x)
        
        # Sadece ikinci sütunun (msgstr) tıklanması durumunda düzenlemeyi başlat
        if column != "#2": return 

        x, y, w, h = self.tree.bbox(item, column)
        
        # Daha önce açılmış bir düzenleme kutusu varsa temizle
        if hasattr(self, 'edit_widget'): self.edit_widget.destroy()

        # Standart Tkinter Entry kullanıyoruz, aksi takdirde ctk Entry treeview ile zor çalışır.
        self.edit_widget = ttk.Entry(self.tree) 
        self.edit_widget.place(x=x, y=y, width=w, height=h)
        
        original_text = self.tree.item(item, 'values')[1]
        self.edit_widget.insert(0, original_text)
        self.edit_widget.select_range(0, 'end')
        self.edit_widget.focus()
        
        # Tamamlama ve odağı kaybetme bağlamaları
        self.edit_widget.bind("<Return>", lambda e, iid=item: self.on_edit_complete(self.edit_widget, iid))
        self.edit_widget.bind("<FocusOut>", lambda e, iid=item: self.on_edit_complete(self.edit_widget, iid))

    def on_edit_complete(self, widget, iid):
        # DÜZELTME A: widget.destroy() çağırmadan önce FocusOut'ın tekrar tetiklenmesini engelle
        if not widget.winfo_exists(): return
        
        new_text = widget.get()
        entry_index = self.iid_map.get(iid)
        
        if entry_index is not None and entry_index < len(self.all_entries):
            original_msgid = self.all_entries[entry_index].msgid
            self.all_entries[entry_index].msgstr = new_text
            self.tree.item(iid, values=(original_msgid, new_text))
            
        widget.destroy()
        if hasattr(self, 'edit_widget') and self.edit_widget is widget:
            del self.edit_widget

    def save_file(self):
        if not self.po_file: return
        try: self.po_file.save(self.file_path); messagebox.showinfo("Başarılı", "Dosya başarıyla kaydedildi.")
        except Exception as e: messagebox.showerror("Hata", f"Dosya kaydedilemedi: {e}")

    def start_manual_translation(self):
        untranslated = [e for e in self.all_entries if not e.msgstr]
        if not untranslated: messagebox.showinfo("Bilgi", "Çevirisi yapılmamış satır bulunamadı."); return
        ManualTranslateWindow(self, untranslated)
        
    def start_auto_translate(self):
        untranslated = [e for e in self.all_entries if not e.msgstr]
        if not untranslated: messagebox.showinfo("Bilgi", "Çevirisi yapılmamış satır bulunamadı."); return
        
        review_mode = self.review_mode_check.get()
        
        # DÜZELTME: Yeni ilerleme penceresini aç
        if not review_mode:
            self.progress_dialog = ProgressDialog(self, len(untranslated))
            self.progress_dialog.grab_set() # Ana pencereyi devre dışı bırak
        else:
            # Gözden geçirme modu için mevcut ilerleme çubuğunu kullanabiliriz (Veya kaldırabiliriz)
            # Şu anki koddaki gibi, status bar'ın yerine koyalım:
            self.progress_bar = ctk.CTkProgressBar(self); 
            self.progress_bar.set(0)
            self.progress_bar.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="ew")
        
        # İş parçacığını başlat
        thread = threading.Thread(target=self._auto_translate_thread, args=(untranslated, review_mode), daemon=True)
        thread.start()

    def _auto_translate_thread(self, entries_to_translate, review_mode):
        try: 
            translator = GoogleTranslator(source='auto', target='tr')
        except Exception as e: 
            self.after(0, lambda: messagebox.showerror("API Hatası", f"Çeviri servisine bağlanılamadı: {e}"))
            if not review_mode and self.progress_dialog: self.after(0, self.progress_dialog.destroy)
            elif review_mode: self.after(0, self.progress_bar.grid_forget)
            return

        total = len(entries_to_translate); cancelled = False
        update_interval = 10 
        
        for i, entry in enumerate(entries_to_translate):
            
            # İPTAL KONTROLÜ
            if not review_mode and self.progress_dialog and self.progress_dialog.cancelled:
                cancelled = True
                break
            
            try:
                # API KISITLAMASI İÇİN KISA BEKLEME
                translated_text = translator.translate(entry.msgid); time.sleep(0.2) 
                
                if review_mode:
                    dialog = ReviewDialog(self, entry.msgid, translated_text, position=self.last_review_dialog_pos)
                    if dialog.result is not None and dialog.result:
                        entry.msgstr = dialog.result
                    elif dialog.result is None:
                        self.after(0, lambda: messagebox.showinfo("İptal Edildi", "Otomatik çeviri işlemi kullanıcı tarafından iptal edildi."))
                        cancelled = True; break
                else: 
                    entry.msgstr = translated_text
                    
            except Exception as e: 
                print(f"Çeviri hatası: {e}"); 
                continue
            
            # İLERLEME GÜNCELLEMESİ
            current_count = i + 1
            if current_count % update_interval == 0 or current_count == total:
                if not review_mode and self.progress_dialog:
                    # Yeni pencereyi kullan
                    self.after(0, self.progress_dialog.update_progress, current_count)
                elif review_mode:
                    # Ana penceredeki çubuğu kullan
                    progress_value = current_count / total
                    self.after(0, self.progress_bar.set, progress_value)
                
        # Bitiş işlemleri
        if not review_mode and self.progress_dialog:
            self.after(0, self.progress_dialog.destroy)
        elif review_mode:
            self.after(0, self.progress_bar.grid_forget)

        self.after(0, self.refresh_data_display)
        if not cancelled and total > 0: 
            self.after(0, lambda: messagebox.showinfo("Tamamlandı", "Otomatik çeviri işlemi başarıyla tamamlandı."))
        
        # Pencere kapandıktan sonra referansı temizle
        if not review_mode:
             self.progress_dialog = None

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark"); ctk.set_default_color_theme("blue")
    app = POEditorApp(); app.mainloop()