
import json
import os
import mysql.connector 
from mysql.connector import errorcode
import sys

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



#-------------------------

def connect_to_db():
    try:
        conn =  mysql.connector.connect(user=os.getenv('MYSQL_USER'), password=os.getenv('MYSQL_PASSWORD'),
                                    host=os.getenv('MYSQL_HOST'),
                                    database=os.getenv('MYSQL_DATABASE'))
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
            dbcur.execute("INSERT IGNORE INTO Servers (server_id,server_name, mod_channel_id, mod_role_id) VALUES (?, ?, ?, ?);", (server_id, server_name, mod_channel_id, mod_role)) 
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
        dbcur.execute("INSERT INTO Servers (server_id,server_name) VALUES (?, ?);", (name,id)) 
        conn.commit()
        dbcur.close()
        conn.close()
        change_config(guild, "id", guild.id)
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
        dbcur.execute("UPDATE Servers SET mod_role_id = ? WHERE server_id = ?;", (role_id,guild_id)) 
        conn.commit()
        dbcur.close()
        conn.close()
        change_config(guild, "mod_role", role.id)
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
    guild_id = "'" + str(guild.id) + "'"
    channel_id = "'" + str(channel.id) + "'"
    try:
        conn = connect_to_db()
        dbcur = conn.cursor()
        dbcur.execute("UPDATE Servers SET mod_channel_id = ? WHERE server_id = ?;", (channel_id,guild_id)) 
        conn.commit()
        dbcur.close()
        conn.close()
        change_config(guild, "output_channel", channel.id)
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
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        config_vals = {}
        #retrieving information 
        cur.execute("SELECT * FROM Servers;") 

        for server_id, server_name, mod_channel_id, mod_role_id  in cur: 
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
