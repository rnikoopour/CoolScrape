import bs4
import requests
import sys
import string
import urllib
import thread
from threading import *

console = "mame"
console_list = ["atari2600", "atari5200", "atari7800", "atarijaguar", "atarilynx", "gba", "gbc", "mame" "neogeopocket", "nes", "n64", "nds", "dc", "genesis", "saturn", "psx", "psp", "snes"]
coolrom_url = "http://coolrom.com"
download_page_url = coolrom_url + "/dlpop.php?id="
lock = Lock()
num_threads = 0


def get_game_id(game):
    game_url =  coolrom_url + game.find('a').get('href')
    game_page = requests.get(game_url)
    game_soup = bs4.BeautifulSoup(game_page.content)
    page_url = game_soup.find('meta', {'property':'og:url'})['content']
    game_id_start = page_url.find(console + '/') + len(console + '/')
    game_id_end = page_url.rfind('/')
    game_id = page_url[game_id_start:game_id_end]
    return game_id

def get_download_url(download_soup):
    script_text = download_soup.find('script').text
    download_url_start = script_text.find('action=') + len('action=')
    download_url_end = script_text.find("><input")
    download_url = script_text[download_url_start:download_url_end].strip('"')
    return download_url

def get_file_name(download_soup):
    script_text = download_soup.find('script').text
    file_name_start = script_text.find("<b>") + len("<b>")
    file_name_end = script_text.find("</b>")
    file_name = script_text[file_name_start:file_name_end]
    return file_name

def download_game(download_url, url_cookies, file_name):
    global num_threads
    lock.acquire()
    num_threads += 1
    lock.release()
    
    try:
        print "Downloading: " + file_name
        actual_download = requests.post(download_url, cookies=url_cookies)
        game_file = open(file_name, 'w')
        game_file.write(actual_download.content)
        game_file.close()
    except:
        print "Error Downloading: " + file_name
    
    lock.acquire()
    num_threads -= 1
    lock.release()
       

def main():
    global num_threads
    num_threads = 0
    
    rom_letters = list(string.ascii_lowercase)
    # 0 is used to represent games begining with numbers
    rom_letters.insert(0, '0')
    
    for letter in rom_letters:
        rom_list_page = requests.get(coolrom_url + "/roms/" + console + '/' + letter)
        rom_list_soup = bs4.BeautifulSoup(rom_list_page.content)
    
        game_list = rom_list_soup.find_all('div', class_='USA')
    
        for game in game_list:
            game_id = get_game_id(game)
        
            download_page = requests.get(download_page_url + game_id)
            download_soup = bs4.BeautifulSoup(download_page.content)
            download_url = get_download_url(download_soup)
            file_name = get_file_name(download_soup)
            
            while num_threads > 10:
                pass
            
            thread.start_new_thread(download_game, (download_url, download_page.cookies, file_name))
            
    while num_threads > 0:
        pass
        
if __name__ == '__main__':
    main()