# ui/main_window.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QVBoxLayout,
                             QHBoxLayout, QFrame, QPushButton, QMessageBox)
from PyQt5.QtGui import QColor
from .graph_canvas import GraphCanvas
from .add_node_dialog import AddNodeDialog
from .coloring_dialog import ColoringDialog  # YENİ
# GÜNCELLEME: İçe aktarma yolu düzeltildi
from core.node import Node
import random
import time


class MainWindow(QMainWindow):
    def __init__(self, graph, data_loader):
        super().__init__()
        self.graph = graph
        self.loader = data_loader
        self.selected_node = None  # Seçilen düğümü tutmak için
        self.coloring_result = {}  # Renklendirme sonucunu tutmak için YENİ

        self.setWindowTitle("Sosyal Ağ Analizi - Üniversite Grafı")
        self.setMinimumSize(1000, 600)

        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QHBoxLayout(container)

        # SOL: Canvas
        # Renklendirme sonucunu canvas'a iletmek için güncellendi
        self.canvas = GraphCanvas(graph, on_node_clicked=self.show_node_details)
        main_layout.addWidget(self.canvas, stretch=3)

        # SAĞ: Panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Bilgi Paneli
        self.info_panel = QFrame()
        self.info_panel.setFrameShape(QFrame.StyledPanel)
        info_layout = QVBoxLayout(self.info_panel)

        self.label_adi = QLabel("Seçim Yapılmadı");
        self.label_adi.setStyleSheet("font-weight:bold")
        self.label_detay = QLabel("")

        info_layout.addWidget(QLabel("<h3>Üniversite Bilgileri</h3>"))
        info_layout.addWidget(self.label_adi)
        info_layout.addWidget(self.label_detay)
        info_layout.addStretch()
        right_layout.addWidget(self.info_panel)

        # --- BUTON GRUBU ---

        # 1. Düzenle Butonu
        self.btn_edit = QPushButton("✏️ Düzenle")
        self.btn_edit.clicked.connect(self.edit_selected_node)
        self.btn_edit.setEnabled(False)  # Başlangıçta pasif
        right_layout.addWidget(self.btn_edit)

        # 2. Sil Butonu
        self.btn_delete = QPushButton("🗑️ Sil")
        self.btn_delete.setStyleSheet("background-color: #f44336; color: white;")
        self.btn_delete.clicked.connect(self.delete_selected_node)
        self.btn_delete.setEnabled(False)  # Başlangıçta pasif
        right_layout.addWidget(self.btn_delete)

        # 3. Renklendirme Butonu (YENİ)
        btn_color = QPushButton("🎨 Renklendir (Welsh-Powell)")
        btn_color.setStyleSheet("background-color: #33aaff; color: white; font-weight: bold; margin-top: 10px;")
        btn_color.clicked.connect(self.run_coloring)
        right_layout.addWidget(btn_color)

        # 4. Ekle Butonu
        btn_add = QPushButton("➕ Yeni Üniversite Ekle")
        btn_add.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; margin-top: 10px;")
        btn_add.clicked.connect(self.open_add_dialog)
        right_layout.addWidget(btn_add)

        right_layout.addStretch()
        main_layout.addWidget(right_panel, stretch=1)

    # ... Diğer metodlar (show_node_details, open_add_dialog, save_university, delete_selected_node, edit_selected_node)

    # Renklendirme Metodu (YENİ)
    def run_coloring(self):
        print("NODE SAYISI:", len(self.graph.nodes))
        print("EDGE SAYISI:", len(self.graph.edges))
        print("ADJ:", self.graph.adj)

        node_count = len(self.graph.nodes)
        if node_count == 0:
            QMessageBox.warning(self, "Uyarı", "Grafikte renklendirilecek düğüm yok.")
            return

        QMessageBox.information(
            self,
            "İşlem Başladı",
            f"Welsh-Powell algoritması {node_count} düğüm üzerinde çalışıyor..."
        )

        try:
            # ⏱ BAŞLANGIÇ ZAMANI
            start_time = time.perf_counter()

            # 🎨 ALGORİTMA
            new_coloring = self.graph.welsh_powell_coloring()

            # ⏱ BİTİŞ ZAMANI
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time

            if not new_coloring:
                QMessageBox.critical(self, "Hata", "Algoritma boş sonuç döndürdü!")
                return

            self.canvas.update_coloring(new_coloring)
            self.coloring_result = new_coloring.copy()

            dialog = ColoringDialog(self.graph, self.coloring_result, self)
            dialog.exec_()

            used_colors = len(set(self.coloring_result.values()))

            QMessageBox.information(
                self,
                "Başarılı",
                f"Graf başarıyla renklendirildi.\n\n"
                f"• Düğüm Sayısı: {node_count}\n"
                f"• Kullanılan Renk: {used_colors}\n"
                f"• Çalışma Süresi: {elapsed_time:.6f} saniye"
            )

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Renklendirme hatası: {e}")

    # Mevcut metotlar (Kesilen kısımlar)
    def show_node_details(self, node):
        self.selected_node = node
        self.label_adi.setText(node.adi)
        # Eğer renklendirme yapıldıysa, detaylara renk ID'sini ekle
        color_id_text = f"Renk ID: {self.coloring_result.get(node.uni_id, 'Yok')}\n" if self.coloring_result else ""
        text = f"{color_id_text}Kuruluş: {node.kurulus_yil}\nŞehir: {node.sehir}\nİlçe: {node.ilce}\nSıralama: {node.tr_siralama}"
        self.label_detay.setText(text)

        # Butonları aktifleştir
        self.btn_edit.setEnabled(True)
        self.btn_delete.setEnabled(True)

    def open_add_dialog(self):
        existing_unis = self.loader.get_university_names()
        # AddNodeDialog'un import edilmesi gerekiyor
        from .add_node_dialog import AddNodeDialog
        dialog = AddNodeDialog(existing_unis, self)
        if dialog.exec_():
            info, partners = dialog.get_data()
            self.save_university(info, partners)

    def save_university(self, info, partners):
        try:
            new_id = self.loader.add_university(info)
            new_node = Node(new_id, info["adi"], info["sehir"], info["ilce"],
                            info["kurulus_yil"], info["ogrenci_sayisi"],
                            int(info["fakulte_sayisi"]), info["akademik_sayisi"], info["tr_siralama"])

            # Rastgele konum ata
            cx = (self.canvas.width() / 2 - self.canvas.offset.x()) / self.canvas.scale_factor
            cy = (self.canvas.height() / 2 - self.canvas.offset.y()) / self.canvas.scale_factor
            new_node.x = cx + random.randint(-50, 50)
            new_node.y = cy + random.randint(-50, 50)

            self.graph.add_node(new_node)

            # İlişkileri hem grafa hem DB'ye ekle
            for pid in partners:
                if pid in self.graph.nodes:
                    # DB Kaydı
                    self.loader.add_relation(new_id, pid)
                    # Graph Kaydı
                    self.graph.add_edge(new_id, pid)

            self.canvas.update()
            QMessageBox.information(self, "Başarılı", "Üniversite eklendi!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def delete_selected_node(self):
        if not self.selected_node: return

        reply = QMessageBox.question(self, 'Onay',
                                     f"{self.selected_node.adi} silinecek. Emin misin?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 1. DB'den sil
            self.loader.delete_university(self.selected_node.uni_id)
            # 2. Graph'tan sil
            self.graph.remove_node(self.selected_node.uni_id)
            # 3. UI Temizle
            self.selected_node = None
            self.label_adi.setText("Silindi")
            self.label_detay.setText("")
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)

            # Renklendirme sonucundan sil
            if self.coloring_result and self.selected_node.uni_id in self.coloring_result:
                del self.coloring_result[self.selected_node.uni_id]

            self.canvas.update()

    def edit_selected_node(self):
        if not self.selected_node: return

        # AddNodeDialog'un import edilmesi gerekiyor
        from .add_node_dialog import AddNodeDialog

        # Mevcut veriyi dialoga gönder
        dialog = AddNodeDialog([], self, edit_data=self.selected_node)
        if dialog.exec_():
            info, _ = dialog.get_data()

            # DB güncelle
            self.loader.update_university(self.selected_node.uni_id, info)

            # Bellekteki Node'u güncelle
            self.selected_node.adi = info["adi"]
            self.selected_node.sehir = info["sehir"]
            self.selected_node.ilce = info["ilce"]
            self.selected_node.kurulus_yil = info["kurulus_yil"]
            self.selected_node.ogrenci_sayisi = info["ogrenci_sayisi"]
            # None kontrolü eklenebilir, ancak mevcut yapıda zaten int'e dönüştürülüyor
            self.selected_node.fakulte_sayisi = int(info["fakulte_sayisi"])
            self.selected_node.akademik_sayisi = info["akademik_sayisi"]
            self.selected_node.tr_siralama = info["tr_siralama"]

            self.show_node_details(self.selected_node)  # Paneli güncelle
            self.canvas.update()  # Grafikteki ismin değişmesi için