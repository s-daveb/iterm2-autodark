#!/usr/bin/env python3

import asyncio
import iterm2
import sys
import random

# Duration between checks
DETECTION_DELAY_SECONDS=1

# Color presets to use
LIGHT_PRESET_NAME="MyEverForest (Dark)"
DARK_PRESET_NAME="Dracula+"

#LIGHT_PRESET_NAME="Dracula"
#DARK_PRESET_NAME="Dracula+"

# Profiles to update
PROFILE_EXCLUDE=["pulldown-terminal","UNIX manpage"]
TAG_EXCLUDE=[]

last_mode=""

async def detect_dark_mode():
  command = 'nice -n 15 defaults read -g AppleInterfaceStyle 2>/dev/null'
  proc = await asyncio.create_subprocess_shell(
      command,
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.PIPE)
  stdout, stderr = await proc.communicate()
  #print('[{!r} exited with {}]'.format(command, proc.returncode))

  if stdout:
    detected_mode=stdout.decode('ascii').rstrip()
    return True if detected_mode == 'Dark' else False
  if stderr:
    print('[stderr] {}'.format(stderr.decode('ascii').rstrip()))
  return False

async def set_colors(connection, profile, preset):
  delay = random.randint(1, 3)
  await asyncio.sleep(delay)

  running_tasks.append(profile.async_set_color_preset(preset))

async def set_transparency(connection, transparency_level):
  app = await iterm2.async_get_app(connection)
  window = app.current_window
  if (window):
    session = window.current_tab.current_session
    change = iterm2.LocalWriteOnlyProfile()

    change.set_transparency(transparency_level)
    setting_task = await session.async_set_profile_properties(change)
    #running_tasks.append(setting_task)

async def set_blur(connection, blur_pct):
  app = await iterm2.async_get_app(connection)
  window =app.current_window

  if (window):
    session = window.current_tab.current_session

    max_blur_radius = 30
    blur_radius = blur_pct * max_blur_radius

    change = iterm2.LocalWriteOnlyProfile()
    change.set_blur_radius(blur_radius)

    session = app.current_terminal_window.current_tab.current_session
    setting_task = await session.async_set_profile_properties(change)
    #running_tasks.append(setting_task)

async def change_profiles(connection,preset_name):
  for profile in (await iterm2.PartialProfile.async_get(connection)):
    should_skip = False

    preset  = await iterm2.ColorPreset.async_get(connection, preset_name)
    for tag in TAG_EXCLUDE:
      if tag in profile.name:
        should_skip = True

    if profile.name not in PROFILE_EXCLUDE and not should_skip:
      print("[set_colors] «start-thread» Setting the {} preset for {}".format(preset_name.lower(), profile.name.lower()))
      change_task =  set_colors(connection, profile, preset)
      running_tasks.append(change_task)
    else:
      print("[set_colors] skipping profile {}".format(profile.name))

async def main(connection):
  global last_mode
  global detected_mode
  global running_tasks
  global app

  app = await iterm2.async_get_app(connection)
  running_tasks = []

  while True:
    is_dark = await detect_dark_mode()
    if is_dark and last_mode != "Dark":
      await change_profiles(connection, DARK_PRESET_NAME)
      last_mode="Dark"
    elif not is_dark and last_mode != "Light":
        await change_profiles(connection, LIGHT_PRESET_NAME)
        last_mode="Light"

    await set_transparency(connection, (0.15 if is_dark else 0.20) )
    await set_blur(connection, 0.25) #,  (0.25 if is_dark else 0.25))

    if (len(running_tasks) > 0):
      print ("Executing threads")
      asyncio.gather(*running_tasks)
      running_tasks.clear()
      print("[main] All threads have completed")

    await asyncio.sleep(DETECTION_DELAY_SECONDS)


iterm2.run_forever(main)

# vim: set ts=2 sts=2 sw=2 et :
