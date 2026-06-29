import tkinter as tk
from tkinter import ttk
import numpy as np
import random
from collections import Counter
import threading


teams_data = {
    'France': {'elo': 2123, 'form': 0.95, 'attack': 2.8, 'defense': 0.8, 'home': 0.0, 'color': '#002654'},
    'Argentina': {'elo': 2148, 'form': 0.92, 'attack': 2.4, 'defense': 0.9, 'home': 0.0, 'color': '#74ACDF'},
    'Spain': {'elo': 2144, 'form': 0.88, 'attack': 2.2, 'defense': 0.7, 'home': 0.0, 'color': '#C8102E'},
    'England': {'elo': 2038, 'form': 0.85, 'attack': 2.5, 'defense': 1.0, 'home': 0.0, 'color': '#00247D'},
    'Brazil': {'elo': 2009, 'form': 0.82, 'attack': 2.6, 'defense': 1.1, 'home': 0.0, 'color': '#00A859'},
    'Germany': {'elo': 1916, 'form': 0.80, 'attack': 2.3, 'defense': 1.0, 'home': 0.0, 'color': '#000000'},
    'Portugal': {'elo': 1990, 'form': 0.83, 'attack': 2.4, 'defense': 1.0, 'home': 0.0, 'color': '#006600'},
    'Netherlands': {'elo': 1980, 'form': 0.84, 'attack': 2.3, 'defense': 0.9, 'home': 0.0, 'color': '#FF9900'},
    'USA': {'elo': 1850, 'form': 0.78, 'attack': 2.0, 'defense': 1.2, 'home': 0.15, 'color': '#002868'},
}

class WorldCupPredictorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("2026 FIFA World Cup • Forecaster")
        self.root.geometry("1000x720")
        self.root.configure(bg="#0a1428")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#0a1428")
        style.configure("TLabel", background="#0a1428", foreground="#e2e8f0")
        style.configure("Header.TLabel", font=("Playfair Display", 28, "bold"), foreground="#f8fafc")
        
        self.create_widgets()
        self.simulating = False

    def create_widgets(self):
        # Title
        title_frame = ttk.Frame(self.root)
        title_frame.pack(pady=20, fill='x')
        
        tk.Label(title_frame, text="⚽  2026 FIFA WORLD CUP", 
                font=("Playfair Display", 36, "bold"), 
                fg="#f8fafc", bg="#0a1428").pack()
        tk.Label(title_frame, text="Probabilistic Forecaster", 
                font=("Inter", 16), fg="#64748b", bg="#0a1428").pack()

        # Control Panel
        ctrl_frame = ttk.Frame(self.root)
        ctrl_frame.pack(pady=10, padx=40, fill='x')
        
        self.sim_btn = tk.Button(ctrl_frame, text="RUN 10,000 SIMULATIONS", 
                                font=("Inter", 14, "bold"), bg="#eab308", fg="#0a1428",
                                activebackground="#facc15", height=2, width=30,
                                command=self.start_simulation)
        self.sim_btn.pack(pady=10)

        # Results Area
        self.result_frame = ttk.Frame(self.root)
        self.result_frame.pack(pady=20, padx=40, fill='both', expand=True)

        # Table
        columns = ("Rank", "Team", "Win Probability", "Finalist Probability")
        self.tree = ttk.Treeview(self.result_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200, anchor='center')
        
        self.tree.pack(fill='both', expand=True)

        # Status
        self.status = tk.Label(self.root, text="Ready • Click to simulate", 
                             fg="#64748b", bg="#0a1428", font=("Inter", 11))
        self.status.pack(pady=10)

    def simulate_match(self, team1, team2):
        t1 = teams_data.get(team1, {'elo': 1800, 'form': 0.7, 'attack': 1.8, 'defense': 1.3, 'home': 0})
        t2 = teams_data.get(team2, {'elo': 1800, 'form': 0.7, 'attack': 1.8, 'defense': 1.3, 'home': 0})
        
        elo_diff = (t1['elo'] - t2['elo']) / 400
        lambda1 = 1.35 + elo_diff * 1.4 + t1['attack'] - t2['defense'] + t1['home']
        lambda2 = 1.35 - elo_diff * 1.4 + t2['attack'] - t1['defense'] + t2['home']
        
        goals1 = np.random.poisson(max(0.4, lambda1 * t1['form']))
        goals2 = np.random.poisson(max(0.4, lambda2 * t2['form']))
        
        if goals1 > goals2: return team1
        elif goals2 > goals1: return team2
        else: return random.choice([team1, team2])

    def run_simulation(self):
        n_sims = 10000
        win_counter = Counter()
        
        for _ in range(n_sims):
            # Weighted random winner (Monte Carlo)
            weights = [data['elo'] * data['form'] * (1 + data['home']) for data in teams_data.values()]
            winner = random.choices(list(teams_data.keys()), weights=weights, k=1)[0]
            win_counter[winner] += 1
        
        # Prepare results
        results = []
        for team, wins in win_counter.most_common():
            prob = (wins / n_sims) * 100
            results.append((team, round(prob, 2)))
        
        # Update GUI
        self.update_table(results)

    def update_table(self, results):
        # Clear previous
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, (team, prob) in enumerate(results[:12], 1):
            color = teams_data.get(team, {}).get('color', '#64748b')
            self.tree.insert("", "end", values=(f"#{i}", team, f"{prob}%", "—"))
            
            # Color the row
            tag = f"tag_{i}"
            self.tree.tag_configure(tag, foreground=color)
            self.tree.item(self.tree.get_children()[-1], tags=(tag,))

    def start_simulation(self):
        if self.simulating:
            return
        self.simulating = True
        self.sim_btn.config(state="disabled", text="SIMULATING...")
        self.status.config(text="Running simulations... Please wait")
        
        def sim_thread():
            self.run_simulation()
            self.root.after(0, self.finish_simulation)
        
        threading.Thread(target=sim_thread, daemon=True).start()

    def finish_simulation(self):
        self.simulating = False
        self.sim_btn.config(state="normal", text="RUN NEW SIMULATION")
        self.status.config(text="Simulation Complete • Updated June 29, 2026")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = WorldCupPredictorGUI()
    app.run()
