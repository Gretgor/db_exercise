import sys, os, requests, re
from bs4 import BeautifulSoup
from retrieve_pokemon import turn_links_into_text
from pandas import read_html
import pandas as pd
from io import StringIO

""" To recall: Table IDs

0 - garbage
1 - name
2 - garbage
3 - description, type, category, pp, power, accuracy, battle effect, 
    secondary effect, contest type, contest effect, contest points (little number of hearts which is gonna be SO ANNOYING),
    TM (if any), priority (quick attack and shit), target (one, multiple, all including allies, etc), affected by bright powder, 
    affected by kings rock, makes contact
4 and onwards - learnsets

"""

class MoveTable:
    att_list = ["name", "type", "category", "PP", "power", "accuracy", 
                "battle_effect", "secondary_effect", "contest_type", 
                "contest_effect", "contest_points", "TM", "priority",
                "target", "bright_powder", "kings_rock", "contact"]
    def __init__(self):
        self.move_list = []

    def add_move(self, move):
        self.move_list.append(move)

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
        self.learn_list = []

    def add_learn(self, learn):
        self.learn_list.append(learn)

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

def check_move_info(dataframe):
    outdict = {}
    return outdict

def check_learnset(dataframe, learn_table, move_name, method):
    print(f"move name {move_name}, learn method '{method}'", file=sys.stderr)

if __name__ == '__main__':
    with open("attackdex_main_page.html", "r", encoding="latin1") as file:
        raw_data = file.readlines()

    # strip the main page of everything that isn't a move, this will be 
    # our retrieval list
    links_to_visit = [line.split("\"")[1] for line in raw_data 
                      if "option value=\"/attackdex-dp/" in line]
    
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
                print(f"FAILED to retrieve move {page}, error {respose.status_code}", 
                      file=sys.stderr)
                continue
        else:
            print(f"Using cached copy of move {page}", file=sys.stderr)

    # start the painstaking process of stripping away the useful information from
    # the absolute mess that is that website
    move_table = MoveTable()
    learn_table = LearnTable()
    
    files_to_check = [link.split('/')[-1] for link in links_to_visit]
    for filename in files_to_check:
        with open(f"move_data/{filename}") as file:
            full_data = file.readlines()
    
        # get all learn types (so we can know what learn type each table
        # corresponds to)
        learn_types = [line.split('By')[1].split('<')[0][1:].split(':')[0] 
                       for line in full_data if "That Learn" in line]

        text_soup = turn_links_into_text('\n'.join(full_data))
        dataframes = read_html(StringIO(str(text_soup)))
        
        # first, retrieve move information and add to move table
        move_info = {"name" : dataframes[1][0].iloc[0]}
        move_info.update(check_move_info(dataframes[3]))
        move_table.add_move(move_info)

        # second, retrieve learnsets from moves
        for i in range(len(learn_types)):
            check_learnset(dataframes[i+4], learn_table, move_info['name'], learn_types[i])

        
