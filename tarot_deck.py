'''
Created on May 10, 2021

@author: Fred
'''
from PIL import Image
from datetime import datetime
import random, os

class tdeck():
    '''
    classdocs
    '''

    def __init__(self, card_dir='./card_images/', invert=True, invert_chance=25):
        '''
        Args
        ----
        card_dir : str
            the directory in which the cards and other files are contained within.
        invert : boolean
            defaults to True. If it is True, checks to see if the directory
            contains a file named 'card_meanings_inverted.txt'
            If so, it will potentially invert cards as they are drawn.
        invert_chance : int
            defaults to 25. The chance a card will be inverted.

        '''
        self.card_dir = card_dir
        self.card_names = open(card_dir+'card_names.txt', 'r').read().split('\n')
        self.deck = list(range(0,len(self.card_names))) #the deck of cards, numbered from 0 to 77
        random.shuffle(self.deck)
        self.hand = []
        if invert:
            if 'card_meanings_inverted.txt' in os.listdir(card_dir):
                self.invert = True
                self.invert_chance = invert_chance
            else:
                self.invert = False
                self.invert_chance = 0
        else:
            self.invert = False
            self.invert_chance = 0
    
    def draw(self):
        '''Draws a card, and then adds that card to the hand.
        We always know which card was drawn last, because it will always be
        at self.hand[-1]
        '''
        drawn_card = int(self.deck.pop())
        if self.invert: #do we potentially invert cards?
            if random.randint(1,100) < self.invert_chance:
                invert = 1
            else:
                invert = 0
        else:
            invert = 0
        self.hand.append((drawn_card, invert))
        return self.card_names[drawn_card]
    
    def reset_hand(self):
        self.hand = []
        self.deck = list(range(0,len(self.card_names)))
        
    def get_name(self, index=-1):
        card = self.hand[index]
        if not card[1]:
            return self.card_names[self.hand[index][0]]
        else:
            return self.card_names[self.hand[index][0]]+", inverted"
    
    def get_desc(self, index=-1):
        card = self.hand[index]
        if not card[1]: #if it's not inverted
            desc_f = 'card_meanings.txt'
        elif card[1]: #if it is inverted
            desc_f = 'card_meanings_inverted.txt'
        card_meanings = open(self.card_dir+desc_f, 'r').read().split('\n')
        return card_meanings[card[0]]
        
class card_table():
    '''
    classdocs
    '''
    
    def __init__(self, owner, deck, spread='Single', invert=True):
        '''
        Args
        ----
        owner : str
            the owner of the table, used mostly for file naming purposes
        deck : tdeck
            a tdeck object. the tdeck class is defined above in this file.
        spread : str
            a string, representing the various allowed tarot spreads.
            spread defaults to 'Single', representing a single card.
            Allowed spreads are as follows:
                Single - 1 card is drawn and shown.
                
        Each of the above is created as an attribute of the table class.
        Additionally, the following attributes are created using this information
        when the class is instantiated:
            draw_max : int
                the maximum number of cards to be drawn, checked with len(self.deck.hand)
                decided by the chosen spread.
            table : Image
                the baseline image, representing the table on which the cards
                are placed, using PIL's Image class. The dimensions
                of this image are decided by the spread.
            cross_loc : tuple
                a tuple of x,y coordinates for use on the image self.table
                only used for the cross spread.
        '''
        valid_spread = {'Single' : 1,
                        'Draw' : 3,
                        'Seven' : 7,
                        'Cross' : 10
                        }
        self.owner = str(owner)
        self.deck = deck
        if spread.title() in valid_spread:
            self.spread = spread.title()
        else:
            self.spread='Single'
        self.draw_max = valid_spread[self.spread]
        self.table = self.construct_table()
        self.cross_loc = (0,0)
    
    def construct_table(self):
        im = Image.open(self.deck.card_dir + "0.jpg")
        im_x = im.size[0]
        im_y = im.size[1]
        if self.spread == 'Single':
            return Image.new('RGB', (im_x, im_y), 'Purple')
        elif self.spread == 'Cross':
            '''
            In a cross spread, the cards will be half size to save space.
            We increase the expected size by 25, in order to allow for a
            nice visual gap.
            The cards will be placed 4 across, with 2.5 up and 2.5 down.
            Or a total width of card-size * 4 and height of card size * 5
            '''
            im_max = max([im_x, im_y])
            im_size = ((im_max*4)+50, (im_max*4)+50)
            return Image.new('RGB', im_size, 'Purple')
        else:
            im_x = ((im_x + 25) * self.draw_max)-25
            im_size = (im_x, im_y)
            return Image.new('RGB', im_size, 'Purple')
        
    def next_step(self):
        if len(self.deck.hand) < self.draw_max: #if we haven't drawn all cards yet
            self.deck.draw()
            drawn_card = self.deck.hand[-1]
            self.place_card(drawn_card)
            return self.deck.get_name()
        else: #if all cards are drawn
            time = datetime.now()
            file_name = self.owner + "_" + time.strftime('%d-%m-%y-%H-%M-%S')+"_"+self.spread + ".jpg"
            self.table.save(self.deck.card_dir+'/complete_imgs/'+file_name)
            return self.deck.card_dir+'/complete_imgs/'+file_name
            
    def place_card(self, card):
        card_im = Image.open(self.deck.card_dir + str(card[0]) + ".jpg")
        inverted = card[1]
        if self.spread != "Cross": #A cross spread requires some weirdness
            if len(self.deck.hand) == 1: #if there is only one card placed...
                location = (0,0)
            else: #otherwise, we slide it over to an empty spot.
                x_coor = (card_im.size[0] + 25) * (len(self.deck.hand)-1)
                location = (x_coor, 0)
        else:
            location = self.get_cross_loc(card_im)
            if len(self.deck.hand) == 2:
                card_im = card_im.transpose(Image.ROTATE_90)
        if inverted:
            card_im = card_im.rotate(180)
        #lastly, we paste the image to the table image
        self.table.paste(card_im, location)
        
    def get_cross_loc(self, card_im):
        if len(self.deck.hand) == 1: #the first card
            x_loc = card_im.size[0]*2
            y_loc = card_im.size[1]*2
            self.cross_loc = (x_loc, y_loc)
        elif len(self.deck.hand) == 2:
            x_loc = self.cross_loc[0] - int(card_im.size[0]/4)
            y_loc = self.cross_loc[1]
            return (x_loc, y_loc)
        elif len(self.deck.hand) == 3:
            x_loc = self.cross_loc[0]
            y_loc = self.cross_loc[1] + card_im.size[1] + 10
            return (x_loc, y_loc)
        elif len(self.deck.hand) == 4:
            x_loc = self.cross_loc[0] - card_im.size[0] - 10
            y_loc = self.cross_loc[1]
            return (x_loc, y_loc)
        elif len(self.deck.hand) == 5:
            x_loc = self.cross_loc[0]
            y_loc = self.cross_loc[1] - card_im.size[1] - 10
            return (x_loc, y_loc)
        elif len(self.deck.hand) == 6:
            x_loc = self.cross_loc[0] + card_im.size[0] + 10
            y_loc = self.cross_loc[1]
            self.cross_loc = (x_loc, y_loc)
        elif len(self.deck.hand) == 7:
            x_loc = self.cross_loc[0] + card_im.size[0] + 10
            y_loc = self.table.size[1] - card_im.size[1]
            self.cross_loc = (x_loc, y_loc)
        else:
            x_loc = self.cross_loc[0]
            y_loc = self.cross_loc[1] - card_im.size[1] - 10
            self.cross_loc = (x_loc, y_loc)
        return self.cross_loc
        
if __name__ == '__main__':
    deck = tdeck()
    table = card_table('Tester', deck, 'Seven')
    while table.draw_max > len(table.deck.hand):
        table.next_step()
        print(table.deck.get_name())
        print(table.deck.get_desc())
    table.next_step()