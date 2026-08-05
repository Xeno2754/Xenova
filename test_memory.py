from memory.database import init_db
from memory.manager import remember, recall

init_db()

remember("college","TCET")

print(recall("college"))