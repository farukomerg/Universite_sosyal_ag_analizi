import sqlite3
import networkx as nx
from .node import Node
from .graph import Graph


class DataLoader:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Veritabanı tablolarını (yoksa) oluşturur."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Üniversiteler Tablosu
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS Üniversiteler
                       (
                           uni_id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           adi
                           TEXT,
                           sehir
                           TEXT,
                           ilce
                           TEXT,
                           kurulus_yil
                           INTEGER,
                           ogrenci_sayisi
                           INTEGER,
                           fakulte_sayisi
                           TEXT,
                           akademik_sayisi
                           INTEGER,
                           tr_siralama
                           INTEGER
                       )
                       """)

        # İlişkiler (Edges) Tablosu - YENİ
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS Iliskiler
                       (
                           source_id
                           INTEGER,
                           target_id
                           INTEGER,
                           PRIMARY
                           KEY
                       (
                           source_id,
                           target_id
                       )
                           )
                       """)
        conn.commit()
        conn.close()

    def load_graph(self, graph: Graph):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 1. Node'ları Yükle
        cursor.execute("SELECT * FROM Üniversiteler")
        rows = cursor.fetchall()

        G_nx = nx.Graph()

        for row in rows:
            node = Node(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
            graph.add_node(node)
            G_nx.add_node(node.uni_id)

        # 2. Edge'leri (İlişkileri) Yükle - ARTIK DB'DEN GELİYOR
        cursor.execute("SELECT source_id, target_id FROM Iliskiler")
        edges = cursor.fetchall()

        for u, v in edges:
            if u in graph.nodes and v in graph.nodes:
                # Ağırlığı anlık hesapla
                n1 = graph.nodes[u]
                n2 = graph.nodes[v]
                weight = graph.calculate_weight(n1, n2)
                graph.add_edge(u, v)
                G_nx.add_edge(u, v, weight=weight)

        # 3. Pozisyonlama (Layout)
        pos = nx.spring_layout(G_nx, seed=42, k=0.5)

        scale = 300
        center_x = 400
        center_y = 300

        for uni_id, p in pos.items():
            if uni_id in graph.nodes:
                graph.nodes[uni_id].x = int(center_x + p[0] * scale)
                graph.nodes[uni_id].y = int(center_y + p[1] * scale)

        conn.close()
        return graph

    def get_university_names(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT uni_id, adi FROM Üniversiteler ORDER BY adi ASC")
        data = cursor.fetchall()
        conn.close()
        return data

    def add_university(self, info_dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = """
                INSERT INTO Üniversiteler
                (adi, sehir, ilce, kurulus_yil, ogrenci_sayisi, fakulte_sayisi, akademik_sayisi, tr_siralama)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?) \
                """
        values = (
            info_dict["adi"], info_dict["sehir"], info_dict["ilce"],
            info_dict["kurulus_yil"], info_dict["ogrenci_sayisi"],
            info_dict["fakulte_sayisi"], info_dict["akademik_sayisi"],
            info_dict["tr_siralama"]
        )
        cursor.execute(query, values)
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id

    def add_relation(self, u_id, v_id):
        """İki üniversite arasındaki ilişkiyi DB'ye kaydeder."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Çift yönlü kontrol (1-2 ve 2-1 aynıdır, ama basitlik için direkt ekliyoruz, unique constraint var)
        try:
            # ID'leri sıralı kaydedelim ki (1,2) ile (2,1) aynı olsun
            s, t = sorted((u_id, v_id))
            cursor.execute("INSERT OR IGNORE INTO Iliskiler (source_id, target_id) VALUES (?, ?)", (s, t))
            conn.commit()
        except:
            pass
        conn.close()

    def delete_university(self, uni_id):
        """Üniversiteyi ve ilişkilerini siler."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Üniversiteler WHERE uni_id = ?", (uni_id,))
        cursor.execute("DELETE FROM Iliskiler WHERE source_id = ? OR target_id = ?", (uni_id, uni_id))
        conn.commit()
        conn.close()

    def update_university(self, uni_id, info):
        """Üniversite bilgilerini günceller."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = """
                UPDATE Üniversiteler \
                SET adi=?, \
                    sehir=?, \
                    ilce=?, \
                    kurulus_yil=?, \
                    ogrenci_sayisi=?, \
                    fakulte_sayisi=?, \
                    akademik_sayisi=?, \
                    tr_siralama=?
                WHERE uni_id = ? \
                """
        values = (
            info["adi"], info["sehir"], info["ilce"],
            info["kurulus_yil"], info["ogrenci_sayisi"],
            info["fakulte_sayisi"], info["akademik_sayisi"],
            info["tr_siralama"], uni_id
        )
        cursor.execute(query, values)
        conn.commit()
        conn.close()