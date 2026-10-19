import json

from algorithm.genetic_algorithm import genetic_algorithm
from algorithm.hill_climbing import (hc_random_restart, hc_sideways_move, hc_steepest_accent, hc_stochastic,)
from algorithm.simulated_anneling import simulated_annealing
from problem import State


def read_input(filename):
    input_path = "../data/" + filename
    with open(input_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return State.from_dict(data)


def save_result(result, filename):
    output_dir = "../output"
    data = result.copy()
    data["initial_state"] = result["initial_state"].to_dict()
    data["final_state"] = result["final_state"].to_dict()
    
    name = filename.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    output_path = output_dir + "/" + name + "_result.json"
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")
    return output_path


def main():
    while True:
        filename = input("Masukkan file input (contoh: test1.json): ").strip()
        try:
            problem = read_input(filename)
            break
        except FileNotFoundError:
            print("File tidak ditemukan. Masukkan nama file yang benar.")
        except json.JSONDecodeError:
            print("Format JSON tidak valid. Pilih file lain.")
    initial_state = State.random(problem.packages, problem.truck)
    while True:
        cmd = input(
            "\nAlgoritma yang ingin kau pakai "
            "(Hill Climbing (HC) | Simulated Annealing (SA) | Genetic Algorithm (GA)): "
        ).strip().lower()
        
        if cmd in ("hc", "hill climbing"):
            print("\nPilih opsi Hill Climbing:")
            print("1. Steepest Accent (SA): Mencari neighbor terbaik dari state sekarang; berpotensi stuck di lokal optimum.")
            print("2. Sideways Move (SM): Mencari neighbor terbaik dan memperbolehkan neighbor dengan nilai yang sama.")
            print("3. Stochastic (SC): Generate neighbor secara random, hanya pindah jika nilainya lebih baik.")
            print("4. Random Restart (RR): Ketika pencarian berhenti, mulai ulang dari initial state random yang baru.")
            while True:
                choice = int(input("Pilih nomor atau nama varian HC: "))
                if choice in ("1", "steepest accent", "steepest ascent", "SA"):
                    algorithm = hc_steepest_accent
                elif choice in ("2", "sideways move", "SM"):
                    algorithm = hc_sideways_move
                elif choice in ("3", "stochastic", "SC"):
                    algorithm = hc_stochastic
                elif choice in ("4", "random restart", "RR"):
                    algorithm = hc_random_restart
                else:
                    print("Pilihan tidak tersedia. Pilih salah satu dari empat varian HC.")
                    continue
                break
            break
        elif cmd in ("ga", "genetic algorithm"):
            algorithm = genetic_algorithm
            break
        elif cmd in ("sa", "simulated annealing"):
            algorithm = simulated_annealing
            break
        else:
            print("Pilihan tidak tersedia. Masukkan HC, SA, atau GA.")
    while True:
        try: 
            num = input("Pilih objective function (1 = total value, 2 = total value - penalty), 3 = total value / total weight): ")
            objective_function = int(value) if value else 1
            if objective_function in (1, 2, 3):
                break
            else:
                print("Pilihan tidak tersedia. Pilih salah satu dari tiga objective function.")
        except ValueError:
            print("Masukkan bilangan bulat.")

    if algorithm == genetic_algorithm:
        while True:
            try:
                value = int(input("Jumlah populasi: "))
                population_size = int(value) if value else 30
                if population_size >= 1:
                    break
            except ValueError:
                print("Masukkan bilangan bulat >= 1.")

        while True:
            try:
                value = int(input("Jumlah generasi: "))
                generations = int(value) if value else 50
                if generations >= 0:
                    break
            except ValueError:
                print("Masukkan bilangan bulat >= 0.")

        result = genetic_algorithm(
            initial_state.packages,
            initial_state.truck,
            num = num,
            population_size=population_size,
            generations=generations,
        )
    elif algorithm == simulated_annealing:
        while True:
            try:
                value = float(input("Initial temperature [Enter = 100.0]: "))
                initial_temperature = float(value) if value else 100.0
                if initial_temperature > 0:
                    break
            except ValueError:
                print("Masukkan bilangan > 0.")

        while True:
            try:
                value = float(input("Cooling rate (0 < rate < 1) [Enter = 0.99]: "))
                cooling_rate = float(value) if value else 0.99
                if 0 < cooling_rate < 1:
                    break
            except ValueError:
                print("Masukkan bilangan di antara 0 dan 1.")

        while True:
            try:
                value = float(input("Minimum temperature [Enter = 0.1]: "))
                minimum_temperature = float(value) if value else 0.1
                if minimum_temperature >= 0 and minimum_temperature < initial_temperature:
                    break
            except ValueError:
                print("Masukkan bilangan >= 0 dan lebih kecil dari initial temperature.")

        while True:
            try:
                value = int(input("Maximum iterations: "))
                max_iterations = int(value) if value else 10000
                if max_iterations >= 1:
                    break
            except ValueError:
                print("Masukkan bilangan bulat >= 1.")

        result = simulated_annealing(
            initial_state=initial_state,
            num=num,
            initial_temperature=initial_temperature,
            cooling_rate=cooling_rate,
            minimum_temperature=minimum_temperature,
            max_iterations=max_iterations,
        )
    else:
        while True:
            try:
                value = int(input("Maximum iterations (per pencarian untuk random restart): "))
                max_iterations = int(value) if value else 1000
                if max_iterations >= 0:
                    break
            except ValueError:
                print("Masukkan bilangan bulat >= 0.")

        if algorithm == hc_sideways_move:
            while True:
                value = int(input("Maximum sideways move [Enter = 100]: "))
                try:
                    max_sideways = int(value) if value else 100
                    if max_sideways >= 0:
                        break
                except ValueError:
                    print("Masukkan bilangan bulat >= 0.")

            result = algorithm(initial_state, num=num, max_sideways=max_sideways, max_iterations=max_iterations)
        elif algorithm == hc_random_restart:
            while True:
                value = int(input("Maximum restart (di luar pencarian awal) [Enter = 10]: "))
                try:
                    max_restarts = int(value) if value else 10
                    if max_restarts >= 0:
                        break
                except ValueError:
                    print("Masukkan bilangan bulat >= 0.")

            result = algorithm(initial_state, num=num, max_restarts=max_restarts, max_iterations=max_iterations)
        else:
            result = algorithm(initial_state, num=num, max_iterations=max_iterations)
    output_path = save_result(result, filename)

    print(f"\nAlgoritma: {result['algorithm']}")
    print(f"Nilai awal: {result['initial_value']}")
    print(f"Nilai akhir: {result['final_value']}")
    print(f"Durasi: {result['duration'] * 1000:.2f} ms")
    print(f"Hasil disimpan di: {output_path}")


if __name__ == "__main__":
    main()
