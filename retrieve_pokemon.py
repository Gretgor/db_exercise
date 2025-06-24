import sys, os, requests, re
from bs4 import BeautifulSoup
from pandas import read_html
import pandas as pd
from io import StringIO

class FullTable():
    typeref = {
        "Normal": "damage_normal",
        "Fire": "damage_fire",
        "Water": "damage_water",
        "Electric": "damage_electric",
        "Grass": "damage_grass",
        "Ice": "damage_ice",
        "Fighting": "damage_fighting",
        "Poison": "damage_poison",
        "Ground": "damage_ground",
        "Flying": "damage_flying",
        "Psychic": "damage_psychic",
        "Bug": "damage_bug",
        "Rock": "damage_rock",
        "Ghost": "damage_ghost",
        "Dragon": "damage_dragon",
        "Dark": "damage_dark",
        "Steel": "damage_steel",
    }
    att_list = [
        "name", "nat_dex_id", "type1", "type2", "egg_group1", "egg_group2",
        "height", "weight",  "male_ratio",
        "classification", "capture_rate", "egg_steps", "exp_growth",
        "ev", "color", "sz_flee_rate", "ability", "base_happiness", "base_atk",
        "base_def", "base_spatk", "base_spdef", "base_speed", "base_hp", "damage_normal", "damage_fire",
        "damage_water", "damage_grass", "damage_electric", "damage_ice",
        "damage_fighting", "damage_poison", "damage_ground", 
        "damage_flying", "damage_psychic", "damage_bug", "damage_rock", 
        "damage_ghost","damage_dragon", "damage_dark", "damage_steel",
        "dex_entry_diamond", "dex_entry_pearl", "dex_entry_platinum", 
        "dex_entry_HG", "dex_entry_SS"
    ]

    def __init__(self):
        self.pokemon_list = []

    def add_pokemon(self,pokemon):
        self.pokemon_list.append(pokemon)

    def save_pokemon_data(self, outfile):
        with open(outfile,"w") as file:
            # print full header
            for element in self.att_list:
                file.write(f"{element}; ")
            file.write("\n")
            for pokemon in self.pokemon_list:
                for key in self.att_list:
                    if key not in pokemon:
                        print(f"Pokemon {pokemon['name']} (ID {pokemon['nat_dex_id']}) has no key {key}!")
                        file.write(f"{None}; ")
                    else:
                        file.write(f"{pokemon[key]}; ")
                file.write("\n")
        
def turn_links_into_text(raw_html):
    soup = BeautifulSoup(raw_html,"lxml")

    # turn all links into text, because Serebii often makes table 
    # entries comprised of links with no text
    for a in soup.find_all('a'):
        href = a.get('href')
        text = a.get_text(strip=True)
        if href and not text:
            # this may be ugly, but I'm relying on the idea that basically every URL
            # is named after the thing it contains
            a.replace_with(f"{href.split('/')[-1].split('.')[0].capitalize()} ")
        else:
            a.replace_with(text)
    for o in soup.find_all('option'):
        # options have to be changed into text because of egg groups
        text = o.get_text()
        o.replace_with(f"{text} ")
    return soup

def check_for_basic_entries(dataframe):
    out_dict = {}
    
    for column in dataframe.columns:
        if dataframe[column].iloc[0] == "Name":
            out_dict["name"] = dataframe[column].iloc[1]
            if "Mega " in out_dict["name"]:
                out_dict["name"] = out_dict["name"].split(" ")[1]
        if dataframe[column].iloc[0] == "No.":
            out_dict["nat_dex_id"] = int(dataframe[column].iloc[1].split("#")[1][0:3])
        if dataframe[column].iloc[0] == "Gender Ratio":
            aux = dataframe[column].iloc[1].split(":")
            if len(aux) < 2:
                out_dict["male_ratio"] = None
            else:
                out_dict["male_ratio"] = float(dataframe[column].iloc[1].split(":")[1].split("%")[0])
        if dataframe[column].iloc[0] == "Type":
            aux = dataframe[column].iloc[1].split(" ")
            out_dict["type1"] = aux[0]
            if len(aux) < 2:
                out_dict["type2"] = None
            else:
                out_dict["type2"] = aux[-1]
        if dataframe[column].iloc[0] == "Egg Groups":
            # Unbreedable pokemon must be Null (nobody ain't touching that thang)
            if "cannot breed" not in dataframe[column].iloc[1]:
                # Water egg groups require special attention (Water 1, Water 2, Water 3)
                if "Water" not in dataframe[column].iloc[1]:
                    out_dict["egg_group1"] = dataframe[column].iloc[1].split(" ")[0]
                    out_dict["egg_group2"] = dataframe[column].iloc[1].split(" ")[-1]
                else:
                    aux = dataframe[column].iloc[1].split(" ")
                    if aux[0] == "Water":
                        out_dict["egg_group1"] = f"Water {aux[1]}"
                    else:
                        out_dict["egg_group1"] = aux[0]
                    if aux[-2] == "Water":
                        out_dict["egg_group2"] = f"Water {aux[-1]}"
                    else:
                        out_dict["egg_group2"] = aux[-1]
            else:
                out_dict["egg_group1"] = None
                out_dict["egg_group2"] = None

        if dataframe.shape[0] > 3:
            if "Ability" in str(dataframe[column].iloc[2]):
                out_dict["ability"] = dataframe[column].iloc[3].split(":")[0]
        if dataframe.shape[0] > 5:
            if dataframe[column].iloc[4] == "Classification":
                out_dict["classification"] = dataframe[column].iloc[5]
            if dataframe[column].iloc[4] == "Capture Rate":
                out_dict["capture_rate"] = int(dataframe[column].iloc[5])
            if dataframe[column].iloc[4] == "Base Egg Steps":
                out_dict["egg_steps"] = int(dataframe[column].iloc[5].replace(",",""))
        if dataframe.shape[0] > 7:
            if dataframe[column].iloc[6] == "Experience Growth":
                out_dict["exp_growth"] = int(dataframe[column].iloc[7].split(" ")[0].replace(",",""))
            if dataframe[column].iloc[6] == "Base Happiness":
                out_dict["base_happiness"] = int(dataframe[column].iloc[7])
            if dataframe[column].iloc[6] == "Effort Values Earned":
                out_dict["ev"] = dataframe[column].iloc[7]
            if dataframe[column].iloc[6] == "Colour":
                out_dict["color"] = dataframe[column].iloc[7]
            if dataframe[column].iloc[6] == "Safari Zone Flee Rate":
                out_dict["sz_flee_rate"] = int(dataframe[column].iloc[7])
    return out_dict

def check_for_defense(dataframe):
    out_dict = {}
    for column in dataframe:
        if dataframe[column].iloc[0] == "Damage Taken":
            key_to_treat = FullTable.typeref[dataframe[column].iloc[1]]
            out_dict[key_to_treat] = float(dataframe[column].iloc[2].split("*")[1])
    return out_dict
        
def check_for_size_data(dataframe):
    out_dict = {}
    for column in dataframe.columns:
        # taking the METRIC information for height and weight.
        # can convert in the database reading application if need be.
        if dataframe[column].iloc[0] == "Weight":
            out_dict["weight"] = float(dataframe[column].iloc[1].split(" ")[2].split("k")[0])
        if dataframe[column].iloc[0] == "Height":
            out_dict["height"] = float(dataframe[column].iloc[1].split(" ")[-1].split("m")[0])
    return out_dict

def check_for_pokedex_entries(dataframe):
    out_dict = {}
    if dataframe[0].iloc[0] == "Flavour Text":
        # had to add this bizarre removal of non-relevant characters because Exeggutor was breaking this particular line
        out_dict["dex_entry_diamond"] = re.sub(r'[^a-zA-Z0-9\ \,\.\:\-\_\!\?]','',dataframe[1].iloc[1])
        out_dict["dex_entry_pearl"] = re.sub(r'[^a-zA-Z0-9\ \,\.\:\-\_\!\?]','',dataframe[1].iloc[2])
        out_dict["dex_entry_platinum"] = re.sub(r'[^a-zA-Z0-9\ \,\.\:\-\_\!\?]','',dataframe[1].iloc[3])
        out_dict["dex_entry_HG"] = re.sub(r'[^a-zA-Z0-9\ \,\.\:\-\_\!\?]','',dataframe[1].iloc[4])
        out_dict["dex_entry_SS"] = re.sub(r'[^a-zA-Z0-9\ \,\.\:\-\_\!\?]','',dataframe[1].iloc[5])
    return out_dict

def check_for_base_stats(dataframe):
    out_dict = {}
    if dataframe[0].iloc[0] == "Stats":
        out_dict["base_hp"] = dataframe[2].iloc[2]
        out_dict["base_atk"] = dataframe[2].iloc[3]
        out_dict["base_def"] = dataframe[2].iloc[4]
        out_dict["base_spatk"] = dataframe[2].iloc[5]
        out_dict["base_spdef"] = dataframe[2].iloc[6]
        out_dict["base_speed"] = dataframe[2].iloc[7]
    return out_dict

def check_for_pokemon_data(dataframe):
    out_dict = {}
    out_dict.update(check_for_basic_entries(dataframe))
    if out_dict != {}:
        return out_dict
    out_dict.update(check_for_defense(dataframe))
    if out_dict != {}:
        return out_dict
    out_dict.update(check_for_size_data(dataframe))
    if out_dict != {}:
        return out_dict
    out_dict.update(check_for_base_stats(dataframe))
    if out_dict != {}:
        return out_dict
    out_dict.update(check_for_pokedex_entries(dataframe))
    return out_dict

def parse_entry(raw_html):    
    soup = turn_links_into_text(raw_html)
    out_dict = {}
    dfs = read_html(StringIO(str(soup)))
    
    for df in dfs:
        # account for empty tables. Why the hell does Serebii even have those
        if df.shape[0] < 2:
            continue
        out_dict.update(check_for_pokemon_data(df))
    print(out_dict)
    return out_dict
    

if __name__ == '__main__':

    # show the entire table if table is to be shown
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_rows', None)
    os.makedirs("pokemon_data",exist_ok=True)

    # retrieval from gen 4 (gen 1 is too simple)
    base_url = "https://serebii.net/pokedex-dp/"

    my_table = FullTable()
    
    # added to avoid overloading the server after the millionth test
    # I'd have used the cached session, but I already had the pokemon data
    # downloaded into separate files, so it's not urgent
    do_it_online = False

    # counters for success and failure
    success = 0
    failure = 0
    for i in range(1,494):
        if do_it_online:
            url = f"{base_url}{str(i).zfill(3)}.shtml"
            filename = f"pokemon_data/pokemon_{i}.shtml"
            response = requests.get(url)

            # Check if the request was ok
            if response.status_code == 200:
                print(f"OK: retrieval of pokemon {i}", file=sys.stderr)
                success += 1
                my_table.add_pokemon(parse_entry(response.text))
            else:
                print(f"Error retrieving pokemon {i} : error code {response.status_code}",file=sys.stderr)
                failure += 1
        else:
            with open(f'pokemon_data/pokemon_{i}.shtml', 'r', encoding='utf8') as file:
                text = file.read()
            my_table.add_pokemon(parse_entry(text))
                
    my_table.save_pokemon_data("pokemon_data.csv")
    print(f"Process terminated with {success} successes and {failure} failures.", file=sys.stderr)
            

