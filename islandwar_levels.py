
levels = {#"Levelnr":{"Islandname":[((pos1), (Color1),ships, ((pos2), (Color2),Ships2),...],      
           "-4":{"Main_islands":[((400,-400),(0,255,0),1),((1030,-400),(255,0,0),0)],#...............
                "Iron_islands":[],                                                   #....M...eM.....
                "Wood_islands":[],                                                   #...............
                "Ship_islands":[]},
           "-3":{"Main_islands":[((300,-400),(0,255,0),3),((1130,-400),(255,0,0),0)],#.....I......
                "Iron_islands":[((715,-200),(255,0,0),0)],                           #..M.....eM..
                "Wood_islands":[((715,-600),(255,0,0),0)],                           #.....W......
                "Ship_islands":[]},
           "-2":{"Main_islands":[((300,-400),(0,255,0),0),((1130,-400),(255,0,0),0)],#....pI......
                "Iron_islands":[((715,-200),(0,255,0),0)],                           #..M.pS..eM..
                "Wood_islands":[((715,-600),(0,255,0),0)],                           #....pW......
                "Ship_islands":[((715,-400),(0,255,0),0)]},
           "-1":{"Main_islands":[((300,-400),(0,255,0),3),((1130,-400),(255,0,0),2)],#.....I......
                "Iron_islands":[((715,-200),(0,0,255),0)],                           #..M.....eM..
                "Wood_islands":[((715,-600),(0,0,255),0)],                           #.....W......
                "Ship_islands":[]},
           "0":{"Main_islands":[((300,-400),(0,255,0),3),((1130,-400),(255,0,0),3)],#....pI.....
                "Iron_islands":[((715,-200),(0,255,0),0)],                          #..M..S..eM..
                "Wood_islands":[((715,-600),(0,255,0),0)],                          #....pW......
                "Ship_islands":[((715,-400),(0,0,255),0)]},
           "1":{"Main_islands":[((300,-400),(0,255,0),3),((1130,-400),(255,0,0),3)],#I...........I
                "Iron_islands":[((150,-200),(0,0,255),0),((1280,-600),(0,0,255),0)],#..M...S..eM.. 
                "Wood_islands":[((150,-600),(0,0,255),0),((1280,-200),(0,0,255),0)],#W...........W
                "Ship_islands":[((715,-400),(0,0,255),0)]},
           "2":{"Main_islands":[((200,-400),(0,255,0),5),((1230,-400),(255,0,0),5)],#....W.....
                "Iron_islands":[((715,-600),(0,0,255),0)],                          #M...S...eM
                "Wood_islands":[((715,-200),(0,0,255),0)],                          #....I.....
                "Ship_islands":[((715,-400),(0,0,255),0)]},
           "3":{"Main_islands":[((715,-250),(0,255,0),5),((715,-550),(255,0,0),5)], #I...M...I
                "Iron_islands":[((200,-100),(0,0,255),0),((1230,-100),(0,0,255),0)],#..S...S..
                "Wood_islands":[((200,-700),(0,0,255),0),((1230,-700),(0,0,255),0)],#W..eM...W
                "Ship_islands":[((476,-400),(0,0,255),0),((952,-400),(0,0,255),0)]},
           "4":{"Main_islands":[((150,-400),(0,255,0),7),((1280,-400),(255,0,0),9)],                        #..I.I.I..
                "Iron_islands":[((515,-200),(0,0,255),0),((715,-200),(0,0,255),0),((915,-200),(0,0,255),0)],#M...S..eM
                "Wood_islands":[((515,-600),(0,0,255),0),((715,-600),(0,0,255),0),((915,-600),(0,0,255),0)],#..W.W.W..
                "Ship_islands":[((715,-400),(0,0,255),0)]},
           "5":{"Main_islands":[((200,-400),(0,255,0),3),((1230,-400),(0,255,0),3)],#pI... eI.
                "Iron_islands":[((300,-200),(0,255,0),1),((1130,-200),(0,255,0),1)],#M...S..eM
                "Wood_islands":[((300,-600),(0,255,0),1),((1130,-600),(0,255,0),1)],#pW....eW.
                "Ship_islands":[((715,-400),(0,0,255),0)]}
         }

level_descriptions = {"-4":["You are the leader of the island with a green ring around it.", "Your aim is to conquer all the enemy islands on the map.", "Click on your island to select it, then on the enemy island to send a ship."],
                      "-3":["On this map, there are three enemy islands. Conquer every one of them."],
                      "-2":["You can build more ships in the shipyard.", "For every new ship, you first need 5 pieces of iron and wood."],
                      "-1":["The enemy can have ships too. If you want to win, you have to defeat them", "and take all their islands."],
                      "0": ["If you want to win this map, you'll have to collect resources and build more ships.", "Don't let the enemy take the resource islands or the shipyard!"],
                      "1": ["It is time for your first real battle. Good luck!"],
                      "2": [],
                      "3": [],
                      "4": [],
                      "5": [],
                      }
                      

#
#
#

def create_sprites(level):
    #islands = type_player:[pos,ship
    islands = levels[str(level)]
    return islands
    #print(Hello world)
    #levels[level][0]
