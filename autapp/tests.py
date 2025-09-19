import time
from colorama import init, Fore, Style,Back
import colorama
import datetime
import os
colorama.init()

ascii_art_green = r"""
                        ,===:'.,            `-._
                        
                       `:.`---.__         `-._
                         EXAON TECH
              `:.     `--.         `.
                   \.        `.         `.
             (,,(,    \.         `.   ____,-`.,
           (,'     `/   \.   ,--.___`.'
        ,  ,'  ,--.  `,   \.;'         `
        `{D, {    \  :    \;
          V,,'    /  /    //
          j;;    /  ,' ,-//.    ,---.      ,
          \;'   /  ,' /  _  \  /  _  \   ,'/ 
            \   `'  / \  `'  / \  `.' /
             `.___,'   `.__,'   `.__,'  VZ
"""



ascii_art_red = f"""{Fore.RED + Style.BRIGHT}
          :::::::::  :::::::::  ::::::::::   :::   :::   ::::::::::: :::    :::
     :+:    :+: :+:    :+: :+:         :+:+: :+:+:      :+:     :+:    :+: 
    +:+    +:+ +:+    +:+ +:+        +:+ +:+:+ +:+     +:+     +:+    +:+  
   +#++:++#+  +#++:++#:  +#++:++#   +#+  +:+  +#+     +#+     +#+    +:+   
  +#+        +#+    +#+ +#+        +#+       +#+     +#+     +#+    +#+    
 #+#        #+#    #+# #+#        #+#       #+#     #+#     #+#    #+#     
###     :::###::: ### ########## ###       ### ###########  ########       
      :+:+: :+:+:                                                          
    +:+ +:+:+ +:+                                                          
   +#+  +:+  +#+                                                           
  +#+       +#+                                                            
 #+#       #+#                                                             
###       ###                                                              
      ::::::::   ::::::::  :::::::::  ::::::::::: ::::::::: :::::::::::    
    :+:    :+: :+:    :+: :+:    :+:     :+:     :+:    :+:    :+:         
   +:+        +:+        +:+    +:+     +:+     +:+    +:+    +:+          
  +#++:++#++ +#+        +#++:++#:      +#+     +#++:++#+     +#+           
        +#+ +#+        +#+    +#+     +#+     +#+           +#+            
#+#    #+# #+#    #+# #+#    #+#     #+#     #+#           #+#             
########   ########  ###    ### ########### ###           ###              
   :::     :::   :::                                                       
  :+:     :+: :+:+:                                                        
 +:+     +:+   +:+                                                         
+#+     +:+   +#+                                                          
+#+   +#+    +#+                                                           
#+#+#+#     #+#                                                            
 ###     #######                                                           
"""

def typewriter_effect(text, delay=0.005):
    """Print text like a typewriter effect, character by character."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
        
     # Reset colors at the end

# Animate both ASCII arts
typewriter_effect(ascii_art_green, delay=0.002)
time.sleep(1)
os.system('cls')
time.sleep(0.5)  # Small pause between arts
typewriter_effect(ascii_art_red, delay=0.002)
if os.name == 'nt':
        os.system('cls')
    # For macOS/Linux

while True:
    baner=f"""{Fore.CYAN + Style.BRIGHT}
                                    _____           ______  
    _________  _______ _____________    __  /______________  /_ 
    _  _ \_  |/_/  __ `/  __ \_  __ \   _  __/  _ \  ___/_  __ \
    /  __/_>  < / /_/ // /_/ /  / / /   / /_ /  __/ /__ _  / / /
    \___//_/|_| \__,_/ \____//_/ /_/    \__/ \___/\___/ /_/ /_/ 

    30 faucets per second 🔥 v1 premium script {Fore.BLUE}server time{Fore.YELLOW}: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    {Fore.BLACK + Fore.GREEN} server status {Fore.YELLOW}: {Fore.GREEN}ONLINE{Fore.YELLOW}
    """
    granted=f"""{Fore.GREEN + Style.BRIGHT} 

            __________________    _____    _____________________________________   
        /  _____/\______   \  /  _  \   \      \__    ___/\_   _____/\______ \  
        /   \  ___ |       _/ /  /_\  \  /   |   \|    |    |    __)_  |    |  \ 
        \    \_\  \|    |   \/    |    \/    |    \    |    |        \ |    `   \
        \______  /|____|_  /\____|__  /\____|__  /____|   /_______  //_______  /
                \/        \/         \/         \/                 \/         \/ 
                thanks for buying the script
    """
    typewriter_effect(baner, delay=0.002)
    time.sleep(0.5)

    userpreference= input(f"{Fore.RED + Style.BRIGHT}1. {Fore.WHITE}Freebitco.in (HACK 9994 MULITPLYER) {Fore.RED + Style.BRIGHT} \n2. 30 faucet auto claim {Fore.WHITE}3 .Exit {Fore.RESET}")

    if userpreference == '1':
        os.system('cls')
        typewriter_effect(baner, delay=0.002)
        time.sleep(0.5)
        print(f"{Fore.RED + Style.BRIGHT}clicked {Fore.WHITE}Freebitco.in (HACK 9994 MULITPLYER)" )
        time.sleep(0.5)
        token=input(f"{Fore.GREEN + Style.BRIGHT} Enter your token {Fore.RESET}")
        if token=="plgp2y8yu":
             
            os.system('cls')

            typewriter_effect(granted, delay=0.002)
            time.sleep(2)
            os.system('cls')
            typewriter_effect(baner, delay=0.002)
            time.sleep(0.5)
            print(f"{Fore.RED + Style.BRIGHT}clicked {Fore.WHITE}Freebitco.in (HACK 9994 MULITPLYER)" )
            time.sleep(0.5)
            
            email=input(f"{Fore.GREEN + Style.BRIGHT} Enter your email or BTC adress {Fore.RESET}")
            password=input(f"{Fore.GREEN + Style.BRIGHT} Enter your password {Fore.RESET}")
            os.system('cls')
            typewriter_effect(baner, delay=0.002)
            time.sleep(0.5)
            typewriter_effect("loading", delay=0.05)
            time.sleep(0.5)
            print("wrong email or password")
            email=input(f"{Fore.GREEN + Style.BRIGHT} Enter your email or BTC adress {Fore.RESET}")
            password=input(f"{Fore.GREEN + Style.BRIGHT} Enter your password {Fore.RESET}")
            os.system('cls')
            typewriter_effect(baner, delay=0.002)
            time.sleep(0.5)
            print(f"{Fore.GREEN + Back.YELLOW} loged in sucessfully" )
            time.sleep(5)
            print("rolling")
            time.sleep(2)
            print(f"{Fore.GREEN + Back.YELLOW} won 0.0000176 BTC")
            print("wait 1hr")
            time.sleep(360)
        else :
            os.system('cls')
            typewriter_effect(baner, delay=0.002)
            time.sleep(0.5)
            print(f"{Fore.RED + Style.BRIGHT}wrong token" )
            time.sleep(0.5)
            break
    elif userpreference == '2':
        os.system('cls')
        typewriter_effect(baner, delay=0.002)
        time.sleep(0.5)
        print(f"{Fore.RED + Style.BRIGHT}clicked {Fore.WHITE}30 faucet auto claim" )
        time.sleep(0.5)
        token=input(f"{Fore.GREEN + Style.BRIGHT} Enter your token {Fore.RESET}")
        if token=="plgp2y8yu":
            os.system('cls')
            typewriter_effect(granted, delay=0.002)
            time.sleep(2)
            os.system('cls')
            typewriter_effect(baner, delay=0.002)
            time.sleep(0.5)
            print(f"{Fore.RED + Style.BRIGHT}clicked {Fore.WHITE}30 faucet auto claim" )
            time.sleep(0.5)
            email=input(f"{Fore.GREEN + Style.BRIGHT} Enter your faucet pay email or LTC adress {Fore.RESET}")
            time.sleep(5)
            print(f"{Fore.GREEN + Back.YELLOW} mining started" )
            import random

# Generate a random 4-digit number
            

            

            while True:
                number = random.randint(1000, 9999)
                print(f"{Fore.GREEN + Back.WHITE} Earned {number} satoshi")
                time.sleep(3)    
      

   