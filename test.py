from pathlib import Path
import os

root= Path(__file__).parent.parent

print(root)
print(os.listdir(os.path.join(root,'chats')))

