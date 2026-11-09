import os
import shutil
import zipfile
import subprocess
import platform
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Elementos esenciales y obligatorios de Unity (ahora incluye Packages)
ELEMENTOS_OBLIGATORIOS = ["Assets", "ProjectSettings", "Packages"]

# Elementos opcionales restantes que se pueden incluir o excluir
ELEMENTOS_OPCIONALES = ["Library", "UserSettings", "Logs", "obj"]

class UnityZipExporterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Unity Project Zip Exporter")
        self.root.geometry("600x650")
        self.root.minsize(550, 600)

        # Variables de estado
        self.proyecto_path = tk.StringVar()
        self.nombre_zip_var = tk.StringVar(value="proyecto_unity_exportado")
        self.checks_vars = {} # Almacenará los BooleanVar de cada elemento
        self.custom_entries = [] # Para almacenar widgets de elementos personalizados

        self.crear_interfaz()

    def crear_interfaz(self):
        # --- MARCO SUPERIOR: Selección de Proyecto ---
        frame_top = ttk.LabelFrame(self.root, text=" 1. Seleccionar Proyecto de Unity ", padding=15)
        frame_top.pack(fill="x", padx=15, pady=10)

        self.lbl_ruta = ttk.Label(frame_top, text="Ninguna carpeta seleccionada", foreground="gray", wraplength=400)
        self.lbl_ruta.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_examinar = ttk.Button(frame_top, text="Examinar...", command=self.seleccionar_carpeta)
        btn_examinar.pack(side="right")

        # --- MARCO CENTRAL: Checklist de Archivos/Carpetas ---
        self.frame_checklist = ttk.LabelFrame(self.root, text=" 2. Elementos a Incluir en el .ZIP ", padding=15)
        self.frame_checklist.pack(fill="both", expand=True, padx=15, pady=5)

        lbl_info = ttk.Label(self.frame_checklist, text="Los elementos obligatorios no se pueden desmarcar:", font=("Segoe UI", 9, "italic"))
        lbl_info.pack(anchor="w", pady=(0, 5))

        # Contenedor con scroll para los checkboxes por si la lista crece
        self.canvas_scroll = tk.Canvas(self.frame_checklist, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.frame_checklist, orient="vertical", command=self.canvas_scroll.yview)
        self.scrollable_frame = ttk.Frame(self.canvas_scroll)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))
        )

        self.canvas_scroll.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas_scroll.configure(yscrollcommand=self.scrollbar.set)

        self.canvas_scroll.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Rellenar checklist inicial
        self.construir_checklist_inicial()

        # --- MARCO AÑADIR PERSONALIZADOS ---
        frame_add = ttk.Frame(self.frame_checklist)
        frame_add.pack(fill="x", pady=(10, 0))

        ttk.Label(frame_add, text="Extra:").pack(side="left", padx=(0, 5))

        self.txt_custom = ttk.Entry(frame_add)
        self.txt_custom.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_add = ttk.Button(frame_add, text="Añadir extra", command=lambda: self.agregar_item_personalizado())
        btn_add.pack(side="right")

        # --- MARCO INFERIOR: Nombre y Exportación ---
        frame_bottom = ttk.LabelFrame(self.root, text=" 3. Configuración y Exportación ", padding=15)
        frame_bottom.pack(fill="x", padx=15, pady=10)

        lbl_nombre = ttk.Label(frame_bottom, text="Nombre del archivo .zip:")
        lbl_nombre.pack(anchor="w")

        frame_nombre_input = ttk.Frame(frame_bottom)
        frame_nombre_input.pack(fill="x", pady=(5, 10))

        self.ent_nombre = ttk.Entry(frame_nombre_input, textvariable=self.nombre_zip_var)
        self.ent_nombre.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Label(frame_nombre_input, text=".zip").pack(side="left")

        self.btn_exportar = ttk.Button(frame_bottom, text="Exportar a Descargas y Abrir", command=self.exportar_proyecto, state="disabled")
        self.btn_exportar.pack(fill="x", pady=5)

    def construir_checklist_inicial(self):
        # Obligatorios (Assets, ProjectSettings, Packages bloqueados)
        for item in ELEMENTOS_OBLIGATORIOS:
            var = tk.BooleanVar(value=True)
            self.checks_vars[item] = {"var": var, "custom": False}
            chk = ttk.Checkbutton(self.scrollable_frame, text=f"{item} (Obligatorio)", variable=var, state="disabled")
            chk.pack(anchor="w", pady=2)

        # Opcionales por defecto
        for item in ELEMENTOS_OPCIONALES:
            var = tk.BooleanVar(value=True if item in ["UserSettings"] else False)
            self.checks_vars[item] = {"var": var, "custom": False}
            chk = ttk.Checkbutton(self.scrollable_frame, text=item, variable=var)
            chk.pack(anchor="w", pady=2)

    def seleccionar_carpeta(self):
        dir_selected = filedialog.askdirectory(title="Selecciona la carpeta raíz del proyecto de Unity")
        if dir_selected:
            self.proyecto_path.set(dir_selected)
            path_mostrar = dir_selected if len(dir_selected) < 50 else "..." + dir_selected[-47:]
            self.lbl_ruta.config(text=path_mostrar, foreground="black")
            self.btn_exportar.config(state="normal")
            
            nombre_carpeta = os.path.basename(dir_selected)
            if nombre_carpeta:
                self.nombre_zip_var.set(f"{nombre_carpeta}_export")

    def agregar_item_personalizado(self):
        nombre_item = self.txt_custom.get().strip()
        if not nombre_item:
            messagebox.showwarning("Aviso", "Escribe el nombre del archivo o carpeta a añadir.")
            return
        
        if nombre_item in self.checks_vars:
            messagebox.showinfo("Información", "Este elemento ya está en la lista.")
            return

        var = tk.BooleanVar(value=True)
        self.checks_vars[nombre_item] = {"var": var, "custom": True}

        row_frame = ttk.Frame(self.scrollable_frame)
        row_frame.pack(anchor="w", fill="x", pady=2)

        chk = ttk.Checkbutton(row_frame, text=f"{nombre_item} (Personalizado)", variable=var)
        chk.pack(side="left")

        btn_del = ttk.Button(row_frame, text="🗑", width=3, command=lambda: self.eliminar_item_personalizado(nombre_item, row_frame))
        btn_del.pack(side="right", padx=5)

        self.txt_custom.delete(0, tk.END)

    def eliminar_item_personalizado(self, nombre_item, row_frame):
        if nombre_item in self.checks_vars:
            del self.checks_vars[nombre_item]
        row_frame.destroy()

    def obtener_ruta_descargas(self):
        ruta_descargas = None
        if platform.system() == "Windows":
            import ctypes
            try:
                SHGetKnownFolderPath = ctypes.windll.shell32.SHGetKnownFolderPath
                KNOWN_FOLDER_ID = ctypes.c_wchar_p("{374DE290-123F-4565-9164-39C4925E467B}")
                p_path = ctypes.c_wchar_p()
                # Intentar obtener la carpeta de descargas del sistema
                if SHGetKnownFolderPath(KNOWN_FOLDER_ID, 0, None, ctypes.byref(p_path)) == 0:
                    ruta_descargas = p_path.value
            except Exception:
                pass
        
        # Si falló la API o estamos en otro SO, usar el método estándar basado en el usuario
        if not ruta_descargas:
            ruta_descargas = os.path.join(os.path.expanduser("~"), "Downloads")
            
        return ruta_descargas

    def abrir_carpeta(self, ruta):
        sistema = platform.system()
        try:
            if sistema == "Windows":
                os.startfile(ruta)
            elif sistema == "Darwin":
                subprocess.run(["open", ruta])
            else:
                subprocess.run(["xdg-open", ruta])
        except Exception as e:
            print(f"No se pudo abrir la carpeta automáticamente: {e}")

    def exportar_proyecto(self):
        dir_proyecto = self.proyecto_path.get()
        nombre_zip = self.nombre_zip_var.get().strip()

        if not dir_proyecto or not os.path.isdir(dir_proyecto):
            messagebox.showerror("Error", "La ruta del proyecto de Unity no es válida.")
            return

        if not nombre_zip:
            messagebox.showerror("Error", "Introduce un nombre válido para el archivo .zip.")
            return

        if nombre_zip.endswith(".zip"):
            nombre_zip = nombre_zip[:-4]

        dir_descargas = self.obtener_ruta_descargas()
        if not os.path.exists(dir_descargas):
            try:
                os.makedirs(dir_descargas)
            except:
                dir_descargas = os.getcwd()

        ruta_zip_final = os.path.join(dir_descargas, f"{nombre_zip}.zip")

        elementos_a_incluir = [item for item, datos in self.checks_vars.items() if datos["var"].get()]

        try:
            self.btn_exportar.config(state="disabled", text="Comprimiendo...")
            self.root.update()

            count_archivos = 0
            with zipfile.ZipFile(ruta_zip_final, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for item in elementos_a_incluir:
                    ruta_elemento = os.path.join(dir_proyecto, item)
                    
                    if os.path.isfile(ruta_elemento):
                        zipf.write(ruta_elemento, arcname=item)
                        count_archivos += 1
                    elif os.path.isdir(ruta_elemento):
                        for root_dir, dirs, files in os.walk(ruta_elemento):
                            for file in files:
                                ruta_completa = os.path.join(root_dir, file)
                                arcname = os.path.relpath(ruta_completa, dir_proyecto)
                                zipf.write(ruta_completa, arcname=arcname)
                                count_archivos += 1

            messagebox.showinfo(
                "¡Éxito!", 
                f"Proyecto exportado correctamente.\n\nUbicación:\n{ruta_zip_final}\n\nArchivos añadidos: {count_archivos}"
            )

            self.abrir_carpeta(dir_descargas)

        except Exception as e:
            messagebox.showerror("Error de compresión", f"Ocurrió un error al generar el archivo ZIP:\n{str(e)}")
        finally:
            self.btn_exportar.config(state="normal", text="Exportar a Descargas y Abrir")

if __name__ == "__main__":
    root = tk.Tk()
    app = UnityZipExporterApp(root)
    root.mainloop()