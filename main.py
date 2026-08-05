import time

start = time.time()
print("Starting...")

t = time.time()
from assistant.assistant import run
print(f"assistant import: {time.time()-t:.2f}s")

t = time.time()
from memory.database import init_db
print(f"database import: {time.time()-t:.2f}s")

t = time.time()
init_db()
print(f"database init: {time.time()-t:.2f}s")

print(f"Total startup before run(): {time.time()-start:.2f}s")

if __name__ == "__main__":
    run()