from pathlib import Path

import tika
import os
from tika import parser
import re
import matplotlib.pyplot as plt
import numpy as np


class Consumption:
    def __init__(self):
        self.cold_water_pat = re.compile(r"Hidegvíz\s(.*?)\sm3", re.IGNORECASE)
        self.warm_water_pat = re.compile(r"Melegvíz\s(.*?)\sm3", re.IGNORECASE)
        self.heat_loss_pat = re.compile(r"Hőmennyiségmérő\s(.*?)\sMWH", re.IGNORECASE)
        self.month_pat = re.compile(r"Fogyasztás\sidőszaka:\s?(20[12]\d\.\d{2})")
        self.results = {}

    def get_cold_water(self, document: str):
        return self.cold_water_pat.search(document).group(1).split()[-1]

    def get_warm_water(self, document: str):
        return self.warm_water_pat.search(document).group(1).split()[-1]

    def get_heat_loss(self, document: str):
        return self.heat_loss_pat.search(document).group(1).split()[-1].replace(",", ".")

    def get_year_month(self, document: str):
        return self.month_pat.search(document).group(1)

    def get_data_from_document(self, document: str):
        year_month = self.get_year_month(document)
        heat_loss = float(self.get_heat_loss(document))
        cold_water = float(self.get_cold_water(document))
        warm_water = float(self.get_warm_water(document))
        self.results.update({year_month: {"Hidegvíz": cold_water, "Melegvíz": warm_water, "Hőmennyiség": heat_loss}})

    def plot_results(self):
        years = sorted(list(set([year.split(".")[0] for year in sorted(list(self.results.keys()))])))
        months = [num for num in range(1, 13)]
        colors = plt.cm.viridis(np.linspace(0, 1, len(years)))
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(9, 3), sharey=False)
        ax1.set_title("Hidegvíz fogyasztás [m3]")
        ax2.set_title("Melegvíz fogyasztás [m3]")
        ax3.set_title("Hőmennyiség [MWh]")
        for index, ev in enumerate(years):
            years_months = ["{}.{}".format(ev, honap) if honap > 9 else "{}.0{}".format(ev, honap) for honap in months]
            cold_waters = [self.results.get(month).get("Hidegvíz") for month in years_months if self.results.get(month)]
            warm_waters = [self.results.get(month).get("Melegvíz") for month in years_months if self.results.get(month)]
            heat_losses = [self.results.get(month).get("Hőmennyiség") for month in years_months if
                           self.results.get(month)]

            ax1.plot(months[:len(cold_waters)], cold_waters, markersize=10, c=colors[index], linestyle='-', marker="o", label=ev)
            ax2.plot(months[:len(warm_waters)], warm_waters, markersize=10, c=colors[index], linestyle='-', marker="o", label=ev)
            ax3.plot(months[:len(heat_losses)], heat_losses, markersize=10, c=colors[index], linestyle='-', marker="o", label=ev)

        ax1.grid(which='both', axis='both')
        ax2.grid(which='both', axis='both')
        ax3.grid(which='both', axis='both')
        ax1.set_xticks(months, months)
        ax2.set_xticks(months, months)
        ax3.set_xticks(months, months)
        ax1.legend()
        ax2.legend()
        ax3.legend()
        fig.tight_layout()
        plt.show()


if __name__ == "__main__":
    consumption = Consumption()
    tika.initVM()
    path = Path(__file__).parent.joinpath("inbox").as_posix()
    # print(os.listdir(path))
    for doc in os.listdir(path):
        parsed = parser.from_file(os.path.join(path, doc))
        consumption.get_data_from_document(parsed.get("content"))
    print(consumption.results)
    consumption.plot_results()
