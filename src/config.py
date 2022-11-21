
import json

config_vals = {}

def load_config():
    global config_vals
    try:
        with open("src\config.txt") as f:
            data = f.read()
            print(data)
            if(data):
                config_vals = json.loads(data)
        for key in config_vals.keys():
            print(key)
        print("loaded")
    except (FileNotFoundError or json.decoder.JSONDecodeError):
        config_vals = {}
        print("Config file not found; no configuration loaded")
        


def change_config(guild, key, val):
    global config_vals
    if (guild.name not in config_vals.keys()):
        config_vals[guild.name] = {}
    
    config_vals[guild.name][key] = val
    save_config(0)

def save_config(exit_flag=0):
    global config_vals
    print(config_vals)
    with open("src\config.txt", "w") as outfile:
        outfile.write(json.dumps(config_vals))
    print("saved")
