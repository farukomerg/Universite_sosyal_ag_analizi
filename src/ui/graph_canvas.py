from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QPoint


class GraphCanvas(QWidget):
    """
    Graf düğümlerini çizer, zoom ve pan (kaydırma) işlemlerini yönetir.
    """

    def __init__(self, graph, on_node_clicked=None, parent=None):
        super().__init__(parent)
        self.graph = graph
        self.on_node_clicked = on_node_clicked  # callback

        # Node yarıçapı
        self.node_radius = 20

        # --- Zoom ve Pan Değişkenleri ---
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.last_mouse_pos = QPoint(0, 0)
        self.is_panning = False
        self.first_resize = True  # İLK AÇILIŞ KONTROLÜ

        self.setStyleSheet("background-color: #f0f0f0;")

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
        # Zoom yapınca yazı çok büyümesin diye fontu ters oranda küçültebiliriz (İsteğe bağlı)
        # font.setPointSizeF(10 / self.scale_factor)
        painter.setFont(font)

        for node in self.graph.nodes.values():
            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(QBrush(QColor("#00FF00")))
            painter.drawEllipse(int(node.x - self.node_radius), int(node.y - self.node_radius),
                                self.node_radius * 2, self.node_radius * 2)

            painter.setPen(QPen(Qt.black))
            painter.drawText(int(node.x - self.node_radius), int(node.y - self.node_radius - 5), node.adi)

        painter.restore()

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