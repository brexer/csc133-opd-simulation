import mesa
import random
from agents import PatientAgent
from servers import ClinicNode

class ClinicModel(mesa.Model):
    """The main digital environment for the OPD Simulation."""
    
    def __init__(self):
        super().__init__()

        self.registration = ClinicNode("Registration", capacity=2) # 2 Clerks
        self.triage = ClinicNode("Triage", capacity=1)             # 1 Triage Nurse
        self.consultation = ClinicNode("Consultation", capacity=3) # 3 Doctors
                
        self.datacollector = mesa.DataCollector(
            agent_reporters={
                "Priority_Tag": "priority_level",
                "Arrival_Time": "spawn_time",
                "Wait_Registration": "wait_time_registration",
                "Wait_Triage": "wait_time_triage",
                "Wait_Consultation": "wait_time_consultation"
            }
        )

    def step(self):
        """
        Advances the simulation by exactly one minute.
        This function is called over and over in a loop until the hospital closes.
        """
        # There is a 20% chance every tick that a patient comes in
        if random.random() < 0.20:
            self.spawn_patient()
            
        self.agents.shuffle_do("step")

        self.registration.process_tick()
        self.triage.process_tick()
        self.consultation.process_tick()

        self.datacollector.collect(self)

    def spawn_patient(self):
        """Generates a new patient with a mathematically weighted priority tag."""
        # Monte Carlo Attribute Assignment 15% for Urgent, 25% for Elderly/PWD/Pregnant, 60% for the rest.
        roll = random.random()
        if roll < 0.15:
            priority = "Urgent"
        elif roll < 0.40:
            priority = "Vulnerable"
        else:
            priority = "Regular"
            
        new_agent = PatientAgent(self, priority, self.steps)
        new_agent.advance_pipeline()