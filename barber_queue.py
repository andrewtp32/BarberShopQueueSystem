import json
from datetime import datetime


class Ticket:
    def __init__(self, number, timeTaken=None, timeServed=None):
        self.number = number
        self.timeTaken = timeTaken or datetime.now()
        self.timeServed = timeServed

    def markServed(self):
        self.timeServed = datetime.now()

    def toDict(self):
        return {
            "number": self.number,
            "timeTaken": self.timeTaken.isoformat(),
            "timeServed": self.timeServed.isoformat() if self.timeServed else None
        }

    @classmethod
    def fromDict(cls, data):
        timeTaken = datetime.fromisoformat(data["timeTaken"])
        timeServed = datetime.fromisoformat(data["timeServed"]) if data["timeServed"] else None
        return cls(data["number"], timeTaken, timeServed)


class BarberQueue:
    def __init__(self):
        self.currentTicket = None
        self.lastTicketGiven = 0
        self.queue = []

    def takeTicket(self):
        self.lastTicketGiven += 1
        ticket = Ticket(self.lastTicketGiven)
        self.queue.append(ticket)

        position = len(self.queue)
        print(f"\nYour ticket number is {ticket.number}.")
        print(f"There are {position - 1} people ahead of you.")
        print(f"Time taken: {ticket.timeTaken.strftime('%I:%M:%S %p')}\n")

    def serveNext(self):
        if self.queue:
            self.currentTicket = self.queue.pop(0)
            self.currentTicket.markServed()

            print(f"\nNow serving ticket #{self.currentTicket.number}.")
            print(f"Time taken: {self.currentTicket.timeTaken.strftime('%I:%M:%S %p')}")
            print(f"Time served: {self.currentTicket.timeServed.strftime('%I:%M:%S %p')}\n")
        else:
            self.currentTicket = None
            print("\nNo one is currently in the queue.\n")

    def viewCurrent(self):
        if self.currentTicket:
            print(f"\nCurrently serving ticket #{self.currentTicket.number}")
            print(f"Time taken: {self.currentTicket.timeTaken.strftime('%I:%M:%S %p')}")
            print(f"Time served: {self.currentTicket.timeServed.strftime('%I:%M:%S %p')}\n")
        else:
            print("\nNo ticket is currently being served.\n")

    def viewStatus(self):
        print("\nQueue Status:")
        if self.currentTicket:
            print(f"- Currently serving: {self.currentTicket.number}")
        else:
            print("- Currently serving: None")

        print(f"- People waiting: {len(self.queue)}")

        if self.queue:
            print("- Tickets in queue:")
            for t in self.queue:
                print(f"  Ticket #{t.number} (taken at {t.timeTaken.strftime('%I:%M:%S %p')})")
        print()

    def saveToFile(self, filename="queue_data.json"):
        data = {
            "lastTicketGiven": self.lastTicketGiven,
            "queue": [t.toDict() for t in self.queue],
            "currentTicket": self.currentTicket.toDict() if self.currentTicket else None
        }
        with open(filename, "w") as f:
            json.dump(data, f)
        print(f"\nQueue state saved to {filename}\n")

    def loadFromFile(self, filename="queue_data.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            self.lastTicketGiven = data["lastTicketGiven"]
            self.queue = [Ticket.fromDict(td) for td in data["queue"]]
            self.currentTicket = Ticket.fromDict(data["currentTicket"]) if data["currentTicket"] else None
            print(f"\nQueue state loaded from {filename}\n")
        except FileNotFoundError:
            print(f"\nNo existing data file found — starting fresh.\n")


def mainMenu():
    queue = BarberQueue()
    queue.loadFromFile()

    while True:
        print("=== Barber Queue System ===")
        print("1. Take a Ticket")
        print("2. View Current Ticket Being Served")
        print("3. Serve Next Customer")
        print("4. View Queue Status")
        print("5. Save Queue to File")
        print("6. Exit")
        choice = input("Select an option (1-6): ")

        if choice == "1":
            queue.takeTicket()
        elif choice == "2":
            queue.viewCurrent()
        elif choice == "3":
            queue.serveNext()
        elif choice == "4":
            queue.viewStatus()
        elif choice == "5":
            queue.saveToFile()
        elif choice == "6":
            queue.saveToFile()
            print("\nGoodbye!\n")
            break
        else:
            print("\nInvalid option. Please try again.\n")


if __name__ == "__main__":
    mainMenu()
