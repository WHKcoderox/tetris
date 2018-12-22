# Tetris
I partially follow a guide on YouTube and this is the result.

## How to install pygame, a library for making games with Python
### Windows Users
Follow this link: https://www.youtube.com/watch?v=AdUZArA-kZw
---
### Mac Users
*Note: this guide is dated at 22/12/2018. For newer guides, check Homebrew's official website*
Install Homebrew :
```bash
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
Once that is done, use Homebrew to install required packages:
```Bash
brew upgrade sdl sdl_image sdl_mixer sdl_ttf portmidi
```
If you don't want to install pygame to the computer and instead create a python project and have pygame as a dependency, you may perform these additional steps:
```bash
python3.6 -m venv anenv
. ./anenv/bin/activate
```
If you just want to install pygame, just perform this step. Use pip3 if pip is not recognised.
```bash
pip install https://github.com/pygame/pygame/archive/master.zip
```
