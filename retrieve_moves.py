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

if __name__ == '__main__':
    with open("attackdex_main_page.html", "r", encoding="latin1") as file:
        raw_data = file.readlines()

    # strip the main page of everything that isn't a move, this will be our retrieval list
    links_to_visit = [line.split("\"")[1] for line in raw_data if "option value=\"/attackdex-dp/" in line]
    
    # show the entire table if table is to be shown
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_rows', None)
    os.makedirs("move_data",exist_ok=True)

    base_url = "https://serebii.net"

    for page in links_to_visit:
        base_name = page.split("/")[-1]
        if not os.path.exists(f"move_data/{base_name}"):
            link_to_retrieve = f"{base_url}{page}"
            response = requests.get(link_to_retrieve)
            if response.status_code == 200:
                print(f"OK: retrieval of move {page}", file=sys.stderr)
                with open(f"move_data/{base_name}","w") as file:
                    file.write(response.text)
            else:
                print(f"FAILED to retrieve move {page}, error {respose.status_code}", file=sys.stderr)
                continue
        else:
            print(f"Using cached copy of move {page}", file=sys.stderr)
            
        
