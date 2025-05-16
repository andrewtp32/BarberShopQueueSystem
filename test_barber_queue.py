import unittest
import os
import json
from datetime import datetime, timedelta
from barber_queue import BarberQueue, Ticket

class TestBarberQueue(unittest.TestCase):

    def setUp(self):
        """Create a fresh queue before each test."""
        self.queue = BarberQueue()

    def test_take_ticket(self):
        self.queue.takeTicket()
        self.assertEqual(len(self.queue.queue), 1)
        self.assertEqual(self.queue.queue[0].number, 1)

    def test_serve_ticket(self):
        self.queue.takeTicket()
        self.queue.serveNext()
        self.assertEqual(len(self.queue.queue), 0)
        self.assertEqual(len(self.queue.servedTickets), 1)
        self.assertIsNotNone(self.queue.servedTickets[0].timeServed)

    def test_average_wait_time(self):
        # Simulate a served ticket with a 2-minute wait
        ticket = Ticket(1)
        ticket.timeTaken = datetime.now() - timedelta(minutes=2)
        ticket.timeServed = datetime.now()
        self.queue.currentTicket = ticket
        self.queue.servedTickets.append(ticket)

        avg = self.queue.getAverageWaitTime()
        self.assertIsNotNone(avg)
        self.assertAlmostEqual(avg, 2, delta=0.1)

    def test_save_and_load_queue(self):
        # Create and serve a ticket
        self.queue.takeTicket()
        self.queue.serveNext()
        self.queue.saveToFile("test_queue.json")

        # Load a new queue from saved data
        new_queue = BarberQueue()
        new_queue.loadFromFile("test_queue.json")

        self.assertEqual(new_queue.lastTicketGiven, 1)
        self.assertEqual(len(new_queue.servedTickets), 1)
        os.remove("test_queue.json")  # Clean up

    def test_reset_on_new_day(self):
        """Ensure the queue resets if the saved file is from yesterday."""
        self.queue.takeTicket()
        self.queue.saveToFile("test_reset.json")

        # Modify the saved file's lastResetDate to simulate yesterday
        with open("test_reset.json", "r+") as f:
            data = json.load(f)
            data["lastResetDate"] = (datetime.now() - timedelta(days=1)).date().isoformat()
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

        new_queue = BarberQueue()
        new_queue.loadFromFile("test_reset.json")

        # Should reset to empty queue
        self.assertEqual(new_queue.lastTicketGiven, 0)
        self.assertEqual(len(new_queue.queue), 0)
        os.remove("test_reset.json")

if __name__ == '__main__':
    unittest.main()
