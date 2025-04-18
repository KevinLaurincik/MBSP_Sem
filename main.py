import numpy as np
import matplotlib.pyplot as plt
import heapq
import random
from collections import defaultdict


class DentistClinic:
    def __init__(self, num_doctors=4):
        self.num_doctors = num_doctors
        self.doctors = [0] * num_doctors  # Čas, kedy bude doktor voľný
        self.waiting_queue = []
        self.waiting_times = []
        self.patients_processed = 0
        self.total_processing_time = 0
        self.urgent_cases = 0

    def add_patient(self, arrival_time, is_urgent=False, scheduled_duration=None):
        if is_urgent:
            # Urgentný prípad - vložíme na začiatok fronty
            heapq.heappush(self.waiting_queue, (0, arrival_time, scheduled_duration))
            self.urgent_cases += 1
        else:
            # Normálny prípad - vložíme na koniec fronty
            heapq.heappush(self.waiting_queue, (1, arrival_time, scheduled_duration))

    def process_patients(self, current_time):
        # Skontrolujeme, či niektorý doktor je voľný a či sú pacienti v čakárni
        while self.waiting_queue and min(self.doctors) <= current_time:
            # Nájdeme prvého voľného doktora
            doctor_idx = np.argmin(self.doctors)
            doctor_free_time = self.doctors[doctor_idx]

            # Zoberieme ďalšieho pacienta z fronty
            priority, arrival_time, duration = heapq.heappop(self.waiting_queue)

            # Skutočný čas začiatku ošetrenia
            start_time = max(arrival_time, doctor_free_time)

            # Čakacia doba
            waiting_time = start_time - arrival_time
            self.waiting_times.append(waiting_time)

            # Aktualizujeme čas doktora
            self.doctors[doctor_idx] = start_time + duration
            self.patients_processed += 1
            self.total_processing_time += duration

    def get_stats(self):
        avg_waiting_time = np.mean(self.waiting_times) if self.waiting_times else 0
        total_time = max(self.doctors) if self.doctors else 0
        utilization = self.total_processing_time / (self.num_doctors * total_time) if total_time > 0 else 0

        return {
            'avg_waiting_time': avg_waiting_time,
            'utilization': utilization,
            'patients_processed': self.patients_processed,
            'urgent_cases': self.urgent_cases,
            'queue_lengths': self.queue_lengths if hasattr(self, 'queue_lengths') else []
        }


def simulate_day(scenario_func, num_doctors=4, show_plot=True):
    clinic = DentistClinic(num_doctors)
    clinic.queue_lengths = []

    # Simulácia času v minútach počas 6-hodinovej smeny
    simulation_duration = 6 * 60
    urgent_prob = 10 / (6 * 60)  # 10 urgentných prípadov za 6 hodín

    # Naplánované príchody pacientov podľa scenára
    scheduled_arrivals = scenario_func()

    # Simulácia každú minútu
    for minute in range(simulation_duration):
        # Pridanie urgentných prípadov
        if random.random() < urgent_prob:
            duration = random.uniform(20, 30)
            clinic.add_patient(minute, is_urgent=True, scheduled_duration=duration)

        # Pridanie naplánovaných pacientov
        for arrival in scheduled_arrivals:
            if arrival == minute:
                # Pacienti neprídu presne, ale +-10 minút
                actual_arrival = minute + random.randint(-10, 10)
                actual_arrival = max(0, min(actual_arrival, simulation_duration - 1))

                # Normálne ošetrenie trvá 20-30 minút, každý 5. má komplikáciu
                if random.random() < 0.2:  # 20% šanca na komplikáciu
                    duration = random.uniform(40, 60)
                else:
                    duration = random.uniform(20, 30)

                clinic.add_patient(actual_arrival, is_urgent=False, scheduled_duration=duration)

        # Spracovanie pacientov
        clinic.process_patients(minute)

        # Zaznamenanie dĺžky fronty
        clinic.queue_lengths.append(len(clinic.waiting_queue))

    # Výpočet štatistík
    stats = clinic.get_stats()

    # Vykreslenie grafu
    if show_plot:
        plt.figure(figsize=(10, 5))
        plt.plot(clinic.queue_lengths)
        plt.title('Počet pacientov v čakárni v priebehu dňa')
        plt.xlabel('Čas (minúty)')
        plt.ylabel('Počet pacientov v čakárni')
        plt.grid(True)
        plt.show()

    return stats


# Definície scenárov
def scenario_1():
    # 4 pacienti každých 30 minút (48 pacientov denne)
    arrivals = []
    for interval in range(0, 6 * 60, 30):
        for _ in range(4):
            arrivals.append(interval)
    return arrivals


def scenario_2():
    # 3 pacienti každých 20 minút (54 pacientov denne)
    arrivals = []
    for interval in range(0, 6 * 60, 20):
        for _ in range(3):
            arrivals.append(interval)
    return arrivals


def scenario_3():
    # 2 pacienti každých 15 minút (48 pacientov denne)
    arrivals = []
    for interval in range(0, 6 * 60, 15):
        for _ in range(2):
            arrivals.append(interval)
    return arrivals

# Nový optimalizovaný scenár
def optimal_scenario():
    # 2 pacienti každých 19 minút (32-33 pacientov denne)
    arrivals = []
    for interval in range(0, 6*60, 19):
        for _ in range(2):
            arrivals.append(interval)
    return arrivals

# Spustenie simulácií
print("Scenár 1: 4 pacienti každých 30 minút (48 pacientov denne)")
stats1 = simulate_day(scenario_1)
print(f"Priemerná čakacia doba: {stats1['avg_waiting_time']:.2f} min")
print(f"Vyťaženosť doktorov: {stats1['utilization']*100:.2f}%")
print(f"Spracovaných pacientov: {stats1['patients_processed']}")
print(f"Urgentné prípady: {stats1['urgent_cases']}\n")

print("Scenár 2: 3 pacienti každých 20 minút (54 pacientov denne)")
stats2 = simulate_day(scenario_2)
print(f"Priemerná čakacia doba: {stats2['avg_waiting_time']:.2f} min")
print(f"Vyťaženosť doktorov: {stats2['utilization']*100:.2f}%")
print(f"Spracovaných pacientov: {stats2['patients_processed']}")
print(f"Urgentné prípady: {stats2['urgent_cases']}\n")

print("Scenár 3: 2 pacienti každých 15 minút (48 pacientov denne)")
stats3 = simulate_day(scenario_3)
print(f"Priemerná čakacia doba: {stats3['avg_waiting_time']:.2f} min")
print(f"Vyťaženosť doktorov: {stats3['utilization']*100:.2f}%")
print(f"Spracovaných pacientov: {stats3['patients_processed']}")
print(f"Urgentné prípady: {stats3['urgent_cases']}\n")

print("Optimalizovaný scenár: 2 pacienti každých 19 minút (36 pacientov denne)")
stats_opt = simulate_day(optimal_scenario)
print(f"Priemerná čakacia doba: {stats_opt['avg_waiting_time']:.2f} min")
print(f"Vyťaženosť doktorov: {stats_opt['utilization']*100:.2f}%")
print(f"Spracovaných pacientov: {stats_opt['patients_processed']}")
print(f"Urgentné prípady: {stats_opt['urgent_cases']}\n")

# Viacnásobná simulácia pre presnejšie výsledky
print("\nPresnejšie výsledky pre optimálny scenár (20 simulácií):")
wait_times = []
utilizations = []
patients_processed = []
urgent_cases = []

for _ in range(20):
    stats = simulate_day(optimal_scenario, show_plot=False)
    wait_times.append(stats['avg_waiting_time'])
    utilizations.append(stats['utilization']*100)
    patients_processed.append(stats['patients_processed'])
    urgent_cases.append(stats['urgent_cases'])

print(f"Priemerná čakacia doba: {np.mean(wait_times):.2f} ± {np.std(wait_times):.2f} min")
print(f"Priemerná vyťaženosť: {np.mean(utilizations):.2f} ± {np.std(utilizations):.2f}%")
print(f"Priemerný počet pacientov: {np.mean(patients_processed):.1f} ± {np.std(patients_processed):.1f}")
print(f"Priemerné urgentné prípady: {np.mean(urgent_cases):.1f} ± {np.std(urgent_cases):.1f}")