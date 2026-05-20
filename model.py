import mesa
import random
from agents import PatientAgent
from servers import ClinicNode

# CONSTANTS
ARRIVAL_PROB = 0.20           # 20% chance of walk-in per minute (~1 per 5 min)
APPOINTMENT_COUNT = 20        # Scheduled patients per day (Scenarios 2 & 5)
TICKS_PER_DAY = 600           # 10-hour clinic shift

class ClinicModel(mesa.Model):
    """The main digital environment for the OPD Simulation.
    
    Parameters
    ----------
    use_appointments : bool
        If True, APPOINTMENT_COUNT patients are pre-scheduled at fixed times.
    use_dynamic_priority : bool
        If True, ClinicNode queues use the Priority Routing algorithm.
    num_doctors : int
        Capacity of the Consultation node (Scenario 4 adds +1).
    seed : int, optional
        RNG seed for reproducibility across replications.
    """
    
    def __init__(self, use_appointments=False, use_dynamic_priority=False, num_doctors=3, seed=None):
        super().__init__(seed=seed)
 
        self.use_appointments = use_appointments
        self.use_dynamic_priority = use_dynamic_priority

        self.current_tick = 0
        
        # If appointments are on, 20 patients are randomly scheduled within the 600-minute day.
        if self.use_appointments:
            rng = random.Random(seed)
            self.appointment_schedule = sorted(
                rng.sample(range(0, TICKS_PER_DAY), APPOINTMENT_COUNT)
            )
        else:
            self.appointment_schedule = []

        self.registration = ClinicNode("Registration", capacity=2)
        self.triage = ClinicNode("Triage", capacity=1)
        self.consultation = ClinicNode("Consultation", capacity=num_doctors)
        
        self.datacollector = mesa.DataCollector(
            agent_reporters={
                "Priority_Tag":          "priority_level",
                "Has_Appointment":       "has_appointment",
                "Arrival_Time":          "spawn_time",
                "Wait_Registration":     "wait_time_registration",
                "Wait_Triage":           "wait_time_triage",
                "Wait_Consultation":     "wait_time_consultation",
                "Service_Registration":  "service_time_registration",
                "Service_Triage":        "service_time_triage",
                "Service_Consultation":  "service_time_consultation",
                "Total_Wait":            lambda a: a.get_total_wait_time(),
                "Location":              "current_location",
            },
            model_reporters={
                "Reg_Line":    lambda m: m.registration.queue_length(),
                "Triage_Line": lambda m: m.triage.queue_length(),
                "Doctor_Line": lambda m: m.consultation.queue_length(),
                "Reg_Active":  lambda m: m.registration.active_count(),
                "Triage_Active": lambda m: m.triage.active_count(),
                "Doctor_Active": lambda m: m.consultation.active_count(),
            }
        )

    def step(self):
        """
        Advances the simulation by exactly one minute.
 
        Order of operations per tick:
          1. Increment our own tick counter FIRST (avoids off-by-one with Mesa).
          2. Spawn walk-in patient (stochastic).
          3. Spawn appointment patient if scheduled for this tick.
          4. Tick all existing patient agents (wait timer increment).
          5. Process all clinic nodes (service countdowns, queue pulls).
          6. Collect data.
        """
        self.current_tick += 1
 
        if random.random() < ARRIVAL_PROB:
            self.spawn_patient(has_appointment=False)
 
        if self.use_appointments and self.current_tick in self.appointment_schedule:
            self.spawn_patient(has_appointment=True)
 
        self.agents.shuffle_do("step")
 
        self.registration.process_tick()
        self.triage.process_tick()
        self.consultation.process_tick()
 
        self.datacollector.collect(self)

    def spawn_patient(self, has_appointment: bool):
        """
        Creates a new PatientAgent with a Monte Carlo priority assignment
        and immediately enqueues them at Registration.
 
        Priority weights (Mandac-Crisostomo 2025 baseline):
            Urgent     15%
            Vulnerable 25%
            Regular    60%
        """
        roll = random.random()
        if roll < 0.15:
            priority = "Urgent"
        elif roll < 0.40:
            priority = "Vulnerable"
        else:
            priority = "Regular"
 
        agent = PatientAgent(
            model=self,
            priority_level=priority,
            spawn_time=self.current_tick,
            has_appointment=has_appointment,
        )

        agent.advance_pipeline()