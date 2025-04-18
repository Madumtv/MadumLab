#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Fichier : MadumLab.py

import sys, os, re
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QFileDialog, QLabel, QTabWidget,
    QTreeView, QListWidget, QComboBox, QMessageBox, QDialog,
    QDialogButtonBox, QPlainTextEdit, QStyle
)
from PySide6.QtGui import (
    QStandardItemModel, QStandardItem,
    QPixmap, QIcon, QImage, QFont
)
from PySide6.QtCore import Qt

# --- Texte du tutoriel ---
TUTORIEL_HTML = """
<h2>Bienvenue dans MadumLab</h2>
<p>MadumLab propose deux modules indépendants :</p>
<ol>
  <li><strong>Arborescence</strong> : création automatique de structures de dossiers et fichiers à partir d’un arbre ASCII.</li>
  <li><strong>Édition Image</strong> : conversion et redimensionnement d’images vers divers formats.</li>
</ol>
<h3>Module Arborescence</h3>
<ul>
  <li>Sélectionnez un dossier cible.</li>
  <li>Collez ou saisissez votre arbre ASCII.</li>
  <li>Cliquez sur <em>Aperçu</em> pour vérifier la structure.</li>
  <li>Cliquez sur <em>Générer</em> pour créer les dossiers et fichiers.</li>
</ul>
<h3>Module Édition Image</h3>
<ul>
  <li>Sélectionnez une image source.</li>
  <li>Choisissez un dossier de sortie.</li>
  <li>Définissez le format et le nom du fichier.</li>
  <li>Choisissez une taille dans la liste ou ajoutez-en une personnalisée.</li>
  <li>Cliquez sur <em>Générer</em> pour exporter l’image.</li>
</ul>
"""

EXEMPLE_ASCII = """\
route_web/
├── manifest.sii
├── def/
│   └── gui/
│       └── route_web.desc
├── lua/
│   └── route_web.lua
└── web_server/
    ├── package.json
    ├── index.js
    └── public/
        └── index.html
"""

ICO_SIZES = [(256,256), (128,128), (64,64), (32,32), (16,16)]

def parse_tree(text: str):
    parents, paths = [], []
    for line in text.splitlines():
        if not line.strip(): continue
        indent = re.match(r'^([\s│ ]*)', line).group(1)
        depth = len(re.findall(r'(?: {4}|│   )', indent))
        name = re.sub(r'^[\s│]*[├└]──\s*', '', line).strip()
        is_dir = name.endswith('/')
        if is_dir: name = name[:-1]
        parents = parents[:depth]
        rel = os.path.join(*(parents + [name])) if parents or name else name
        paths.append((rel, is_dir))
        if is_dir: parents.append(name)
    return paths

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # détecte script vs onefile
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS
        else:
            base = os.path.dirname(__file__)
        # icône de la fenêtre
        ico = os.path.join(base, "MadumLab.ico")
        if os.path.exists(ico):
            self.setWindowIcon(QIcon(ico))

        self.setWindowTitle("MadumLab")
        self.resize(900, 700)

        tabs = QTabWidget()
        tabs.addTab(self._make_welcome_tab(),    "Bienvenue")
        tabs.addTab(self._make_tree_tab(),       "Arborescence")
        tabs.addTab(self._make_icon_tab(),       "Édition Image")
        self.setCentralWidget(tabs)

    # --- Onglet Bienvenue ---
    def _make_welcome_tab(self):
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS
        else:
            base = os.path.dirname(__file__)
        cand = [
            os.path.join(base, "MadumLab.png"),
            os.path.join(os.getcwd(), "MadumLab.png")
        ]
        logo = next((p for p in cand if os.path.exists(p)), None)

        w = QWidget()
        lo = QVBoxLayout(w); lo.setSpacing(10)

        h = QHBoxLayout()
        tut = QLabel()
        tut.setTextFormat(Qt.RichText)
        tut.setText(TUTORIEL_HTML)
        tut.setWordWrap(True)
        h.addWidget(tut, stretch=3)

        logo_lbl = QLabel()
        if logo:
            px = QPixmap(logo).scaled(200,200,Qt.KeepAspectRatio,Qt.SmoothTransformation)
            logo_lbl.setPixmap(px)
        else:
            logo_lbl.setText("Logo introuvable")
        logo_lbl.setAlignment(Qt.AlignCenter)
        h.addWidget(logo_lbl, stretch=1)

        lo.addLayout(h)

        lo.addWidget(QLabel("Exemple d’arborescence ASCII :"))
        ex = QLabel(EXEMPLE_ASCII)
        f = QFont("Courier New"); ex.setFont(f)
        ex.setTextInteractionFlags(Qt.TextSelectableByMouse)
        ex.setStyleSheet("border:1px solid #ccc; padding:4px;")
        lo.addWidget(ex)

        btn = QPushButton("Copier l’exemple")
        btn.clicked.connect(lambda: (
            QApplication.clipboard().setText(EXEMPLE_ASCII),
            QMessageBox.information(self, "Copié", "Exemple copié dans le presse‑papier.")
        ))
        hb = QHBoxLayout(); hb.addStretch(); hb.addWidget(btn); hb.addStretch()
        lo.addLayout(hb)

        return w

    # --- Onglet Arborescence ---
    def _make_tree_tab(self):
        w = QWidget()
        lo = QVBoxLayout(w); lo.setSpacing(8)

        # dossier cible
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Dossier cible :"))
        self.dest = QLineEdit(); h1.addWidget(self.dest,1)
        b1 = QPushButton("Parcourir…"); b1.clicked.connect(self._browse)
        h1.addWidget(b1)
        lo.addLayout(h1)

        # zone ASCII tree editable
        lo.addWidget(QLabel("Arborescence (ASCII tree) :"))
        self.text_tree = QPlainTextEdit()
        # placeholder grisé
        self.text_tree.setPlaceholderText(EXEMPLE_ASCII)
        self.text_tree.setFont(QFont("Courier New"))
        self.text_tree.setLineWrapMode(QPlainTextEdit.NoWrap)
        lo.addWidget(self.text_tree,1)

        # boutons
        h2 = QHBoxLayout(); h2.addStretch()
        ap = QPushButton("Aperçu"); ap.clicked.connect(self._preview)
        ge = QPushButton("Générer"); ge.clicked.connect(self._generate)
        h2.addWidget(ap); h2.addWidget(ge)
        lo.addLayout(h2)

        # treeview
        lo.addWidget(QLabel("Pré‑aperçu :"))
        self.view = QTreeView()
        self.model = QStandardItemModel(); self.model.setHorizontalHeaderLabels(["Nom"])
        self.view.setModel(self.model)
        lo.addWidget(self.view,1)

        return w

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Choisir dossier cible")
        if d: self.dest.setText(d)

    def _preview(self):
        try:
            items = parse_tree(self.text_tree.toPlainText())
            self.model.removeRows(0,self.model.rowCount())
            nodes = {'':self.model.invisibleRootItem()}
            for rel,is_dir in items:
                parts,par=rel.split(os.sep), ''
                for i,p in enumerate(parts):
                    key = os.path.join(*parts[:i+1])
                    if key not in nodes:
                        it=QStandardItem(p)
                        ic = (QStyle.SP_DirIcon if ((is_dir and i==len(parts)-1) or i<len(parts)-1)
                              else QStyle.SP_FileIcon)
                        it.setIcon(self.style().standardIcon(ic))
                        nodes[par].appendRow(it)
                        nodes[key]=it
                    par=key
            self.view.expandAll()
            QMessageBox.information(self,"Aperçu","Structure mise à jour.")
        except Exception as e:
            QMessageBox.critical(self,"Erreur",str(e))

    def _generate(self):
        base=self.dest.text().strip()
        if not base or not os.path.isdir(base):
            QMessageBox.critical(self,"Erreur","Dossier invalide."); return
        cnt=0
        for rel,is_dir in parse_tree(self.text_tree.toPlainText()):
            full=os.path.join(base,rel)
            if is_dir:
                os.makedirs(full,exist_ok=True)
            else:
                os.makedirs(os.path.dirname(full),exist_ok=True)
                open(full,'w').close()
            cnt+=1
        QMessageBox.information(self,"Succès",f"{cnt} élément(s) créés.")

    # --- Onglet Édition Image ---
    def _make_icon_tab(self):
        w = QWidget()
        lo = QVBoxLayout(w); lo.setSpacing(8)

        # Choix image
        h1 = QHBoxLayout()
        bimg=QPushButton("Choisir image…"); bimg.clicked.connect(self._choose_img)
        self.lbl_img=QLabel("(aucune)"); h1.addWidget(bimg); h1.addWidget(self.lbl_img,1)
        lo.addLayout(h1)

        lo.addWidget(QLabel("Aperçu :"))
        self.lbl_prev=QLabel(alignment=Qt.AlignCenter)
        self.lbl_prev.setFixedSize(256,256)
        self.lbl_prev.setStyleSheet("background:#f0f0f0;")
        lo.addWidget(self.lbl_prev,alignment=Qt.AlignCenter)

        # Dossier sortie
        h2=QHBoxLayout()
        bout=QPushButton("Dossier sortie…"); bout.clicked.connect(self._choose_out)
        self.lbl_out=QLabel("(aucun)"); h2.addWidget(bout); h2.addWidget(self.lbl_out,1)
        lo.addLayout(h2)

        # Format
        hfmt=QHBoxLayout(); hfmt.addWidget(QLabel("Format :"))
        self.fmt=QComboBox(); self.fmt.addItems(["ico","png","jpg","bmp","gif","webp"])
        hfmt.addWidget(self.fmt); lo.addLayout(hfmt)

        # Nom
        hnom=QHBoxLayout(); hnom.addWidget(QLabel("Nom :"))
        self.ent=QLineEdit("MadumLab.ico"); hnom.addWidget(self.ent,1); lo.addLayout(hnom)

        # Tailles
        lo.addWidget(QLabel("Tailles :"))
        self.lst=QListWidget(); lo.addWidget(self.lst)
        h4=QHBoxLayout()
        h4.addWidget(QLabel("W :")); self.wid=QLineEdit(); self.wid.setPlaceholderText("48"); h4.addWidget(self.wid)
        h4.addWidget(QLabel("H :")); self.hei=QLineEdit(); self.hei.setPlaceholderText("48"); h4.addWidget(self.hei)
        badd=QPushButton("Ajouter"); badd.clicked.connect(self._add_size); h4.addWidget(badd)
        lo.addLayout(h4)

        bgen=QPushButton("Générer"); bgen.clicked.connect(self._gen_img)
        lo.addWidget(bgen,alignment=Qt.AlignCenter)

        self._refresh()
        if self.lst.count(): self.lst.setCurrentRow(0)
        return w

    def _choose_img(self):
        path,*_ = QFileDialog.getOpenFileName(self,"Sélectionner image","","Images (*.png *.jpg *.gif *.bmp);;Tous (*)")
        if path:
            self.png=path; self.lbl_img.setText(os.path.basename(path))
            px=QPixmap(path).scaled(256,256,Qt.KeepAspectRatio,Qt.SmoothTransformation)
            self.lbl_prev.setPixmap(px)

    def _choose_out(self):
        d=QFileDialog.getExistingDirectory(self,"Choisir dossier sortie")
        if d: self.out=d; self.lbl_out.setText(d)

    def _add_size(self):
        wt,ht=self.wid.text().strip(),self.hei.text().strip()
        if not wt.isdigit() or not ht.isdigit():
            QMessageBox.warning(self,"Format","W et H entiers."); return
        pair=f"{wt}×{ht}"
        ex=[self.lst.item(i).text() for i in range(self.lst.count())]
        if pair not in ex: self.lst.addItem(pair)
        self.wid.clear(); self.hei.clear()

    def _refresh(self):
        self.lst.clear()
        for w,h in ICO_SIZES: self.lst.addItem(f"{w}×{h}")

    def _gen_img(self):
        if not hasattr(self,"png"):
            QMessageBox.critical(self,"Erreur","Aucune image."); return
        if not hasattr(self,"out"):
            QMessageBox.critical(self,"Erreur","Aucun dossier."); return
        fmt=self.fmt.currentText()
        name=self.ent.text().strip() or f"MadumLab.{fmt}"
        if not name.lower().endswith(f".{fmt}"): name+=f".{fmt}"
        out=os.path.join(self.out,name)
        img=QImage(self.png)
        if img.isNull():
            QMessageBox.critical(self,"Erreur","Impossible charger image."); return
        cur=self.lst.currentItem()
        w,h=(map(int,cur.text().split("×")) if cur else ICO_SIZES[0])
        pix=QPixmap.fromImage(img).scaled(w,h,Qt.KeepAspectRatio,Qt.SmoothTransformation)
        if not pix.save(out,fmt.upper()):
            QMessageBox.critical(self,"Erreur",f"Échec .{fmt}"); return
        dlg=QDialog(self); dlg.setWindowTitle("Succès")
        v=QVBoxLayout(dlg); v.addWidget(QLabel(f"Fichier généré :\n{out}"))
        bb=QDialogButtonBox()
        bb.addButton("Ouvrir dossier",QDialogButtonBox.ActionRole).clicked.connect(lambda: os.startfile(os.path.dirname(out)))
        bb.addButton("Revenir",QDialogButtonBox.RejectRole).clicked.connect(dlg.accept)
        bb.addButton("Quitter",QDialogButtonBox.DestructiveRole).clicked.connect(self.close)
        v.addWidget(bb); dlg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
