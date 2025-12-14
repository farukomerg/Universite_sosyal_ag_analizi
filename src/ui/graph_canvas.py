# ui/graph_canvas.py

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QPoint


class GraphCanvas(QWidget):
    """
    Graf düğümlerini çizer, zoom ve pan (kaydırma) işlemlerini yönetir.
    """
    # Renk paleti
    COLOR_PALETTE_INFO = [
        {"id": 1, "name": "Kırmızı", "color": QColor("#FF5733")},
        {"id": 2, "name": "Yeşil", "color": QColor("#33FF57")},
        {"id": 3, "name": "Mavi", "color": QColor("#3357FF")},
        {"id": 4, "name": "Pembe", "color": QColor("#FF33F5")},
        {"id": 5, "name": "Altın Sarısı", "color": QColor("#FFD733")},
        {"id": 6, "name": "Turkuaz", "color": QColor("#33FFF0")},
        {"id": 7, "name": "Mor", "color": QColor("#9933FF")},
        {"id": 8, "name": "Turuncu", "color": QColor("#FF8D33")},
        {"id": 9, "name": "Gri", "color": QColor("#A0A0A0")},
        {"id": 10, "name": "Açık Yeşil", "color": QColor("#33FFC0")}
    ]
    COLOR_PALETTE = [info["color"] for info in COLOR_PALETTE_INFO]

    # Renk ID'sine göre isim bulmak için yardımcı sözlük (Exporter için)
    COLOR_NAME_MAP = {
        info["id"]: info["name"]
        for info in COLOR_PALETTE_INFO
    }

    def __init__(self, graph, on_node_clicked=None, coloring_result=None, parent=None):
        super().__init__(parent)
        self.graph = graph
        self.on_node_clicked = on_node_clicked  # callback
        self.coloring_result = {}


        # Node yarıçapı
        self.node_radius = 20

        # --- Zoom ve Pan Değişkenleri ---
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.last_mouse_pos = QPoint(0, 0)
        self.is_panning = False
        self.first_resize = True  # İLK AÇILIŞ KONTROLÜ

        self.setStyleSheet("background-color: #f0f0f0;")

    def update_coloring(self, coloring: dict):
        """Renklendirme sonucunu günceller ve yeniden çizim ister."""
        self.coloring_result.clear()
        self.coloring_result.update(coloring)
        print("RENKLENDİRME SONUCU GÜNCELLENDİ:", self.coloring_result)
        self.update()

    # ... Diğer metodlar (resizeEvent, fit_view)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.save()
        painter.translate(self.offset)
        painter.scale(self.scale_factor, self.scale_factor)

        # Kenarlar
        pen = QPen(Qt.darkGray, 2)
        painter.setPen(pen)
        for edge in self.graph.edges:
            x1, y1 = edge.node1.x, edge.node1.y
            x2, y2 = edge.node2.x, edge.node2.y
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Düğümler
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        for node in self.graph.nodes.values():
            uni_id = node.uni_id
            color_id = self.coloring_result.get(uni_id)

            # Renk ataması
            if color_id is not None and color_id > 0:
                # Renk paletinden seç, palet dışına çıkarsa döngüsel olarak tekrarla
                color_index = (color_id - 1) % len(self.COLOR_PALETTE)
                fill_color = self.COLOR_PALETTE[color_index]
            else:
                fill_color = QColor("#00FF00")  # Varsayılan yeşil

            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(QBrush(fill_color))

            painter.drawEllipse(int(node.x - self.node_radius), int(node.y - self.node_radius),
                                self.node_radius * 2, self.node_radius * 2)

            painter.setPen(QPen(Qt.black))
            painter.drawText(int(node.x - self.node_radius), int(node.y - self.node_radius - 5), node.adi)

        painter.restore()


    def resizeEvent(self, event):
        """Pencere boyutu değiştiğinde veya ilk açıldığında çalışır."""
        super().resizeEvent(event)
        # Eğer program ilk kez açılıyorsa ve grafikte veri varsa otomatik sığdır
        if self.first_resize and self.graph.nodes:
            self.fit_view()
            self.first_resize = False

    def fit_view(self):
        """Tüm düğümleri ekrana sığdıracak şekilde zoom ve pan ayarı yapar."""
        if not self.graph.nodes:
            return

        xs = [node.x for node in self.graph.nodes.values()]
        ys = [node.y for node in self.graph.nodes.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        graph_width = max_x - min_x
        graph_height = max_y - min_y

        # Eğer tek bir düğüm varsa veya hepsi üst üsteyse genişliği 1 yapma
        if graph_width < 100: graph_width = 100
        if graph_height < 100: graph_height = 100

        padding = 150  # Kenar boşluğunu biraz artırdık
        view_width = self.width()
        view_height = self.height()

        scale_x = view_width / (graph_width + padding)
        scale_y = view_height / (graph_height + padding)

        # --- DÜZELTME BURADA ---
        # Çok fazla küçülmeyi (zoom out) engelle.
        # En fazla %60'a kadar küçülsün, daha fazla küçülmesin.
        new_scale = min(scale_x, scale_y)
        if new_scale < 0.6:
            new_scale = 0.6

        self.scale_factor = new_scale

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        self.offset = QPoint(
            int(view_width / 2 - center_x * self.scale_factor),
            int(view_height / 2 - center_y * self.scale_factor)
        )
        self.update()

    def wheelEvent(self, event):
        zoom_in_factor = 1.1
        zoom_out_factor = 0.9
        if event.angleDelta().y() > 0:
            self.scale_factor *= zoom_in_factor
        else:
            self.scale_factor *= zoom_out_factor
        if self.scale_factor < 0.01: self.scale_factor = 0.01
        if self.scale_factor > 10.0: self.scale_factor = 10.0
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()
            self.is_panning = True

    def mouseMoveEvent(self, event):
        if self.is_panning:
            delta = event.pos() - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_panning = False
            click_pos = event.pos()
            real_x = (click_pos.x() - self.offset.x()) / self.scale_factor
            real_y = (click_pos.y() - self.offset.y()) / self.scale_factor

            for node in self.graph.nodes.values():
                dx = node.x - real_x
                dy = node.y - real_y
                if (dx * dx + dy * dy) <= (self.node_radius ** 2):
                    if self.on_node_clicked:
                        self.on_node_clicked(node)
                    return

