class Card:
    RANKS = [str(i) for i in range(2, 11)] + list('JQKA')
    SUITS = '♠ ♥ ♦ ♣'.split()

    def __init__(self, rank, suit, is_flipped=True):
        self.rank = rank
        self.suit = suit
        self.is_flipped = is_flipped

    def __str__(self):
        if not self.is_flipped:
            return 'XX'
        return f'{self.rank}{self.suit}'

    @property
    def cost(self):
        i = self.RANKS.index(self.rank)
        if i <= 7:
            return i + 2
        if i < len(self.RANKS) - 1:
            return 10
        return 1

    def flip(self):
        self.is_flipped = not self.is_flipped


class Deck:

    def __init__(self):
        self.cards = []
        self.deal()

    def deal(self):
        self.create()
        self.shuffle()

    def __str__(self):
        return ' '.join(map(str, self.cards))

    def create(self):
        self.cards = [Card(rank, suit) for suit in Card.SUITS for rank in Card.RANKS]

    def shuffle(self):
        import random
        random.shuffle(self.cards)

    def give_card(self, hand):
        if not self.cards:
            self.deal()
        hand.get_card(self.cards.pop(0))


class Hand:
    def __init__(self, name):
        self.name = name
        self.cards = []

    def get_card(self, card):
        self.cards.append(card)

    def clear(self):
        self.cards.clear()

    def __lt__(self, other):
        return self.total_cost < other.total_cost

    def __gt__(self, other):
        return self.total_cost > other.total_cost

    @property
    def is_aces(self):
        return any(card.rank == 'A' for card in self.cards)

    @property
    def is_went_over(self):
        return self.total_cost > 21

    @property
    def total_cost(self):
        if not all(card.is_flipped for card in self.cards):
            return '?'
        total = sum(card.cost for card in self.cards)
        if total < 12 and self.is_aces:
            total += 10
        return total

    def __str__(self):
        return f"{self.name} {' '.join(map(str, self.cards))} - {self.total_cost}"


class Player(Hand):
    def __init__(self, money=50, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.money = money
        self.bet = 0

    def place_the_bet(self):
        while True:
            answer = input(f'{self.name}, place your bet, please: ')
            if not answer.isdigit():
                print('Input a positive integer not exceeding your balance.')
                continue

            bet = int(answer)
            if bet > self.money:
                print(f'Not enough money for this bet. Your balance is {self.money}')
                continue

            self.bet = bet
            break

    def won_the_round(self):
        self.money += self.bet
        print(f'{self.name} win')

    def loose_the_round(self):
        self.money -= self.bet
        print(f'{self.name} lose')

    def tied_the_round(self):
        print(f'{self.name} tied')

    @property
    def get_balance(self):
        return f'{self.name}`s balance is ${self.money}'


class Dealer(Hand):
    @property
    def is_shortfall(self):
        return self.total_cost < 17

    def flip_the_last_card(self):
        self.cards[-1].flip()


class Game:
    def __init__(self):
        self.players = []
        self.deck = Deck()
        self.dealer = Dealer(name='Dealer')

    def greet(self):
        print('-' * 20)
        print('{:^20s}'.format('Welcome'))
        print('{:^20s}'.format('to the game'))
        print('{:^20s}'.format('"BlackJack"'))
        print('-' * 20)

    def start(self):
        self.greet()
        self.register_players()
        self.loop()

    def create_player(self, position):
        while True:
            name = input(f'Input {position} player`s name: ')
            if not name:
                continue
            return Player(name=name)

    def register_players(self):
        while (count := input('\nInput numbers of players from 1 to 7: ')) not in list(map(str, range(1, 8))):
            pass
        for i in range(int(count)):
            new_player = self.create_player(i + 1)
            self.players.append(new_player)

    def hand_over_cards(self, hands, per_hand=1):
        for _ in range(per_hand):
            for hand in hands:
                self.deck.give_card(hand)

    def first_distribution(self):
        self.hand_over_cards(hands=(*self.players, self.dealer), per_hand=2)
        self.dealer.flip_the_last_card()

    def player_turn(self, player):
        while player.total_cost < 21 and (
                answer := input(f'\n{player.name}, do You want to get a card, y/n? ').lower()) != 'n':
            if answer == 'y':
                self.deck.give_card(player)
                print(player)
                if player.is_went_over:
                    player.loose_the_round()
                    self.remaining_players.remove(player)

    def dealer_turn(self):
        while self.dealer.is_shortfall:
            self.deck.give_card(self.dealer)

    def check_balance_player(self):
        status_balance = ''
        for player in self.players:
            if player.money == 0:
                print(f'{player.name} leaves the table. Good luck!')
                self.players.remove(player)

    def loop(self):
        while self.players:
            self.remaining_players = self.players[:]

            print('\nPlace your bets gentlemen.')
            for player in self.players:
                player.place_the_bet()

            self.first_distribution()
            print(self)

            for player in self.players:
                self.player_turn(player)
            print(self)

            self.dealer.flip_the_last_card()
            if not self.remaining_players:
                print(self)
                print('Dealer won')

            else:
                self.dealer_turn()
                print(self)
                if self.dealer.is_went_over:
                    print('Dealer lose')
                    for player in self.remaining_players:
                        player.won_the_round()
                else:
                    for player in self.remaining_players:
                        if player > self.dealer:
                            player.won_the_round()
                        elif player < self.dealer:
                            player.loose_the_round()
                        else:
                            player.tied_the_round()

            for hand in (*self.players, self.dealer):
                hand.clear()

            self.check_balance_player()

            for player in self.players:
                print(player.get_balance)

        else:
            print('There aren`t no players')

    def __str__(self):
        top_table = '\n' + '  |  '.join(map(str, self.players))
        width_table = len(top_table)
        border = '\n' + '-' * width_table
        empty_space = 2 * ('\n' + ' ' * (width_table - 1))
        bottom_table = '\n' + str(self.dealer).center(width_table - 1)
        table = border + top_table + empty_space + bottom_table + border
        return table


def main():
    game = Game()
    game.start()


if __name__ == '__main__':
    main()
