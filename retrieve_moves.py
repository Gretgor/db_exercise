import sys, os, requests, re
from bs4 import BeautifulSoup
from pandas import read_html
import pandas as pd
from io import StringIO

class MoveTable:
    att_list = ["name", "type", "category", "PP", "power", "accuracy", 
                "battle_effect", "secondary_effect", "contest_type", 
                "contest_effect", "contest_points", "TM", "priority",
                "target", "bright_powder", "kings_rock", "contact"]
    def __init__(self):
        move_list = []

    def add_move(self, move):
        move_list.append(move)

    def save_move_data(self, outfile):
        with open(outfile,"w") as file:
            # print full header
            for element in self.att_list:
                file.write(f"{element}; ")
            file.write("\n")
            for move in self.move_list:
                for key in self.att_list:
                    if key not in move:
                        print(f"Move {move['name']} has no key {key}!")
                        file.write(f"{None}; ")
                    else:
                        file.write(f"{move[key]}; ")
                file.write("\n")

class LearnTable:
    att_list = ["nat_dex_id", "move", "level", "method"]
    def __init__(self):
        learn_list = []

    def add_learn(self, learn):
        learn_list.append(learn)

    def save_learn_data(self, outfile):
        with open(outfile,"w") as file:
            # print full header
            for element in self.att_list:
                file.write(f"{element}; ")
            file.write("\n")
            for learn in self.learn_list:
                for key in self.att_list:
                    if key not in learn:
                        print(f"Learnset {learn['nat_dex_id']},{learn['move']} has no key {key}!")
                        file.write(f"{None}; ")
                    else:
                        file.write(f"{learn[key]}; ")
                file.write("\n")
