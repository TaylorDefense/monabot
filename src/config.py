
import json
import os
import mysql.connector 
from mysql.connector import errorcode
import sys
import warnings
import random
warnings.warn("Warning...........Message")

config_vals = {}
assassin_vals = {}

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
    #save_config(0)


def save_config(exit_flag=0):
    global config_vals
    print(config_vals)
    with open("src\config.txt", "w") as outfile:
        outfile.write(json.dumps(config_vals))
    print("saved: ", config_vals)
    print()



#-------------------------

def connect_to_db():
    try:
        conn =  mysql.connector.connect(user=os.getenv('MYSQL_USER'), password=os.getenv('MYSQL_PASSWORD'),
                                    host=os.getenv('MYSQL_HOST'),
                                    database=os.getenv('MYSQL_DATABASE'))
        print("connected to db!")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    return conn

#initialize the table if it doesn't exist
def initialize_table():
    global config_vals
    try:
        conn = connect_to_db()
        dbcur = conn.cursor()
        dbcur.execute("""
            CREATE TABLE IF NOT EXISTS Servers (
                server_id VARCHAR(20) PRIMARY KEY,
                server_name VARCHAR(128) NOT NULL,
                mod_channel_id VARCHAR(20),
                mod_role_id VARCHAR(20)
            );
            """)
        # load in values saved to config file
        load_config()
        for key in config_vals.keys():
            vals = config_vals[key]
            #get values to insert
            server_name = key
            server_id = str(vals["id"])
            #get mod channel if exists
            if "output_channel" in vals.keys():
                mod_channel_id = str(vals["output_channel"])
            else:
                mod_channel_id = "NULL"
            # get mod role if exists
            if "mod_role" in vals.keys():
                mod_role = str(vals["mod_role"])
            else:
                mod_role = "NULL"
            #insert into table
            dbcur.execute("INSERT IGNORE INTO Servers (server_id,server_name, mod_channel_id, mod_role_id) VALUES (%s, %s, %s, %s);", (server_id, server_name, mod_channel_id, mod_role)) 
        print("table initialized")
        config_vals = {}
        conn.commit()
        dbcur.close()
        conn.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    return

#add a guild to the database, to be called on join
def add_guild(guild):
    name = guild.name
    id = str(guild.id)
    try:
        conn = connect_to_db()
        dbcur = conn.cursor()
        dbcur.execute("INSERT INTO Servers (server_id,server_name) VALUES (%s, %s);", (id,name)) 
        conn.commit()
        dbcur.close()
        conn.close()
        change_config(guild, "id", guild.id)
        print("added guild")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)


#add a mod role for a guild to the database
def set_mod_role(guild, role):
    guild_id =str(guild.id)
    role_id = str(role.id)
    try:
        conn = connect_to_db()
        dbcur = conn.cursor()
        dbcur.execute("UPDATE Servers SET mod_role_id = %s WHERE server_id = %s;", (role_id,guild_id)) 
        dbcur.execute("SELECT server_name, mod_role_id FROM Servers")
        for server_name, mod_role in dbcur: print(server_name, mod_role)
        conn.commit()
        dbcur.close()
        conn.close()
        change_config(guild, "mod_role", role.id)
        print("mod role set")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    return


#add a mod channel for a guild to the database
def set_mod_channel(guild, channel):
    guild_id = str(guild.id)
    channel_id = str(channel.id)
    try:
        conn = connect_to_db()
        dbcur = conn.cursor()
        dbcur.execute("UPDATE Servers SET mod_channel_id = %s WHERE server_id = %s", (channel_id,guild_id)) 
        conn.commit()
        dbcur.close()
        conn.close()
        change_config(guild, "output_channel", channel.id)
        print("mod channel set")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    return

#load config vals from the database
def load_config_from_db():
    global config_vals
    config_vals = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        config_vals = {}
        #retrieving information 
        cur.execute("SELECT * FROM Servers;") 

        for server_id, server_name, mod_channel_id, mod_role_id  in cur: 
            print(server_name, str(server_id), str(mod_channel_id), str(mod_role_id))
            config_vals[server_name] = {
                "id" : server_id,
                "output_channel" : mod_channel_id,
                "mod_role" : mod_role_id
            }
        cur.close()
        conn.close()
        print("hello from load_config_from_db()", config_vals)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    return

def show_db_instances():
    try:
        conn = connect_to_db()
        dbcur = conn.cursor()
        dbcur.execute("SELECT * FROM Servers;")
        for (server_id, server_name, mod_channel_id, mod_role_id) in dbcur: 
            print(server_name)
            print(str(server_id))
            print(str(mod_channel_id))
            print(str(mod_role_id))
            print()
        dbcur.close()
        conn.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

def clear_db():
    global config_vals
    try:
        conn = connect_to_db()
        dbcur = conn.cursor()
        dbcur.execute("DROP TABLE Servers") 
        conn.commit()
        dbcur.close()
        conn.close()
        print("dropped table")
        config_vals = {}
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

# --- ASSASSIN FUNCTIONS ---

def make_assassin_tables(gamemaster_id):
    global assassin_vals
    try:
        conn = connect_to_db()
        dbcur = conn.cursor()
        dbcur.execute("""
            CREATE TABLE IF NOT EXISTS AssassinPlayers (
                player_id INT(255) PRIMARY KEY,
                player_name VARCHAR(128) NOT NULL,
                status VARCHAR(3),
                target_id INT(255),
                target_name VARCHAR(128),
                killed_by VARCHAR(128),
                kill_count INT(255)
            );
            """)
        dbcur.execute("""
            CREATE TABLE IF NOT EXISTS Assassin (
                gamemaster_id INT(255) PRIMARY KEY,
                player_count INT(255) NOT NULL
            );
            """)
        
        dbcur.execute("INSERT INTO Assassin (gamemaster_id, player_count) VALUES (%s, %s);", (gamemaster_id, 0)) 
        conn.commit()
        dbcur.close()
        conn.close()
        print("tables created\n")
        assassin_vals = {}
        assassin_vals["gamemaster_id"] = gamemaster_id
        assassin_vals["player_count"] = 0
        assassin_vals["players"] = {}
        print(assassin_vals + "\n")
        print()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        # load in values saved to config file

def drop_assassin_tables():
    global assassin_vals
    try:
        conn = connect_to_db()
        dbcur = conn.cursor()
        dbcur.execute("DROP TABLE AssassinPlayers") 
        dbcur.execute("DROP TABLE Assassin") 
        conn.commit()
        dbcur.close()
        conn.close()
        print("dropped table AssassinPlayers and Assassin")
        assassin_vals = {}
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

def check_game_status():
    global assassin_vals
    if len(assassin_vals) != 0:
        return True
    else:
        return False

def get_gamemaster():
    global assassin_vals
    if len(assassin_vals) != 0:
        return assassin_vals["gamemaster_id"]
    else:
        return -1

def add_new_player(pid, pname):
    global assassin_vals
    try:
        conn = connect_to_db()
        dbcur = conn.cursor()
        dbcur.execute("INSERT INTO AssassinPlayers (player_id, player_name, status, target_id, target_name, killed_by, kill_count) VALUES (%d, %s, %s, %d, %s, %s, %d );", (pid, pname, "in", None, None, None, 0 )) 
        conn.commit()
        dbcur.close()
        conn.close()
        assassin_vals["players"][pid] = {}
        assassin_vals["players"][pid]["name"] = pname
        assassin_vals["players"][pid]["status"] = "in"
        assassin_vals["players"][pid]["target_id"] = None
        assassin_vals["players"][pid]["target_name"] = None
        assassin_vals["players"][pid]["killed_by"] = None 
        assassin_vals["players"][pid]["kill_count"] = 0
        print(assassin_vals)
        print("\nadded player\n")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

def get_players():
    global assassin_vals
    players = []
    if len(assassin_vals) ==  0:
        return players
    for player_id in assassin_vals["players"]:
        players.append((player_id["name"], player_id["status"]))
    print(players)
    print(assassin_vals)
    return players
    
def generate_targets():
    global assassin_vals
    if len(assassin_vals) <= 1:
        print("Not enough targets to assign")
        return
    players = assassin_vals["players"].keys()
    for player in players:
        target = player
        while target == player:
            target = players[random.randint(0, (len(players) - 1))]
            if target == player and len(players = 1):
                return generate_targets()
        players.remove(target)
        assassin_vals["players"][player]["target_id"] = target
        assassin_vals["players"][player]["target_name"] = assassin_vals["players"][target]["player_name"]


