import random
import numpy as np

def _sample_registration():
    return max(1, int(round(random.gauss(5, 1.5))))
 
def _sample_triage():
    return max(1, int(round(np.random.gamma(shape=3, scale=1.5))))
 
def _sample_consultation():
    return max(1, int(round(np.random.lognormal(mean=2.8, sigma=0.55))))

class ClinicNode:
    """
    Represents a specific station in the OPD (e.g., Registration, Triage, Consultation).
    This handles the capacity limits and enforces the Priority Routing Algorithm.
    """
    
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity      # parallel servers (clerks / nurses / doctors)
        self.queue = []               # waiting agents, sorted by priority
        self.active_agents = []       # agents currently being served
        
    def receive_patient(self, agent, use_dynamic_priority=True):
        """
        The Dynamic Priority Sorting Algorithm.
        This triggers the moment an agent arrives at this station.
        """
        agent.is_waiting = True
        # If a doctor is free, the patient bypasses the queue entirely.
        if len(self.active_agents) < self.capacity:
            self.start_service(agent)
            return
        
        if not use_dynamic_priority:
            self.queue.append(agent)
            return
        
        weight = agent.get_priority_weight()
        insert_pos = 0
        for i, queued in enumerate(self.queue):
            if queued.get_priority_weight() <= weight:
                insert_pos = i + 1
            else:
                break
        self.queue.insert(insert_pos, agent)

    def start_service(self, agent):
        """
        Pulls the agent out of the waiting state and into active service.
        Sets service duration based on literature-grounded distributions.
        """
        self.active_agents.append(agent)
        agent.is_waiting = False
 
        if self.name == "Registration":
            duration = _sample_registration()
            agent.service_time_registration = duration
            agent.current_location = "In_Registration"
 
        elif self.name == "Triage":
            duration = _sample_triage()
            agent.service_time_triage = duration
            agent.current_location = "In_Triage"
 
        elif self.name == "Consultation":
            duration = _sample_consultation()
            agent.service_time_consultation = duration
            agent.current_location = "In_Consultation"
 
        agent.current_service_time_left = duration

    def process_tick(self):
        """
        Decrements service timers; discharges finished patients;
        pulls next patient from the queue if a server opens up.
        """
        finished = []
        for agent in self.active_agents:
            agent.current_service_time_left -= 1
            if agent.current_service_time_left <= 0:
                finished.append(agent)
 
        for agent in finished:
            self.active_agents.remove(agent)
            agent.advance_pipeline()   # moves to next node or Discharged
 
        # Fill any newly freed servers from the queue
        while self.queue and len(self.active_agents) < self.capacity:
            next_patient = self.queue.pop(0)
            self.start_service(next_patient)

    def queue_length(self):
        return len(self.queue)
 
    def active_count(self):
        return len(self.active_agents)