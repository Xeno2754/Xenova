from brain.ai import chat

history = []

while True:
    user = input("You: ")

    if user.lower() == "exit":
        break

    reply, history = chat(user, history)

    print("\nXENOVA:", reply)
    print()