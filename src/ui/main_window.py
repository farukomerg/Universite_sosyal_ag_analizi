from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QVBoxLayout,
                             QHBoxLayout, QFrame, QPushButton, QMessageBox)
from .graph_canvas import GraphCanvas
from .add_node_dialog import AddNodeDialog
from core.node import Node
import random


class MainWindow(QMainWindow):
    def __init__(self, graph, data_loader):
        super().__init__()
        self.graph = graph
        self.loader = data_loader
        self.selected_node = None  # Seçilen düğümü tutmak için

        self.setWindowTitle("Sosyal Ağ Analizi - Üniversite Grafı")
        self.setMinimumSize(1000, 600)

        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QHBoxLayout(container)

        # SOL: Canvas
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

        # 3. Ekle Butonu
        btn_add = QPushButton("➕ Yeni Üniversite Ekle")
        btn_add.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; margin-top: 10px;")
        btn_add.clicked.connect(self.open_add_dialog)
        right_layout.addWidget(btn_add)

        right_layout.addStretch()
        main_layout.addWidget(right_panel, stretch=1)

    def show_node_details(self, node):
        self.selected_node = node
        self.label_adi.setText(node.adi)
        text = f"Kuruluş: {node.kurulus_yil}\nŞehir: {node.sehir}\nİlçe: {node.ilce}\nSıralama: {node.tr_siralama}"
        self.label_detay.setText(text)

        # Butonları aktifleştir
        self.btn_edit.setEnabled(True)
        self.btn_delete.setEnabled(True)

    def open_add_dialog(self):
        existing_unis = self.loader.get_university_names()
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
            self.canvas.update()

    def edit_selected_node(self):
        if not self.selected_node: return

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
            self.selected_node.fakulte_sayisi = int(info["fakulte_sayisi"])
            self.selected_node.akademik_sayisi = info["akademik_sayisi"]
            self.selected_node.tr_siralama = info["tr_siralama"]

            self.show_node_details(self.selected_node)  # Paneli güncelle
            self.canvas.update()  # Grafikteki ismin değişmesi için