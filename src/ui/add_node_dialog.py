from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QSpinBox, QDialogButtonBox, QScrollArea,
                             QCheckBox, QGroupBox, QWidget, QLabel)


class AddNodeDialog(QDialog):
    def __init__(self, existing_universities, parent=None, edit_data=None):
        super().__init__(parent)
        self.setWindowTitle("Üniversite Ekle / Düzenle")
        self.resize(500, 600)

        self.checkboxes = []
        layout = QVBoxLayout(self)

        # 1. Bilgiler
        form_group = QGroupBox("Üniversite Bilgileri")
        form_layout = QFormLayout()

        self.inp_adi = QLineEdit()
        self.inp_sehir = QLineEdit()
        self.inp_ilce = QLineEdit()
        self.inp_kurulus = QSpinBox();
        self.inp_kurulus.setRange(1000, 2030);
        self.inp_kurulus.setValue(2000)
        self.inp_ogrenci = QSpinBox();
        self.inp_ogrenci.setRange(0, 1000000)
        self.inp_fakulte = QSpinBox()
        self.inp_akademik = QSpinBox();
        self.inp_akademik.setRange(0, 50000)
        self.inp_siralama = QSpinBox();
        self.inp_siralama.setRange(1, 1000)

        # EĞER DÜZENLEME MODUYSA VERİLERİ DOLDUR
        if edit_data:
            self.inp_adi.setText(edit_data.adi)
            self.inp_sehir.setText(edit_data.sehir)
            self.inp_ilce.setText(edit_data.ilce)
            self.inp_kurulus.setValue(edit_data.kurulus_yil)
            self.inp_ogrenci.setValue(edit_data.ogrenci_sayisi)
            try:
                self.inp_fakulte.setValue(int(edit_data.fakulte_sayisi))
            except:
                pass
            self.inp_akademik.setValue(edit_data.akademik_sayisi)
            self.inp_siralama.setValue(edit_data.tr_siralama)

        form_layout.addRow("Üniversite Adı:", self.inp_adi)
        form_layout.addRow("Şehir:", self.inp_sehir)
        form_layout.addRow("İlçe:", self.inp_ilce)
        form_layout.addRow("Kuruluş Yılı:", self.inp_kurulus)
        form_layout.addRow("Öğrenci Sayısı:", self.inp_ogrenci)
        form_layout.addRow("Fakülte Sayısı:", self.inp_fakulte)
        form_layout.addRow("Akademik Personel:", self.inp_akademik)
        form_layout.addRow("TR Sıralaması:", self.inp_siralama)
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # 2. Ortak Çalışmalar (Sadece Ekleme modunda aktif edelim, düzenlemede karmaşık olmasın)
        if not edit_data:
            layout.addWidget(QLabel("<b>Hangi üniversiteler ile ortak akademik çalışma yapıldı?</b>"))
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFixedHeight(150)
            scroll_content = QWidget()
            chk_layout = QVBoxLayout(scroll_content)

            for uni_id, uni_name in existing_universities:
                chk = QCheckBox(uni_name)
                chk.setProperty("uni_id", uni_id)
                chk_layout.addWidget(chk)
                self.checkboxes.append(chk)

            scroll.setWidget(scroll_content)
            layout.addWidget(scroll)

        # 3. Butonlar
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        partners = [chk.property("uni_id") for chk in self.checkboxes if chk.isChecked()]
        info = {
            "adi": self.inp_adi.text(), "sehir": self.inp_sehir.text(), "ilce": self.inp_ilce.text(),
            "kurulus_yil": self.inp_kurulus.value(), "ogrenci_sayisi": self.inp_ogrenci.value(),
            "fakulte_sayisi": str(self.inp_fakulte.value()), "akademik_sayisi": self.inp_akademik.value(),
            "tr_siralama": self.inp_siralama.value()
        }
        return info, partners