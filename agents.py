import mesa

class PatientAgent(mesa.Agent):
    """An autonomous agent representing a patient in the OPD pipeline."""
    
    def __init__(self, model, priority_level, spawn_time, has_appointment=False):
        super().__init__(model)
        
        # evaluate agent: "Urgent", "Elderly/PWD/Pregnant (Vulnerable)", or "Regular"
        self.priority_level = priority_level
        self.spawn_time = spawn_time          # the exact minute they arrived
        self.has_appointment = has_appointment
        
        # state machine (tracks location)
        self.current_location = "Entrance"
        self.is_waiting = False
        
        # metrics
        self.wait_time_registration = 0
        self.wait_time_triage = 0
        self.wait_time_consultation = 0
        
        self.service_time_registration = 0
        self.service_time_triage = 0
        self.service_time_consultation = 0

        self.current_service_time_left = 0

    def step(self):
        """
        1 tick in the simulation = 1 minute in real life.
        If agent is stuck waiting, their wait timer is incremented.
        """
        if not self.is_waiting:
            return
 
        if self.current_location == "Waiting_Registration":
            self.wait_time_registration += 1
        elif self.current_location == "Waiting_Triage":
            self.wait_time_triage += 1
        elif self.current_location == "Waiting_Consultation":
            self.wait_time_consultation += 1
                
    def get_total_wait_time(self):
        """Total queue time across all nodes."""
        return (
            self.wait_time_registration
            + self.wait_time_triage
            + self.wait_time_consultation
        )
    
    def advance_pipeline(self):
        """Moves the patient to the next bottleneck after finishing a service."""

        priority_mode = self.model.use_dynamic_priority

        if self.current_location == "Entrance":
            self.current_location = "Waiting_Registration"
            self.model.registration.receive_patient(self, priority_mode)
 
        elif self.current_location == "In_Registration":
            self.current_location = "Waiting_Triage"
            self.model.triage.receive_patient(self, priority_mode)
 
        elif self.current_location == "In_Triage":
            self.current_location = "Waiting_Consultation"
            self.model.consultation.receive_patient(self, priority_mode)
 
        elif self.current_location == "In_Consultation":
            self.current_location = "Discharged"
            self.model.agents.remove(self)

    def get_total_service_time(self):
        """Total time actively being served across all nodes."""
        return (
            self.service_time_registration
            + self.service_time_triage
            + self.service_time_consultation
        )
 
    def get_total_time_in_system(self):
        """
        Sojourn time = wait + service across all nodes.
        Valid only after discharge; returns None otherwise.
        """
        if self.current_location != "Discharged":
            return None
        return self.get_total_wait_time() + self.get_total_service_time()
 
    def get_priority_weight(self):
        """
        Numeric sort key for the Dynamic Priority Routing algorithm.
        Lower = higher priority (consistent with ESI and RA 9994 / RA 10754).
        Returns a tuple (tier, appointment_bonus) for stable sub-sorting.
        """
        base = {"Urgent": 0, "Vulnerable": 1, "Regular": 2}.get(self.priority_level, 2)
        appt_bonus = 0 if self.has_appointment else 1
        return (base, appt_bonus)