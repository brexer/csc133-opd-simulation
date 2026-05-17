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
        
    def receive_patient(self, agent):
        """
        The Dynamic Priority Sorting Algorithm.
        This triggers the moment an agent arrives at this station.
        """
        # If a doctor is free, the patient bypasses the queue entirely.
        if len(self.active_agents) < self.capacity:
            self.start_service(agent)
            return

        # If the station is full, evaluate the agent's priority level and sort them.
        if agent.priority_level == "Urgent":
            # Finds the last Urgent patient and inserts right behind them (Index 0 tier)
            insert_pos = sum(1 for p in self.queue if p.priority_level == "Urgent")
            self.queue.insert(insert_pos, agent)
            
        elif agent.priority_level == "Vulnerable":
            # Finds the end of the Urgent and Vulnerable blocks, inserts behind them (Index 1 tier)
            insert_pos = sum(1 for p in self.queue if p.priority_level in ["Urgent", "Vulnerable"])
            self.queue.insert(insert_pos, agent)
            
        else:
            # Regular walk-in: Standard First-In-First-Out (FIFO) at the back of the line
            self.queue.append(agent)
            
        agent.is_waiting = True

    def start_service(self, agent):
        """Moves the agent out of the queue and into the consultation room."""
        self.active_agents.append(agent)
        agent.is_waiting = False

    def process_tick(self):
        """
        Runs every minute to check if doctors are finished.
        If a doctor is free, it strictly pulls from Index 0 of the queue.
        """
        
        while len(self.active_agents) < self.capacity and len(self.queue) > 0:
            next_patient = self.queue.pop(0)
            self.start_service(next_patient)