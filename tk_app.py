import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
from PIL import Image

ICO_SIZES = [(256,256), (128,128), (64,64), (32,32), (16,16)]

EXAMPLE_ASCII = "route_web/\n├── manifest.sii\n├── def/\n│   └── gui/\n│       └── route_web.desc\n└── file.txt"

def parse_tree(text: str):
    parents, paths = [], []
    for line in text.splitlines():
        if not line.strip():
            continue
        indent = re.match(r'^([\s│ ]*)', line).group(1)
        depth = len(re.findall(r'(?: {4}|│   )', indent))
        name = re.sub(r'^[\s│]*[├└]──\s*', '', line).strip()
        is_dir = name.endswith('/')
        if is_dir:
            name = name[:-1]
        parents = parents[:depth]
        rel = os.path.join(*(parents + [name])) if parents or name else name
        paths.append((rel, is_dir))
        if is_dir:
            parents.append(name)
    return paths

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MadumLab Tk")
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True)
        nb.add(self.make_tree_tab(), text="Arborescence")
        nb.add(self.make_image_tab(), text="Édition Image")

    # --- Tree tab ---
    def make_tree_tab(self):
        frame = ttk.Frame()
        dest_frame = ttk.Frame(frame)
        dest_frame.pack(fill='x', pady=5)
        ttk.Label(dest_frame, text="Dossier cible:").pack(side='left')
        self.dest = ttk.Entry(dest_frame)
        self.dest.pack(side='left', fill='x', expand=True)
        ttk.Button(dest_frame, text="Parcourir…", command=self.choose_dest).pack(side='left')

        ttk.Label(frame, text="Arborescence:").pack(anchor='w')
        self.tree_text = tk.Text(frame, height=10)
        self.tree_text.insert('1.0', EXAMPLE_ASCII)
        self.tree_text.pack(fill='both', expand=True)

        btn_frame = ttk.Frame(frame); btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Générer", command=self.generate_tree).pack()
        return frame

    def choose_dest(self):
        d = filedialog.askdirectory()
        if d:
            self.dest.delete(0,'end'); self.dest.insert(0,d)

    def generate_tree(self):
        base = self.dest.get().strip()
        if not base:
            messagebox.showerror("Erreur", "Dossier invalide")
            return
        cnt = 0
        for rel, is_dir in parse_tree(self.tree_text.get('1.0','end')):
            full = os.path.join(base, rel)
            if is_dir:
                os.makedirs(full, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(full), exist_ok=True)
                open(full, 'w').close()
            cnt += 1
        messagebox.showinfo("Succès", f"{cnt} élément(s) créés")

    # --- Image tab ---
    def make_image_tab(self):
        frame = ttk.Frame()
        in_frame = ttk.Frame(frame); in_frame.pack(fill='x', pady=5)
        ttk.Button(in_frame, text="Choisir image…", command=self.choose_img).pack(side='left')
        self.img_label = ttk.Label(in_frame, text="(aucune)")
        self.img_label.pack(side='left')

        out_frame = ttk.Frame(frame); out_frame.pack(fill='x', pady=5)
        ttk.Button(out_frame, text="Dossier sortie…", command=self.choose_out).pack(side='left')
        self.out_label = ttk.Label(out_frame, text="(aucun)")
        self.out_label.pack(side='left')

        size_frame = ttk.Frame(frame); size_frame.pack(fill='x', pady=5)
        ttk.Label(size_frame, text="Taille:").pack(side='left')
        self.size_var = tk.StringVar(value="256x256")
        ttk.Entry(size_frame, textvariable=self.size_var, width=10).pack(side='left')

        ttk.Button(frame, text="Générer", command=self.generate_img).pack(pady=5)
        return frame

    def choose_img(self):
        path = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.bmp *.gif")])
        if path:
            self.img_path = path
            self.img_label.config(text=os.path.basename(path))

    def choose_out(self):
        d = filedialog.askdirectory()
        if d:
            self.out_path = d
            self.out_label.config(text=d)

    def generate_img(self):
        if not hasattr(self, 'img_path') or not hasattr(self, 'out_path'):
            messagebox.showerror("Erreur", "Image ou dossier manquant")
            return
        size = self.size_var.get()
        try:
            w, h = map(int, size.lower().replace('x',' ').split())
        except ValueError:
            messagebox.showerror("Erreur", "Taille invalide")
            return
        img = Image.open(self.img_path)
        img = img.resize((w,h), Image.Resampling.LANCZOS)
        name = os.path.splitext(os.path.basename(self.img_path))[0] + f"_{w}x{h}.png"
        out = os.path.join(self.out_path, name)
        img.save(out)
        messagebox.showinfo("Succès", f"Image enregistrée: {out}")

if __name__ == '__main__':
    App().mainloop()
