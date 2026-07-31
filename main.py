from memory.database import create_tables
from memory.memory import save_memory, get_memory

create_tables()

save_memory("name", "Ainesh")

print(get_memory("name"))