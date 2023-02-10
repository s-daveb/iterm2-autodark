#!/usr/bin/env python3

import asyncio
import iterm2
import sys

# Duration between checks
DURATION=30

# Color presets to use
LIGHT_PRESET_NAME="Everforest_soft_light"
DARK_PRESET_NAME="Everforest_hard_dark"

# Profiles to update
PROFILE_EXCLUDE=[]
TAG_EXCLUDE=["tmux"]

async def dark_mode():
  command = 'defaults read -g AppleInterfaceStyle 2>/dev/null'
  proc = await asyncio.create_subprocess_shell(
      command,
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.PIPE)
  stdout, stderr = await proc.communicate()
  #print('[{!r} exited with {}]'.format(command, proc.returncode))

  if stdout:
    return True if stdout.decode('ascii').rstrip() == 'Dark' else False
  if stderr:
    print('[stderr] {}'.format(stderr.decode('ascii').rstrip()))
  return False

async def set_colors(connection, preset_name):
  print("[set_colors] Setting the {} preset...".format(preset_name.lower()))
  preset = await iterm2.ColorPreset.async_get(connection, preset_name)
  for profile in (await iterm2.PartialProfile.async_get(connection)):
    should_skip = False
    for tag in TAG_EXCLUDE:
        if profile.name.contains(tag):
            should_skip = True

    if profile.name not in PROFILE_EXCLUDE and not should_skip:
        await profile.async_set_color_preset(preset)
        await asyncio.sleep(10)

async def main(connection):
  while True:
    is_dark = await dark_mode()
    await asyncio.sleep(1)
    if is_dark:
      await set_colors(connection, DARK_PRESET_NAME)
    else:
      await set_colors(connection, LIGHT_PRESET_NAME)
    await asyncio.sleep(DURATION)

iterm2.run_forever(main)
