# core/graph.py

import math
from .node import Node
from .edge import Edge
from datetime import datetime
import heapq


class Graph:
    """
    Üniversiteler arası sosyal ağ grafı.
    Düğümler Node objeleri,
    Kenarlar Edge objeleri olarak saklanır.
    """

    def __init__(self):
        self.nodes = {}  # uni_id → Node
        self.edges = []  # Edge listesi
        # YENİ: Komşuluk listesi (Adjacency List)
        # {uni_id: set(neighbor_id, ...)}
        self.adj = {}

        # -----------------------

    # NODE YÖNETİMİ
    # -----------------------
    def add_node(self, node: Node):
        if node.uni_id in self.nodes:
            raise ValueError(f"Node already exists: {node.uni_id}")
        self.nodes[node.uni_id] = node
        self.adj[node.uni_id] = set()  # YENİ: Düğüm eklenince komşuluk listesini başlat

    def remove_node(self, uni_id: int):
        if uni_id not in self.nodes:
            return

        # Komşuluk listesinden ve kenar listesinden sil
        if uni_id in self.adj:
            neighbors_to_remove = list(self.adj[uni_id])
            for neighbor_id in neighbors_to_remove:
                if neighbor_id in self.adj:
                    self.adj[neighbor_id].discard(uni_id)  # Komşunun listesinden de sil

        del self.adj[uni_id]  # Kendi komşuluk listesini sil

        self.edges = [e for e in self.edges
                      if e.node1.uni_id != uni_id and e.node2.uni_id != uni_id]

        del self.nodes[uni_id]

    # -----------------------
    # EDGE YÖNETİMİ
    # -----------------------
    def add_edge(self, node_id1: int, node_id2: int):
        if node_id1 == node_id2:
            raise ValueError("Self-loop edge oluşturulamaz.")

        n1 = self.nodes.get(node_id1)
        n2 = self.nodes.get(node_id2)

        if not n1 or not n2:
            raise ValueError("Node bulunamadı.")

        # HIZLI KONTROL: Komşuluk listesi ile kenar mevcut mu?
        if node_id2 in self.adj.get(node_id1, set()):
            return  # Çift eklemeyi engelle

        # Kenarı ekle
        weight = self.calculate_weight(n1, n2)
        self.edges.append(Edge(n1, n2, weight))

        # YENİ: Komşuluk listesini güncelle
        self.adj[node_id1].add(node_id2)
        self.adj[node_id2].add(node_id1)

    def remove_edge(self, node_id1: int, node_id2: int):
        # YENİ: Komşuluk listesini güncelle
        if node_id1 in self.adj:
            self.adj[node_id1].discard(node_id2)
        if node_id2 in self.adj:
            self.adj[node_id2].discard(node_id1)

        # Kenar listesini temizle (daha yavaş olan kısım)
        self.edges = [
            e for e in self.edges
            if not (
                    (e.node1.uni_id == node_id1 and e.node2.uni_id == node_id2) or
                    (e.node1.uni_id == node_id2 and e.node2.uni_id == node_id1)
            )
        ]

    # -----------------------
    # DİNAMİK AĞIRLIK HESABI
    # -----------------------
    def calculate_weight(self, n1: Node, n2: Node) -> float:
        """
        PDF'deki DOĞRU Formül:
        Weight = 1 + sqrt( (AktiflikFarkı)^2 + (EtkileşimFarkı)^2 + ... )
        """
        # None kontrolü (Veritabanında boş veri varsa 0 sayalım)
        akademik_1 = n1.akademik_sayisi if n1.akademik_sayisi else 0
        akademik_2 = n2.akademik_sayisi if n2.akademik_sayisi else 0

        siralama_1 = n1.tr_siralama if n1.tr_siralama else 1000  # Boşsa kötü sıralama varsay
        siralama_2 = n2.tr_siralama if n2.tr_siralama else 1000

        ogrenci_1 = n1.ogrenci_sayisi if n1.ogrenci_sayisi else 0
        ogrenci_2 = n2.ogrenci_sayisi if n2.ogrenci_sayisi else 0

        now = 2025  # Sabit yıl veya datetime.now().year
        yas_1 = now - (n1.kurulus_yil if n1.kurulus_yil else 2000)
        yas_2 = now - (n2.kurulus_yil if n2.kurulus_yil else 2000)

        # Farkların Karesi
        fark_akademik = (akademik_1 - akademik_2) ** 2
        fark_siralama = (siralama_1 - siralama_2) ** 2
        fark_ogrenci = (ogrenci_1 - ogrenci_2) ** 2
        fark_yas = (yas_1 - yas_2) ** 2

        # Formül: 1 + Karekök(Toplam Fark)
        # Farklılık arttıkça Maliyet artar. Benzerler arası maliyet düşer.
        # Ölçekleme (Scale) sorunu olmaması için farkları normalize etmek gerekebilir ama
        # PDF formülü direkt istiyor:
        total_diff = fark_akademik + fark_siralama + fark_ogrenci + fark_yas
        weight = 1 + math.sqrt(total_diff)

        return weight

    # -----------------------
    # GRAF ANALİZİ / RENKLENDİRME DESTEK
    # -----------------------
    def get_neighbors(self, uni_id: int):
        """Bir düğümün komşularını döndürür. O(1) veya O(Derece)"""
        # HIZLI ERİŞİM
        return self.adj.get(uni_id, set())

    def get_degree(self, uni_id: int) -> int:
        """Bir düğümün derecesini döndürür. O(1)"""
        return len(self.get_neighbors(uni_id))

    def welsh_powell_coloring(self) -> dict:
        """
        Welsh-Powell graf renklendirme algoritmasını uygular.
        Sonuç: {uni_id: renk_id}
        """
        if not self.nodes:
            return {}

        coloring = {}
        color_id = 1
        uncolored_nodes = set(self.nodes.keys())

        # Ana renklendirme döngüsü
        while uncolored_nodes:

            # 1. Henüz boyanmamış düğümleri azalan dereceye göre sırala (O(N log N))
            # SADECE renklendirilmemiş düğümleri al
            uncolored_list = list(uncolored_nodes)

            # Renklendirilmemiş düğümlerin derecelerini hesapla
            current_degrees = {uni_id: self.get_degree(uni_id) for uni_id in uncolored_list}

            # Azalan dereceye göre sırala (Bu, Welsh-Powell'ın kilit adımıdır)
            sorted_uncolored_ids = sorted(uncolored_list,
                                          key=lambda uni_id: current_degrees[uni_id],
                                          reverse=True)

            # Eğer sıralanacak düğüm kalmadıysa (normalde olmaması gerekir)
            if not sorted_uncolored_ids:
                break

            nodes_to_color_with_current = []

            # 2. Mevcut renkle boyanacak düğümleri seç
            for uni_id in sorted_uncolored_ids:

                # uni_id zaten uncolored_nodes'un içinden geldiği için tekrar kontrol etmeye gerek yok
                is_adjacent_to_colored = False

                current_node_neighbors = self.get_neighbors(uni_id)

                # Bu düğüm, nodes_to_color_with_current listesindeki herhangi bir düğüme komşu mu?
                for colored_node_id in nodes_to_color_with_current:
                    # Komşuluk kontrolü: O(Derece * Seçilen Düğüm Sayısı)
                    if colored_node_id in current_node_neighbors:
                        is_adjacent_to_colored = True
                        break

                # Eğer komşu değilse, bu renkle boyanabilir
                if not is_adjacent_to_colored:
                    nodes_to_color_with_current.append(uni_id)

            # 3. Seçilen düğümleri boya ve listeden çıkar
            if not nodes_to_color_with_current:
                # BU NOKTADA HATA VARSA: Bu, uncolored_nodes içinde düğüm olmasına rağmen
                # hiçbirine renk atanamadığı anlamına gelir.
                # Algoritma doğruysa bu olmaz. Eğer oluyorsa, tüm renklendirilmemiş düğümler
                # (uncolored_nodes) kendi aralarında tam bir küme oluşturuyor olmalı, ki bu
                # imkansızdır çünkü en azından en yüksek dereceli ilk düğüm seçilmelidir.
                # Eğer buraya düşüyorsanız, komşuluk listesi (self.adj) BOŞ demektir.
                # DataLoader'da kenarların doğru yüklendiğinden emin olun.
                print(f"HATA: {color_id}. renkte düğüm atanamadı. Komşuluk listelerini kontrol edin.")
                break

            for uni_id in nodes_to_color_with_current:
                coloring[uni_id] = color_id
                uncolored_nodes.remove(uni_id)

            # Sonraki renge geç
            color_id += 1

        return coloring

    def dijkstra(self, start_id: int, end_id: int):
        """
        Dijkstra algoritması ile en kısa yolu bulur.
        Dönüş: (toplam_maliyet, yol_listesi) -> (float, [Node, Node, ...])
        """
        if start_id not in self.nodes or end_id not in self.nodes:
            return float('inf'), []

        # Priority Queue: (Maliyet, Şu anki Node ID)
        # Başlangıç noktasının maliyeti 0
        queue = [(0, start_id)]

        # En kısa mesafeleri tutan sözlük (Sonsuz ile başlat)
        distances = {node_id: float('inf') for node_id in self.nodes}
        distances[start_id] = 0

        # Yolu geri takip etmek için (Nereden geldik?)
        predecessors = {node_id: None for node_id in self.nodes}

        while queue:
            current_cost, current_id = heapq.heappop(queue)

            # Eğer hedefi bulduysak döngüyü kır (Erken çıkış)
            if current_id == end_id:
                break

            # Eğer bulduğumuz yol, zaten bildiğimizden daha uzunsa atla
            if current_cost > distances[current_id]:
                continue

            # Komşuları gez
            # self.adj[current_id] komşuluk setidir
            for neighbor_id in self.adj.get(current_id, set()):
                n1 = self.nodes[current_id]
                n2 = self.nodes[neighbor_id]

                # Ağırlığı dinamik hesapla
                weight = self.calculate_weight(n1, n2)
                distance = current_cost + weight

                # Eğer daha kısa bir yol bulduysak güncelle
                if distance < distances[neighbor_id]:
                    distances[neighbor_id] = distance
                    predecessors[neighbor_id] = current_id
                    heapq.heappush(queue, (distance, neighbor_id))

        # --- YOLU GERİ OLUŞTURMA (Backtracking) ---
        path = []
        curr = end_id

        # Hedefe hiç ulaşılmadıysa
        if distances[end_id] == float('inf'):
            return float('inf'), []

        while curr is not None:
            path.insert(0, self.nodes[curr])
            curr = predecessors[curr]

        return distances[end_id], path

    # -----------------------
    # GRAF SELLEŞTİRME DESTEK FONK.
    # -----------------------
    def __repr__(self):
        return f"Graph(nodes={len(self.nodes)}, edges={len(self.edges)})"

    def bfs(self, start_id: int):
        """
        Breadth-First Search (Sığ Öncelikli Arama).
        Yakındaki komşulardan başlayarak dalga dalga yayılır.
        Dönüş: Ziyaret sırasına göre Node listesi.
        """
        if start_id not in self.nodes:
            return []

        visited = set()
        queue = [start_id]
        visited.add(start_id)
        order = []  # Ziyaret sırası

        while queue:
            current_id = queue.pop(0)  # Kuyruğun başından al
            order.append(self.nodes[current_id])

            # Komşuları gez
            # self.adj[current_id] set olduğu için sıralı gelmeyebilir,
            # görsel tutarlılık için sorted() diyebiliriz (isteğe bağlı)
            for neighbor_id in sorted(list(self.adj.get(current_id, set()))):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append(neighbor_id)

        return order

    def dfs(self, start_id: int):
        """
        Depth-First Search (Derin Öncelikli Arama).
        Bir kolda gidebildiği kadar derine gider, sonra geri döner.
        Dönüş: Ziyaret sırasına göre Node listesi.
        """
        if start_id not in self.nodes:
            return []

        visited = set()
        stack = [start_id]  # Yığın kullanıyoruz
        order = []

        while stack:
            current_id = stack.pop()  # Yığının sonundan al

            if current_id not in visited:
                visited.add(current_id)
                order.append(self.nodes[current_id])

                # Komşuları yığına ekle
                # (Ters sıralarsak, küçük ID'li komşuya önce gider - görsel tercih)
                neighbors = sorted(list(self.adj.get(current_id, set())), reverse=True)
                for neighbor_id in neighbors:
                    if neighbor_id not in visited:
                        stack.append(neighbor_id)

        return order