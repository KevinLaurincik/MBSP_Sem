import random
import matplotlib.pyplot as plt

# Parametre simulácie
NUM_DOCTORS = 4
SHIFT_HOURS = 6
ACUTE_CASES_PER_DAY = (6, 10)
TREATMENT_TIME_NORMAL = (20, 30)
TREATMENT_TIME_COMPLEX = (40, 60)
COMPLEX_CASE_PROB = 0.2
APPOINTMENT_VARIATION = (-10, 10)
END_TIME = SHIFT_HOURS * 60  # Čas v minútach
REPLICATIONS = 700  # Počet replikácií simulácie

# Trieda pacienta
class Patient:
    def __init__(self, arrival_time, urgent=False):
        self.arrival_time = arrival_time
        self.urgent = urgent
        self.treatment_time = random.randint(*TREATMENT_TIME_COMPLEX) if random.random() < COMPLEX_CASE_PROB else random.randint(*TREATMENT_TIME_NORMAL)

# Funkcia simulácie
def simulate_clinic():
    event_list = []
    doctor_busy_time = {i: 0 for i in range(NUM_DOCTORS)}
    doctors_available = list(range(NUM_DOCTORS))
    waiting_queue = []
    queue_size_over_time = []
    time_stamps = []
    total_waiting_time = 0
    treated_patients = 0

    # Generovanie pacientov
    appointment_times = [random.randint(0, END_TIME) + random.randint(*APPOINTMENT_VARIATION) for _ in range(30)]
    acute_cases = [random.randint(0, END_TIME) for _ in range(random.randint(*ACUTE_CASES_PER_DAY))]

    for time in appointment_times:
        event_list.append(("arrival", time, Patient(time)))

    for time in acute_cases:
        event_list.append(("arrival", time, Patient(time, urgent=True)))

    # Zoradenie udalostí podľa času
    event_list.sort(key=lambda x: x[1])

    current_time = 0
    while event_list:
        event_type, event_time, patient = event_list.pop(0)
        current_time = event_time

        time_stamps.append(current_time)
        queue_size_over_time.append(len(waiting_queue))

        if event_type == "arrival":
            if doctors_available:
                doctor = doctors_available.pop(0)
                doctor_busy_time[doctor] += patient.treatment_time
                event_list.append(("release_doctor", current_time + patient.treatment_time, doctor))
                event_list.sort(key=lambda x: x[1])
            else:
                waiting_queue.append(patient)

        elif event_type == "release_doctor":
            doctor = patient
            doctors_available.append(doctor)
            if waiting_queue:
                p = waiting_queue.pop(0)
                waiting_time = current_time - p.arrival_time
                total_waiting_time += waiting_time
                treated_patients += 1
                doctor_busy_time[doctor] += p.treatment_time
                doctors_available.remove(doctor)
                event_list.append(("release_doctor", current_time + p.treatment_time, doctor))
                event_list.sort(key=lambda x: x[1])

        time_stamps.append(current_time)
        queue_size_over_time.append(len(waiting_queue))

    avg_waiting_time = total_waiting_time / max(1, treated_patients)
    doctor_utilization = {doc: (busy_time / END_TIME) * 100 for doc, busy_time in doctor_busy_time.items()}

    return avg_waiting_time, doctor_utilization, time_stamps, queue_size_over_time

# Spustenie replikácií simulácie
total_waiting_time = []
doctor_utilization_aggregated = {i: [] for i in range(NUM_DOCTORS)}

for _ in range(REPLICATIONS):
    avg_waiting_time, doctor_utilization, time_stamps, queue_sizes = simulate_clinic()
    total_waiting_time.append(avg_waiting_time)
    for doc, utilization in doctor_utilization.items():
        doctor_utilization_aggregated[doc].append(utilization)

average_waiting_time = sum(total_waiting_time) / len(total_waiting_time)
doctor_average_utilization = {doc: sum(utilizations) / len(utilizations) for doc, utilizations in doctor_utilization_aggregated.items()}

# Vykreslenie grafu
plt.figure(figsize=(10, 5))
plt.plot(time_stamps, queue_sizes, marker='o', linestyle='-')
plt.xlabel("Čas (min)")
plt.ylabel("Počet pacientov v rade")
plt.title("Závislosť počtu pacientov v rade od času")
plt.grid()
plt.show()

print(f"Priemerný čas čakania po {REPLICATIONS} replikáciách: {average_waiting_time:.2f} minút")
print("Vyťaženosť doktorov:")
for doc, utilization in doctor_average_utilization.items():
    print(f"Doktor {doc + 1}: {utilization:.2f}%")