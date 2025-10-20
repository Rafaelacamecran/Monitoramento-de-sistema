import psutil
import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import csv

class SystemMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor e Limpeza de Sistema v2.0 (Modo Simulação)")
        self.root.geometry("850x650")

        # Variáveis de controle
        self.monitoring = False
        self.scanning = False
        self.found_files = []
        self.simulation_mode = tk.BooleanVar(value=True) # Modo simulação ativo por padrão
        
        # Configuração de diretório de logs e relatórios
        self.log_dir = r"D:\Meus projetos\Monitoramento de sistemas"
        self.action_log_file = None
        
        self.setup_logging_dir()

        # Criação da Interface com Abas
        self.create_widgets()

    def setup_logging_dir(self):
        """Cria o diretório de logs se não existir."""
        try:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
        except OSError as e:
            messagebox.showerror(
                "Erro de Permissão",
                f"Não foi possível criar o diretório de trabalho em:\n{self.log_dir}\n\n"
                f"Erro: {e}\n\nVerifique as permissões ou execute como administrador."
            )
            self.root.quit()

    def create_widgets(self):
        """Cria a interface principal com abas."""
        # Estilo para os widgets
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, relief="flat", background="#0078D7", foreground="white")
        style.map("TButton", background=[('active', '#005a9e')])
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

        # Configuração das cores para as tags na Treeview
        style.configure("suspeito.Treeview", background="#FFADAD", foreground="black") # Vermelho mais visível
        style.configure("desnecessario.Treeview", background="#FFD6A5", foreground="black") # Amarelo/Laranja mais visível
        style.configure("seguro.Treeview", background="#CAFFBF", foreground="black") # Verde para arquivos seguros

        # Notebook (gerenciador de abas)
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # Aba 1: Monitor de Sistema
        monitor_frame = ttk.Frame(notebook, padding="10")
        notebook.add(monitor_frame, text='Monitor em Tempo Real')
        self.create_monitor_tab(monitor_frame)

        # Aba 2: Limpeza e Análise
        scanner_frame = ttk.Frame(notebook, padding="10")
        notebook.add(scanner_frame, text='Limpeza e Análise do Sistema')
        self.create_scanner_tab(scanner_frame)

    # ABA 1: MONITOR DE SISTEMA
    def create_monitor_tab(self, parent):
        """Cria os widgets para a aba de monitoramento."""
        self.cpu_label = ttk.Label(parent, text="CPU Uso: --%", font=("Helvetica", 12))
        self.cpu_label.pack(pady=10)

        self.mem_label = ttk.Label(parent, text="Memória Usada: --% (-- GB / -- GB)", font=("Helvetica", 12))
        self.mem_label.pack(pady=10)
        
        self.disk_label = ttk.Label(parent, text="Disco Usado: --% (-- GB / -- GB)", font=("Helvetica", 12))
        self.disk_label.pack(pady=10)

        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=15)

        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=10)
        self.start_button = ttk.Button(button_frame, text="Iniciar Monitoramento", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Parar Monitoramento", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(parent, text="Status: Parado", foreground="red", font=("Helvetica", 10, 'italic'))
        self.status_label.pack(pady=20)
    
    # ABA 2: LIMPEZA E ANÁLISE
    def create_scanner_tab(self, parent):
        """Cria os widgets para a aba de limpeza."""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill='x', pady=5)

        self.scan_button = ttk.Button(control_frame, text="Iniciar Escaneamento", command=self.start_scan_thread)
        self.scan_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(control_frame, text="Apagar Arquivos Suspeitos", state=tk.DISABLED, command=self.delete_suspicious_files)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.report_button = ttk.Button(control_frame, text="Gerar Relatórios", state=tk.DISABLED, command=self.generate_reports)
        self.report_button.pack(side=tk.LEFT, padx=5)

        # Checkbox para o modo simulação
        simulation_check = ttk.Checkbutton(control_frame, text="Modo de Simulação (não apaga arquivos reais)", variable=self.simulation_mode)
        simulation_check.pack(side=tk.RIGHT, padx=15)

        self.scan_status_label = ttk.Label(parent, text="Pronto para escanear. O modo de simulação está ATIVO.", font=("Helvetica", 9))
        self.scan_status_label.pack(fill='x', pady=5)
        self.progress_bar = ttk.Progressbar(parent, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill='x', pady=5)

        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, columns=("path", "size", "reason"), show="headings")
        self.tree.heading("path", text="Caminho do Arquivo")
        self.tree.heading("size", text="Tamanho (MB)")
        self.tree.heading("reason", text="Motivo")
        self.tree.column("path", width=450)
        self.tree.column("size", width=100, anchor=tk.CENTER)
        self.tree.column("reason", width=200, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # LÓGICA DE MONITORAMENTO
    def start_monitoring(self):
        self.monitoring = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Monitorando...", foreground="green")
        self.log_action("--- Monitoramento em tempo real INICIADO ---")
        self.update_info()

    def stop_monitoring(self):
        self.monitoring = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Parado", foreground="red")
        self.log_action("--- Monitoramento em tempo real FINALIZADO ---")

    def update_info(self):
        if not self.monitoring: return
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        self.cpu_label.config(text=f"CPU Uso: {cpu}%")
        self.mem_label.config(text=f"Memória Usada: {mem.percent}% ({round(mem.used/1e9, 2)} GB / {round(mem.total/1e9, 2)} GB)")
        self.disk_label.config(text=f"Disco (C:) Usado: {disk.percent}% ({round(disk.used/1e9, 2)} GB / {round(disk.total/1e9, 2)} GB)")
        self.root.after(2000, self.update_info)

    # LÓGICA DE ESCANEAMENTO E LIMPEZA
    def start_scan_thread(self):
        self.scanning = True
        self.scan_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.report_button.config(state=tk.DISABLED)
        self.tree.delete(*self.tree.get_children())
        self.found_files.clear()
        self.log_action("--- Escaneamento do sistema INICIADO ---")
        scan_thread = threading.Thread(target=self.scan_filesystem, daemon=True)
        scan_thread.start()

    def scan_filesystem(self):
        paths_to_scan = [os.path.expanduser('~\\AppData\\Local\\Temp'), os.environ.get('WINDIR', 'C:\\Windows') + '\\Temp', os.path.expanduser('~\\Downloads')]
        suspicious_ext = ['.tmp', '.log', '.bak', '._mp', '.dmp', '.old', '.gid', '.err']
        large_file_size_mb = 500

        files_to_check = []
        for path in paths_to_scan:
            if os.path.exists(path):
                for root_dir, _, filenames in os.walk(path, topdown=True):
                    for filename in filenames:
                        files_to_check.append(os.path.join(root_dir, filename))

        total_files = len(files_to_check)
        self.progress_bar['maximum'] = total_files

        for i, filepath in enumerate(files_to_check):
            category = "inaccessible" # Categoria padrão
            try:
                file_size_mb = round(os.path.getsize(filepath) / (1024*1024), 2)
                _, ext = os.path.splitext(filepath)
                
                # Lógica de categorização
                if ext.lower() in suspicious_ext:
                    category = "suspeito"
                    reason = f"Extensão suspeita ({ext})"
                elif 'Temp' in filepath:
                    category = "desnecessario"
                    reason = "Arquivo temporário"
                elif 'Downloads' in filepath and file_size_mb > large_file_size_mb:
                    category = "desnecessario"
                    reason = f"Arquivo grande (>{large_file_size_mb}MB)"
                else:
                    category = "seguro"
                    reason = "Arquivo comum"

                # Adiciona à lista de resultados e à árvore da GUI
                file_info = (filepath, file_size_mb, reason, category)
                self.found_files.append(file_info)
                self.root.after(0, self.add_file_to_tree, file_info)
                    
            except (FileNotFoundError, PermissionError):
                # Se o arquivo não puder ser acessado, ele será marcado como inacessível
                # mas não será adicionado à lista de resultados.
                pass
            
            # Atualiza a GUI com a cor correspondente à categoria
            self.root.after(0, self.update_scan_status, i, total_files, filepath, category)
        
        self.root.after(0, self.scan_finished)

    def update_scan_status(self, current, total, filepath, category):
        self.progress_bar['value'] = current

        color_map = {
            "suspeito": "red",
            "desnecessario": "#E69138", # Laranja escuro
            "seguro": "green",
            "inaccessible": "gray"
        }
        color = color_map.get(category, "black") # Padrão para preto

        self.scan_status_label.config(
            text=f"Analisando [{current + 1}/{total}]: {os.path.basename(filepath)}",
            foreground=color
        )

    def add_file_to_tree(self, file_info):
        filepath, size, reason, category = file_info
        # Usa a categoria como tag para aplicar a cor na linha da árvore
        self.tree.insert("", tk.END, values=(filepath, size, reason), tags=(category,))
        
    def scan_finished(self):
        status_text = f"Escaneamento concluído. {len(self.found_files)} arquivos encontrados."
        if self.simulation_mode.get():
            status_text += " O modo de simulação está ATIVO."
        
        # Reseta a cor do texto de status para o padrão
        self.scan_status_label.config(text=status_text, foreground="black")
        self.progress_bar['value'] = 0
        self.scan_button.config(state=tk.NORMAL)
        
        if any(f[3] == 'suspeito' for f in self.found_files):
            self.delete_button.config(state=tk.NORMAL)
        if self.found_files:
            self.report_button.config(state=tk.NORMAL)
            
        self.log_action(f"--- Escaneamento FINALIZADO. {len(self.found_files)} arquivos encontrados. ---")

    def delete_suspicious_files(self):
        """Apaga APENAS os arquivos marcados como 'suspeitos' (vermelhos)."""
        items_to_delete = self.tree.get_children('')
        suspicious_items = [item for item in items_to_delete if 'suspeito' in self.tree.item(item, 'tags')]

        if not suspicious_items:
            messagebox.showinfo("Nenhum Arquivo Suspeito", "Nenhum arquivo categorizado como suspeito foi encontrado para apagar.")
            return

        is_simulation = self.simulation_mode.get()
        prefix = "[SIMULAÇÃO] " if is_simulation else ""
        
        msg = f"{prefix}Você tem certeza que deseja apagar os {len(suspicious_items)} arquivos suspeitos?"
        if not is_simulation:
            msg += "\n\nAVISO: O MODO DE SIMULAÇÃO ESTÁ DESATIVADO. OS ARQUIVOS SERÃO APAGADOS PERMANENTEMENTE DO SEU DISCO."
        
        if messagebox.askyesno("Confirmar Exclusão", msg):
            self.log_action(f"--- {prefix}Processo de exclusão INICIADO ---")
            deleted_count = 0
            for item in suspicious_items:
                filepath = self.tree.item(item, "values")[0]
                try:
                    if not is_simulation:
                        os.remove(filepath)
                    
                    self.tree.delete(item)
                    self.log_action(f"{prefix}SUCESSO: Arquivo apagado - {filepath}")
                    deleted_count += 1
                except Exception as e:
                    self.log_action(f"{prefix}FALHA: Não foi possível apagar {filepath}. Erro: {e}")
            
            messagebox.showinfo("Processo Concluído", f"{prefix}{deleted_count} de {len(suspicious_items)} arquivos foram processados para exclusão.")
            self.log_action(f"--- {prefix}Processo de exclusão FINALIZADO. {deleted_count} arquivos processados. ---")

    # LÓGICA DE RELATÓRIOS E LOGS
    def generate_reports(self):
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        csv_path = os.path.join(self.log_dir, f"relatorio_arquivos_{timestamp}.csv")
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Caminho Completo", "Tamanho (MB)", "Motivo", "Categoria"])
                writer.writerows(self.found_files)
            self.log_action(f"Relatório CSV gerado com sucesso em: {csv_path}")
            messagebox.showinfo("Sucesso", f"Relatório CSV salvo em:\n{csv_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar o relatório CSV.\nErro: {e}")
            self.log_action(f"FALHA ao gerar relatório CSV. Erro: {e}")

    def log_action(self, message):
        try:
            if self.action_log_file is None or self.action_log_file.closed:
                log_filename = f"log_de_atividades_{datetime.datetime.now().strftime('%d-%m-%Y')}.txt"
                self.action_log_file = open(os.path.join(self.log_dir, log_filename), "a", encoding="utf-8")
            
            current_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            self.action_log_file.write(f"[{current_time}] {message}\n")
            self.action_log_file.flush()
        except Exception as e:
            print(f"Erro ao escrever no log: {e}")

    def on_closing(self):
        if self.monitoring and messagebox.askokcancel("Sair", "O monitoramento está ativo. Deseja parar e sair?"):
            self.stop_monitoring()
        if self.action_log_file and not self.action_log_file.closed:
            self.log_action("--- Sessão da aplicação ENCERRADA ---")
            self.action_log_file.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()