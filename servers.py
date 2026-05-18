import random

class ClinicNode:
    """
    Represents a specific station in the OPD (e.g., Registration, Triage, Consultation).
    This handles the capacity limits and enforces the Priority Routing Algorithm.
    """
    
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity  # Number of available clerks/doctors
        self.queue = []           # The dynamic waiting array
        self.active_agents = []   # Agents currently receiving service
        
    def receive_patient(self, agent, use_dynamic_priority=True):
        """
        The Dynamic Priority Sorting Algorithm.
        This triggers the moment an agent arrives at this station.
        """
        # If a doctor is free, the patient bypasses the queue entirely.
        if len(self.active_agents) < self.capacity:
            self.start_service(agent)
            return
        
        if not use_dynamic_priority:
            self.queue.append(agent)
            agent.is_waiting = True
            return

        # If the station is full, evaluate the agent's priority level and sort them.
        if agent.priority_level == "Urgent":
            # Finds the last Urgent patient and inserts right behind them (Index 0 tier)
            insert_pos = sum(1 for p in self.queue if p.priority_level == "Urgent")
            self.queue.insert(insert_pos, agent)
            
        elif agent.priority_level == "Vulnerable":
            # Finds the end of the Urgent and Vulnerable blocks, inserts behind them (Index 1 tier)
            if agent.has_appointment:
                insert_pos = sum(1 for p in self.queue if p.priority_level == "Urgent" or 
                                (p.priority_level == "Vulnerable" and p.has_appointment))   # Vulnerable patients with appointment bypasses Vulnerable walk-ins
            else:
                insert_pos = sum(1 for p in self.queue if p.priority_level in ["Urgent", "Vulnerable"])
            self.queue.insert(insert_pos, agent)
            
        else:
            # Regular walk-in: Standard First-In-First-Out (FIFO) at the back of the line
            # Regular patients with appointment bypasses Regular walk-ins
            if agent.has_appointment:
                insert_pos = sum(1 for p in self.queue if p.priority_level in ["Urgent", "Vulnerable"] or 
                                (p.priority_level == "Regular" and p.has_appointment))
                self.queue.insert(insert_pos, agent)
            else:
                self.queue.append(agent)
            
        agent.is_waiting = True

    def start_service(self, agent):
        """Moves the agent out of the queue and into the active room."""
        self.active_agents.append(agent)
        agent.is_waiting = False
        
        # Set service times for each station
        if self.name == "Registration":
            agent.current_service_time_left = random.randint(2, 5)   # Takes 2-5 minutes
        elif self.name == "Triage":
            agent.current_service_time_left = random.randint(3, 8)   # Takes 3-8 minutes
        elif self.name == "Consultation":
            agent.current_service_time_left = random.randint(10, 20) # Takes 10-20 minutes

    def process_tick(self):
        """Runs every minute to process active patients and pull from the queue."""
        # Patients currently with a doctor or clerk
        finished_agents = []
        for agent in self.active_agents:
            agent.current_service_time_left -= 1
            if agent.current_service_time_left <= 0:
                finished_agents.append(agent)
                
        # Move patients to the next station
        for agent in finished_agents:
            self.active_agents.remove(agent)
            agent.advance_pipeline()

        # Pull the next high-priority patients to move to the next stations
        while len(self.active_agents) < self.capacity and len(self.queue) > 0:
            next_patient = self.queue.pop(0)
            self.start_service(next_patient)