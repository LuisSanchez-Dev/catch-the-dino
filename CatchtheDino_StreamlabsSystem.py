# Catch the Dino script for Streamlabs Chatbot
# Copyright (C) 2020 Luis Sanchez
# 
# Versions:
#   - 1.0.0 08/27/2020: Release

import os
import sys
import clr
import codecs
import re
import json
import threading

# Required script variables
ScriptName  = "Catch the Dino"
Description = "Win points taming dinosaurs from all sizes!"
Creator     = "LuisSanchezDev"
Website     = "https://www.fiverr.com/luissanchezdev"
Version     = "1.0.0"

# Define Global Variables
global PATH, CONFIG_FILE, SETTINGS
PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(PATH, "config.json")
SETTINGS   = {}


# Initialize Data (Only called on load)
def Init():
  global SETTINGS, CONFIG_FILE
  
  try:
    with codecs.open(CONFIG_FILE, encoding='utf-8-sig', mode='r') as file:
      SETTINGS = json.load(file, encoding='utf-8-sig')
  except Exception as error:
    SETTINGS = {
      "command": "!tame",
      "cmd_feed": "!feed",
      "usercd": 30,
      "globalcd": 3,
      "firstline": "$user attempts to tame $adjective $dino",
      "firsttosecondwait": 5,
      "secondline": ". . .",
      "secondtothirdwait": 5,
      "thirdtofourthwait": 5,
      "win_line": "$user won $points $currency for taming a $adjective $dino!",
      "win_response": "This dino is tamed!!",
      "lose_response": "This dino ran away",
      "tame_prize": 10,
      "small_mult": 1,
      "medium_mult": 2,
      "big_mult": 3,
      "feed_msg_win": "The $adjective $dino ate the food peacefully, you win $prize $currency",
      "feed_msg_lose": "The $adjective $dino growls at you, better luck next time",

    }

# Execute Data / Process messages
def Execute(data):
  global SETTINGS
  if data.IsChatMessage():
    if data.GetParam(0) == SETTINGS["cmd_feed"]:
      size = get_random_size()
      dinosaur = get_dinosaur_of_size(size)
      success = Parent.GetRandom(0, 100) >= 50
      if success:
        points = SETTINGS["tame_prize"] * SETTINGS[size + "_mult"] / 3
        output = SETTINGS["feed_msg_win"]
        output = output.replace(  '$dino'   ,dinosaur)
        output = output.replace('$adjective',size)
        output = output.replace(  '$user'   ,data.User)
        output = output.replace( '$prize'  ,str(points))
        output = output.replace('$currency' ,Parent.GetCurrencyName())
        Parent.SendStreamMessage((output))
        Parent.AddPoints(data.User, data.User, points)
      else:
        output = SETTINGS["feed_msg_lose"]
        output = output.replace(  '$dino'   ,dinosaur)
        output = output.replace('$adjective',size)
        Parent.SendStreamMessage(output)
      return
    elif not data.GetParam(0) == SETTINGS['command']: return
    if Parent.IsOnUserCooldown(ScriptName, SETTINGS["command"], data.User) and int(SETTINGS["usercd"]) > 0:
      output = get_random_user_cd_response()['name'].replace('$user',data.User)
      output = output.replace('$randusername',Parent.GetRandomActiveUser())
      Parent.SendStreamMessage(output)
      return
    if Parent.IsOnCooldown(ScriptName, SETTINGS["command"]) and int(SETTINGS["globalcd"]) > 0:
      output = get_random_global_cd_response()['name'].replace('$user',data.User)
      output = output.replace('$randusername',Parent.GetRandomActiveUser())
      Parent.SendStreamMessage(output)
      return

    size = get_random_size()
    dinosaur  = get_dinosaur_of_size(size)
    success   = get_random_success()
    
    firstline = SETTINGS['firstline']
    firstline = firstline.replace('$user'     ,data.User)
    firstline = firstline.replace('$adjective', size)
    firstline = firstline.replace('$dino'     ,dinosaur)
    Parent.SendStreamMessage(firstline)
    
    threading.Timer(SETTINGS['firsttosecondwait'],lambda: Parent.SendStreamMessage(SETTINGS['secondline'])).start()
    lastlineswait = SETTINGS['firsttosecondwait'] + SETTINGS['secondtothirdwait']
    
    successline = success['name']
    successline = successline.replace('$dino',dinosaur)
    successline = successline.replace('$user',data.User)
    threading.Timer(lastlineswait,lambda: Parent.SendStreamMessage(successline)).start()
    
    if success["success"]:
      points = SETTINGS["tame_prize"] * SETTINGS[size + "_mult"]

      output = SETTINGS["win_line"]
      output = output.replace(  '$dino'   ,dinosaur)
      output = output.replace('$adjective',size)
      output = output.replace(  '$user'   ,data.User)
      output = output.replace( '$points'  ,str(points))
      output = output.replace('$currency' ,Parent.GetCurrencyName())
      threading.Timer(lastlineswait + SETTINGS['thirdtofourthwait'],lambda: Parent.SendStreamMessage(output)).start()
      threading.Timer(lastlineswait + SETTINGS['thirdtofourthwait'],lambda: Parent.AddPoints(data.User,data.UserName,points)).start()
    Parent.AddUserCooldown(ScriptName, SETTINGS["command"], data.User, int(SETTINGS["usercd"]) * 60)
    Parent.AddCooldown(ScriptName, SETTINGS["command"], int(SETTINGS["globalcd"]) * 60)

# Tick method (Gets called during every iteration even when there is no incoming data)
def Tick():
  pass

def get_random_size():
  sizes = [
    {"size": "small", "probability": 70},
    {"size": "medium", "probability": 20},
    {"size": "big", "probability": 10}
  ]
  sizes = sorted(sizes, key=lambda x: x['probability'])
  last_cumulative_prob = 0.0
  for size in sizes:
    size['cumulativeprobability'] = last_cumulative_prob + size['probability']
    last_cumulative_prob = size['cumulativeprobability']
  return get_weighted_random(sizes)["size"]

def get_random_success():
  successes = [
    {"name": SETTINGS["win_response"], "success": True, "probability": 70},
    {"name": SETTINGS["lose_response"], "success": False, "probability": 30},
  ]
  successes = sorted(successes, key=lambda x: x['probability'])
  last_cumulative_prob = 0.0
  for success in successes:
    success['cumulativeprobability'] = last_cumulative_prob + success['probability']
    last_cumulative_prob = success['cumulativeprobability']
  return get_weighted_random(successes)

def get_dinosaur_of_size(size):
  dino_file = os.path.join(PATH, "config",size + ".txt")
  lines = list(open(dino_file))
  if len(lines) > 0:
    return lines[Parent.GetRandom(0, len(lines))].replace("\r","").replace("\n","")

def get_random_user_cd_response():
  return get_weighted_random(load_user_cd_responses())
def get_random_global_cd_response():
  return get_weighted_random(load_global_cd_responses())
def get_weighted_random(inputlist):
  dice = Parent.GetRandom(0, inputlist[-1]["cumulativeprobability"])
  for entry in inputlist:
    if entry['cumulativeprobability'] >= dice:
      return entry

def load_user_cd_responses():
  return parse_list_file('config\\usercd_responses.json')
def load_global_cd_responses():
  return parse_list_file('config\\globalcd_responses.json')
def parse_list_file(filename):
  global PATH
  content = []
  try:
    with codecs.open(os.path.join(PATH, filename), encoding='utf-8-sig', mode='r') as file:
      content = json.load(file, encoding='utf-8-sig')
  except Exception as error:
    Parent.Log('ERROR','Error!' + str(error))
    return []
  
  try:
    parsedcontent = sorted(content, key = lambda x : x['probability'])
  except:
    MessageBox.Show(str(content))
    return
  lastprob = 0.0
  for line in parsedcontent:
    line['cumulativeprobability'] = lastprob + line['probability']
    lastprob = line['cumulativeprobability']
  return parsedcontent

# UI Buttons
def edit_small_dinos():
  file_path = os.path.join(PATH, "config", "small.txt")
  os.startfile(file_path)
def edit_medium_dinos():
  file_path = os.path.join(PATH, "config", "medium.txt")
  os.startfile(file_path)
def edit_big_dinos():
  file_path = os.path.join(PATH, "config", "big.txt")
  os.startfile(file_path)
def edit_global_cd():
  file_path = os.path.join(PATH, "config", "small.txt")
  os.startfile(file_path)
def donate():
  os.startfile("https://streamlabs.com/luissanchezdev/tip")
def open_contact_me():
  os.startfile("https://www.fiverr.com/luissanchezdev")
def open_readme():
  os.startfile("https://github.com/LuisSanchez-Dev/catch-the-dino")