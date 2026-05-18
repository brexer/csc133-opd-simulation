import mesa
import random
from agents import PatientAgent
from servers import ClinicNode

class ClinicModel(mesa.Model):
    """The main digital environment for the OPD Simulation."""
    
    def __init__(self, use_appointments=False, use_dynamic_priority=True, num_doctors=3):
        super().__init__()

        self.use_appointments = use_appointments
        self.use_dynamic_priority = use_dynamic_priority
        
        # If appointments are on, 20 patients are randomly scheduled within the 600-minute day.
        if self.use_appointments:
            self.appointment_schedule = sorted(random.sample(range(0, 600), 20))
        else:
            self.appointment_schedule = []

        self.registration = ClinicNode("Registration", capacity=2) 
        self.triage = ClinicNode("Triage", capacity=1)             
        self.consultation = ClinicNode("Consultation", capacity=num_doctors) 
        
        self.datacollector = mesa.DataCollector(
            agent_reporters={
                "Priority_Tag": "priority_level",
                "Has_Appointment": "has_appointment",
                "Arrival_Time": "spawn_time",
                "Wait_Registration": "wait_time_registration",
                "Wait_Triage": "wait_time_triage",
                "Wait_Consultation": "wait_time_consultation"
            },
            model_reporters={
                "Reg_Line": lambda m: len(m.registration.queue),
                "Triage_Line": lambda m: len(m.triage.queue),
                "Doctor_Line": lambda m: len(m.consultation.queue)
            }
        )

    def step(self):
        """
        Advances the simulation by exactly one minute.
        This function is called over and over in a loop until the hospital closes.
        """
        # There is a 20% chance every tick that a patient comes in
        if random.random() < 0.20:
            self.spawn_patient(has_appointment=False)

        # Checks if the current minute is in today's appointment book
        if self.use_appointments and self.steps in self.appointment_schedule:
            self.spawn_patient(has_appointment=True)
            
        self.agents.shuffle_do("step")

        self.registration.process_tick()
        self.triage.process_tick()
        self.consultation.process_tick()

        self.datacollector.collect(self)

    def spawn_patient(self, has_appointment):
        """Generates a new patient with a mathematically weighted priority tag."""
        # Monte Carlo Attribute Assignment 15% for Urgent, 25% for Elderly/PWD/Pregnant, 60% for the rest.
        roll = random.random()
        if roll < 0.15:
            priority = "Urgent"
        elif roll < 0.40:
            priority = "Vulnerable"
        else:
            priority = "Regular"
            
        new_agent = PatientAgent(self, priority, self.steps, has_appointment)
        new_agent.advance_pipeline()