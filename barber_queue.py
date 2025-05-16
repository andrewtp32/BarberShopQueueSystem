import json
from datetime import datetime, timedelta
from statistics import mean


class Ticket:
    """Represents a single customer's ticket in the queue."""
    def __init__(self, number):
        self.number = number
        self.timeTaken = datetime.now()       # Time ticket was issued
        self.timeServed = None                # Filled in when served

    def markServed(self):
        """Mark this ticket as served now."""
        self.timeServed = datetime.now()

    def to_dict(self):
        """Serialize ticket to a dict for JSON saving."""
        return {
            "number": self.number,
            "timeTaken": self.timeTaken.isoformat(),
            "timeServed": self.timeServed.isoformat() if self.timeServed else None
        }

    @staticmethod
    def from_dict(data):
        """Reconstruct a Ticket from a saved JSON dict."""
        ticket = Ticket(data["number"])
        ticket.timeTaken = datetime.fromisoformat(data["timeTaken"])
        if data["timeServed"]:
            ticket.timeServed = datetime.fromisoformat(data["timeServed"])
        return ticket


class BarberQueue:
    """Manages the state of the queue system."""
    def __init__(self):
        self.queue = []                  # List of waiting Ticket objects
        self.currentTicket = None        # Currently served ticket
        self.lastTicketGiven = 0
        self.servedTickets = []          # List of completed Ticket objects

    def takeTicket(self):
        """Create and add a new ticket to the queue. Show estimated wait."""
        self.lastTicketGiven += 1
        ticket = Ticket(self.lastTicketGiven)
        self.queue.append(ticket)

        print(f"Ticket #{ticket.number} taken at {ticket.timeTaken.strftime('%H:%M:%S')}")

        people_ahead = len(self.queue) - 1
        print(f"There are {people_ahead} people ahead of you.")

        avg_wait = self.getAverageWaitTime()
        if avg_wait is not None and people_ahead > 0:
            estimated_wait = int(avg_wait * people_ahead)
            print(f"Estimated wait time: {estimated_wait} minutes.")
        elif people_ahead == 0:
            print("No wait — you’ll be served shortly!")
        else:
            print("Waiting time estimate is not available yet.")

    def serveNext(self):
        """Move the next person in the queue into service."""
        if self.queue:
            self.currentTicket = self.queue.pop(0)
            self.currentTicket.markServed()
            self.servedTickets.append(self.currentTicket)
            print(f"Now serving Ticket #{self.currentTicket.number} (served at {self.currentTicket.timeServed.strftime('%H:%M:%S')})")
        else:
            print("No one is waiting in the queue.")

    def getAverageWaitTime(self):
        """Calculate the average wait time (in minutes) from served tickets."""
        wait_times = []

        if self.currentTicket and self.currentTicket.timeServed:
            wait_time = (self.currentTicket.timeServed - self.currentTicket.timeTaken).total_seconds()
            wait_times.append(wait_time)

        for ticket in self.servedTickets:
            if ticket.timeServed:
                wait_time = (ticket.timeServed - ticket.timeTaken).total_seconds()
                wait_times.append(wait_time)

        if not wait_times:
            return None

        avg_seconds = mean(wait_times)
        return avg_seconds / 60  # Return minutes

    def showStatus(self):
        """Print the queue status and who's currently being served."""
        print("\n--- Queue Status ---")
        if self.currentTicket:
            print(f"Currently serving: Ticket #{self.currentTicket.number}")
        else:
            print("No one is currently being served.")
        print(f"Waiting in queue: {[ticket.number for ticket in self.queue]}")

    def saveToFile(self, filename="queue_data.json"):
        """Save the full queue state to a JSON file."""
        data = {
            "lastTicketGiven": self.lastTicketGiven,
            "queue": [t.to_dict() for t in self.queue],
            "servedTickets": [t.to_dict() for t in self.servedTickets],
            "currentTicket": self.currentTicket.to_dict() if self.currentTicket else None
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print("Queue state saved to file.")

    def loadFromFile(self, filename="queue_data.json"):
        """Load the queue state from a JSON file, resetting if it's a new day."""
        try:
            with open(filename, "r") as f:
                data = json.load(f)

            # Compare saved date to today's date
            last_saved_date = datetime.fromisoformat(
                data.get("lastResetDate", datetime.now().isoformat())
            ).date()
            today = datetime.now().date()

            if today > last_saved_date:
                print("New day detected. Resetting queue to start fresh.")
                return  # Leave self.* values in default state (empty queue)

            # Load saved data if it's still the same day
            self.lastTicketGiven = data["lastTicketGiven"]
            self.queue = [Ticket.from_dict(d) for d in data["queue"]]
            self.servedTickets = [Ticket.from_dict(d) for d in data["servedTickets"]]
            if data["currentTicket"]:
                self.currentTicket = Ticket.from_dict(data["currentTicket"])
            else:
                self.currentTicket = None
            print("Queue state loaded from file.")
        except FileNotFoundError:
            print("No saved queue found. Starting fresh.")



def run_queue_system():
    """Command-line interface to interact with the BarberQueue."""
    queue = BarberQueue()
    queue.loadFromFile()

    while True:
        print("\n--- Barber Queue System ---")
        print("1. Take a ticket")
        print("2. Serve next customer")
        print("3. Show queue status")
        print("4. Save queue")
        print("5. Load queue")
        print("6. Show average wait time")
        print("7. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            queue.takeTicket()
        elif choice == "2":
            queue.serveNext()
        elif choice == "3":
            queue.showStatus()
        elif choice == "4":
            queue.saveToFile()
        elif choice == "5":
            queue.loadFromFile()
        elif choice == "6":
            avg_wait = queue.getAverageWaitTime()
            if avg_wait is None:
                print("Not enough data to calculate average wait time yet.")
            else:
                print(f"Average wait time: {int(avg_wait)} minutes.")
        elif choice == "7":
            queue.saveToFile()
            print("Exiting. Queue state saved.")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    run_queue_system()
