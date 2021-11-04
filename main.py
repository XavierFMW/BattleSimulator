from random import randint
import pygame 
import sys
import csv


 ### Defining Global Variables ###

WINDOW_WIDTH, WINDOW_HEIGHT = 1378, 963
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Battle Simulator")

NATIONS = []
LANDS = []
TURNS = []

TOTAL_LOSSES = False
TURNS_PER_SEC = 5    # The number of game turns per second.

MAP = pygame.image.load("map.png")


 ### Defining Key Classes ###

class land:
    """
    Represents a piece of land on the map. May swap hands between nations.

    Attributes:
        nation (nation): The nation which currently owns this piece of land.
        image (Surface): The image representing the nation on the map.
        coords (tuple): A tuple which holds the x and y values for the image's position on the map.

        n, s, e, w, etc. (land): The pieces of land directly next to this piece geographically. Names based on cardinal and ordinal directions.
    """

    def __init__(self, nation, image, coords, ne=None, n=None, nw=None, w=None, sw=None, s=None, se=None, e=None):
        
        self.nation = nation
        self.image = image
        self.coords = coords

        self.ne = ne
        self.n = n
        self.nw = nw
        self.w = w
        self.sw = sw
        self.s = s
        self.se = se
        self.e = e

        # I physically cannot express how much I hate this code. First the program checks to make sure each direction is actually filled with
        # another 'land' node, then sets the direction of each node relative to itself as itself. For example, the node to the west of this 
        # node would have this node set as it's '.east' attribute, as to keep continuity between nodes. Issue is, you can't edit these 
        # attributes in place by looping through a list. I apologize to anyone who has to read this, good luck.

        if self.ne:
            self.ne.sw = self
        
        if self.n:
            self.n.s = self
        
        if self.nw:
            self.nw.se = self
        
        if self.w:
            self.w.e = self
        
        if self.sw:
            self.sw.ne = self
        
        if self.s:
            self.s.n = self
        
        if self.se:
            self.se.nw = self
        
        if self.e:
            self.e.w = self


class nation:
    """
    A nation within the game. Attributes given based on each line in the "nations.csv" file.

    Attributes:
        name (str): The full name of the nation.
        name_stem (str): The short-hand name for the nation, ie "Britain, Germany."
        flag (Surface): An image of the nation's real world flag.
        logo (Surface): A logo representing the nation's ideology. Listed as None until an ideology is chosen.
        size (int): A number from 1-3 representing the nations military strength.
        ideology (chr): A character represening the nation's ideology. Listed as None until an ideology is chosen.
        self.allies (list): A list of all of a nation's allies.
        starting_land (land): The land a nation's begins with in the game. 
    """

    def __init__(self, name, size, image, coords, ne, n, nw, w, sw, s, se, e):
        
        self.name = name
        self.name_stem = name

        flag_path = "flags\\" + name.lower().replace(" ", "_") + ".png"
        self.flag = pygame.image.load(flag_path)
        self.logo = None

        self.size = size
        self.ideology = None

        self.allies = []

        self.starting_land = land(self, image, coords, ne, n, nw, w, sw, s, se, e)
        LANDS.append(self.starting_land)


 ### Defining Key Functions ###

def create_nations():
    """
    Populates the NATIONS list based on the information within "nations.csv"
    """

    with open("nations.csv", "r") as nations:

        reader = csv.reader(nations)
        for nation_info in reader:
            
            # line: NAME, SIZE, COORDS_X, COORDS_Y, NORTH EAST, NORTH, NORTH WEST, WEST, SOUTH WEST, SOUTH, SOUTH EAST, EAST

            file_path = "nation_images\\" + nation_info[0].lower().replace(" ", "_") + ".png"
            coords = (int(nation_info[2]), int(nation_info[3]))

            image = pygame.image.load(file_path)

            ne = None
            n = None
            nw = None
            w = None
            sw = None
            s = None
            se = None
            e = None
            
            if nation_info[4] in [x.name for x in NATIONS]:
                ne = [x for x in NATIONS if x.name == nation_info[4]][0].starting_land

            if nation_info[5] in [x.name for x in NATIONS]:
                n = [x for x in NATIONS if x.name == nation_info[5]][0].starting_land

            if nation_info[6] in [x.name for x in NATIONS]:
                nw = [x for x in NATIONS if x.name == nation_info[6]][0].starting_land

            if nation_info[7] in [x.name for x in NATIONS]:
                w = [x for x in NATIONS if x.name == nation_info[7]][0].starting_land

            if nation_info[8] in [x.name for x in NATIONS]:
                sw = [x for x in NATIONS if x.name == nation_info[8]][0].starting_land

            if nation_info[9] in [x.name for x in NATIONS]:
                s = [x for x in NATIONS if x.name == nation_info[9]][0].starting_land

            if nation_info[10] in [x.name for x in NATIONS]:
                se = [x for x in NATIONS if x.name == nation_info[10]][0].starting_land

            if nation_info[11] in [x.name for x in NATIONS]:
                e = [x for x in NATIONS if x.name == nation_info[11]][0].starting_land

            NATIONS.append(nation(nation_info[0], int(nation_info[1]), image, coords, ne, n, nw, w, sw, s, se, e))


def fight_war(first_nation):
    """
    Plays out a war between 2 nations.

    Arguments:
        first_nation: The nation declaring war.

    Notes:
        A target nation is chosen based on the neighbors of the nations starting land.

        The global attribute TOTAL_LOSSES changes the outcome of wars. If TOTAL_LOSSES is disabled, the nation which loses the war will lose only 1
        point of military strength and the targetted land, still remaining in the game.

        If TOTAL_LOSSES is enabled, the losing nation will be removed from the game, with all of their land and strength being given to the winning nation. 
    """

    target = first_nation.starting_land
    while target.nation == first_nation:

        targets = [target.ne, target.n, target.nw, target.w, target.sw, target.s, target.se, target.e]
        target = targets[randint(0, 7)]

        while target == None:

            targets.remove(target)

            try:
                target = targets[randint(0, (len(targets) - 1))]

            except ValueError:

                target == first_nation.starting_land
                break
    
    second_nation = target.nation

    first_strength = first_nation.size
    for ally in first_nation.allies:
        first_strength += ally.size

    second_strength = second_nation.size
    for ally in second_nation.allies:
        second_strength += ally.size

    armies = []
    armies.extend([first_nation for x in range(0, first_strength)])
    armies.extend([second_nation for x in range(0, second_strength)])

    victor = armies[randint(0, len(armies) - 1)]
    loser = [x for x in armies if x != victor][0]


    if TOTAL_LOSSES:
    
    ### Losses are total ###

        victor.size += loser.size

        for land in [x for x in LANDS if x.nation == loser]:
            land.nation = victor

        for ally in loser.allies:
            ally.allies.remove(loser)

        print(f"{first_nation.name} declared war against {second_nation.name}, {victor.name_stem} won the battle.")

        NATIONS.remove(loser)
        del loser
    

    else:

    ### Losses are partial ###

        victor.size += 1
        loser.size -= 1

        target.nation = victor

        print(f"{first_nation.name} declared war against {second_nation.name}, {victor.name_stem} won the battle.")

        if len([x for x in LANDS if x.nation == loser]) == 0 or loser.size <= 0:

            for land in [x for x in LANDS if x.nation == loser]:
                land.nation = victor

            for ally in loser.allies:
                ally.allies.remove(loser)

            print(f"{first_nation.name} declared war against {second_nation.name}, {victor.name_stem} won the battle.")

            NATIONS.remove(loser)
            del loser


def add_ally(first_nation):
    """
    Establishes alliances between 2 randomly chosen nations. Unlike war, the nations don't have to be geographically close.
    """

    try:
        second_nation = [x for x in NATIONS if x != first_nation and x not in first_nation.allies][randint(0, len(NATIONS) - (2 + len(first_nation.allies)))]

    except ValueError:
        return

    if first_nation.ideology and second_nation.ideology and first_nation.ideology != second_nation.ideology:
        
        print(f"{first_nation.name} tried to form an alliance with {second_nation.name}, but negotiations failed.")
        return

    else:
        
        first_nation.allies.append(second_nation)
        second_nation.allies.append(first_nation)

        print(f"{first_nation.name} and {second_nation.name} have formed and alliance.")


def change_ideology(acting_nation):
    """
    Changes a nation's ideology and increases their strength by 1. If a nation is a different ideology than another nation, they cannot ally. If 
        the nation is already allies with a nation of a different ideology, that alliance will break.
    """

    # TODO have nations show logos based on ideology

    ideologies = ["D", "C", "M", "F"]
    ideology = ideologies[randint(0, 3)] 

    if ideology == acting_nation.ideology:
        return

    else:

        announcements = {
            "D": f"The people of {acting_nation.name_stem} have gained political freedom, as {acting_nation.name_stem} becomes a Democracy!",
            "C": f"The workers of {acting_nation.name_stem} have broken their chains, as {acting_nation.name_stem} becomes Communist!",
            "M": f"{acting_nation.name_stem} has returned to Feudalism, as {acting_nation.name_stem} becomes Monarchist!",
            "F": f"A dictator has risen to power in {acting_nation.name_stem}, as {acting_nation.name_stem} becomes Fascist!"
        }

        names = {
            "D": f"The Republic of {acting_nation.name_stem}",
            "C": f"The Workers' Union of {acting_nation.name_stem}",
            "M": f"The Kingdom of {acting_nation.name_stem}",
            "F": f"The Fascist State of {acting_nation.name_stem}"
        }

        logos = {
            "D": "logos\\democracy.png",
            "C": "logos\\communism.png",
            "M": "logos\\monarchy.png",
            "F": "logos\\fascism.png",
        }

        acting_nation.name = names[ideology]
        acting_nation.ideology = ideology
        acting_nation.logo = pygame.image.load(logos[ideology])

        acting_nation.size += 1

        announcement = announcements[ideology]
        lost_allies = ""

        for ally in acting_nation.allies:
            
            if ally.ideology and ally.ideology != ideology:

                ally.allies.remove(acting_nation)
                acting_nation.allies.remove(ally)
                lost_allies += f"{ally.name}, "

        if len(lost_allies) > 0:
            announcement += f" They have lost favor with " + lost_allies[:-2] + "!"

        print(announcement)


def draw_country(nation, original, coords):
    """
    Draws a specific piece of land on the map, filled in with the flag of the nation it belongs to.
    """

    image_width, image_height = original.get_size()
    colored = pygame.Surface((image_width, image_height))

    flag = pygame.transform.scale(nation.flag, colored.get_size())
    colored.blit(flag, (0, 0))

    colored.set_colorkey((0, 0, 0))
    colored.blit(original, (0, 0))

    window.blit(colored, coords)


def draw_logos():
    """
    Draws the logos of all nations which posses an ideology. 
    """

    for nation in [x for x in NATIONS if x.logo != None]:

        if nation.starting_land.nation == nation:
            land = nation.starting_land
        else:
            land = [x for x in LANDS if x.nation == nation][0]

        image_width, image_height = land.image.get_size()
        nation_x, nation_y = land.coords

        logo = nation.logo
        logo_width, logo_height = logo.get_size()

        coords = (nation_x + (image_width // 2) - (logo_width // 2), nation_y + (image_height // 2) - (logo_height // 2))
        window.blit(logo, coords)


def draw_map():
    """
    Renders that nations and ideology logos after each turn.
    """

    window.blit(MAP, (0, 0))

    for land in LANDS:
        draw_country(land.nation, land.image, land.coords)

    draw_logos()

    pygame.display.update()


def run_turn():
    """
    Randomly chooses 1 of 3 possible actions, then randomly picks a nation to perform it.
    """

    actions = [fight_war, add_ally, change_ideology]
    action = actions[randint(0, len(actions) - 1)]

    if len(TURNS) >= 3:
        recent_actions = TURNS[-5:] 
        
        if fight_war not in recent_actions:
            action = fight_war

        elif len([x for x in recent_actions if x == action]) >= 3:
            action = [x for x in actions if x != action][randint(0, len(actions) - 2)]

    TURNS.append(action)
    acting_nation = NATIONS[randint(0, len(NATIONS) - 1)]
    action(acting_nation)   
    draw_map()


def main():
    """
    Runs turns until only 1 nations remains in the game. That nation is the winner.
    """

    clock = pygame.time.Clock()
    
    create_nations()
    draw_map()

    while len(NATIONS) > 1:
        clock.tick(TURNS_PER_SEC)

        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                sys.exit()

        run_turn()

    print(f"\n{NATIONS[0].name} has won the game!\n")


if __name__ == "__main__":
    main()
