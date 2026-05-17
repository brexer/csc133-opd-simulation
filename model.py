import mesa
import random
from agents import PatientAgent

class ClinicModel(mesa.Model):
    """The main digital environment for the OPD Simulation."""
    
    def __init__(self):
        super().__init__()
        
        # 1 tick = 1 minute in real time.
        self.schedule = mesa.time.BaseScheduler(self)
        self.current_id = 0
                
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
        # There is a 20% chance every tick that a patient comes in. This is based on Mandac-Crisostomo baseline data
        if random.random() < 0.20:
            self.spawn_patient()
            
        self.schedule.step()
        self.datacollector.collect(self)

    def spawn_patient(self):
        """Generates a new patient with a mathematically weighted priority tag."""
        self.current_id += 1
        
        # Monte Carlo Attribute Assignment 15% for Urgent, 25% for Elderly/PWD/Pregnant, 60% for the rest.
        roll = random.random()
        if roll < 0.15:
            priority = "Urgent"
        elif roll < 0.40:
            priority = "Elderly/PWD/Pregnant"
        else:
            priority = "Regular"
            
        new_patient = PatientAgent(self.current_id, self, priority, self.schedule.time)
        self.schedule.add(new_patient)