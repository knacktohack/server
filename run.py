from multiprocessing import Process
from core.azure.message_queue import loopForChunkingQueue
from app import startApp
if __name__ == '__main__':
    processes = []
    
    try:
        p = Process(target=loopForChunkingQueue)
        p.start()
        
        processes.append(p)
        
        p = Process(target=startApp)
        p.start()
        
        processes.append(p)
        
    except KeyboardInterrupt:
        for p in processes:
            p.terminate()
            p.join()
        print("Processes terminated.")
        