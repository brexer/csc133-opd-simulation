import mesa

class PatientAgent(mesa.Agent):
    """An autonomous agent representing a patient in the OPD pipeline."""
    
    def __init__(self, unique_id, model, priority_level, spawn_time):
        super().__init__(unique_id, model)
        
        # evaluate agent: "Urgent", "Elderly/PWD/Pregnant", or "Regular"
        self.priority_level = priority_level
        self.spawn_time = spawn_time          # the exact minute they arrived
        
        # state machine (tracks location)
        self.current_location = "Entrance"
        self.is_waiting = True
        
        # metrics
        self.wait_time_registration = 0
        self.wait_time_triage = 0
        self.wait_time_consultation = 0
        
        self.service_time_registration = 0
        self.service_time_triage = 0
        self.service_time_consultation = 0

    def step(self):
        """
        1 tick in the simulation = 1 minute in real life.
        If agent is stuck waiting, their wait timer is incremented.
        """
        if self.is_waiting:
            if self.current_location == "Entrance":
                self.wait_time_registration += 1
            elif self.current_location == "Registration":
                self.wait_time_triage += 1
            elif self.current_location == "Triage":
                self.wait_time_consultation += 1
                
    def get_total_wait_time(self):
        """Calculates the absolute total friction the patient experienced (throughput)."""
        return self.wait_time_registration + self.wait_time_triage + self.wait_time_consultation