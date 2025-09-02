import queue
import threading

from app.utils.file_processor import process_csv_file

class QueueManager:
    def __init__(self, workers_count):
        self.queue = queue.Queue()
        self.workers_count = workers_count
        self.workers = []

    def add(self, task):
        # Apenas adiciona a tarefa na fila.
        self.queue.put(task)
        print(f"Tarefa '{task}' adicionada na fila.")

    def worker(self):
        while True:
            task = self.queue.get()
            if task is None:
                print(f"[{threading.current_thread().name}] Sinal de parada recebido. Encerrando.")
                break         
            print(f"[{threading.current_thread().name}] Processando a tarefa: {task}")
            
            process_csv_file(task)
    
            print(f"[{threading.current_thread().name}] Tarefa '{task}' concluida.")
            
            self.queue.task_done()
    
    def start(self):
        print(f"Iniciando {self.workers_count} workers...")
        for i in range(self.workers_count):
            t = threading.Thread(target=self.worker, name=f"Worker-{i+1}")
            t.daemon = True
            t.start()
            self.workers.append(t)

    def wait_for_completion(self):
        self.queue.join()
        
    def stop(self):
        for _ in range(self.workers_count):
            self.queue.put(None)
        
        for worker in self.workers:
            worker.join()
        
        print("Todos os workers foram encerrados.")

# # --- Exemplo de uso ---
# manager = QueueManager(workers_count=3)

# # Adiciona 50 tarefas na fila.
# for i in range(50):
#     manager.add(i)

# # Inicia o processamento com os workers.
# manager.start()

# # Espera até que todas as tarefas sejam processadas.
# manager.wait_for_completion()

# # Após todas as tarefas, envia o sinal para os workers pararem.
# manager.stop()

# print("Processamento de todas as tarefas concluído. Fim do programa.")