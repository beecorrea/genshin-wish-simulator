import casino
import random
from dataclasses import dataclass


@dataclass
# In the end, the initial investment for a copy of a 5-star character
# is at least (minimum_bet * soft_pity), which is around USD 200~220.
class Pity:
    # Hard pity incites the player to pay, given that grinding 90 fates is too much work.
    hard_pity: int
    # Soft pity means the player must pay at least (minimum_bet * soft_pity) to have a considerable chance at winning.
    soft_pity: int

    base_ratio: int
    has_50_pity: bool

    pity_counter: int = 0

    def get_rate(self):
        if self.is_in_hard_pity():
            return 1
        if self.is_in_soft_pity():
            return self.calc_soft_pity()
        return self.base_ratio

    def calc_soft_pity(self):
        curr_wish = (self.pity_counter - self.soft_pity) + 1
        increase = self.get_increase_ratio() * curr_wish
        return increase + self.base_ratio

    def get_increase_ratio(self):
        return 1 / (self.hard_pity - self.soft_pity)

    def is_in_soft_pity(self):
        return (
            self.pity_counter >= self.soft_pity
            and self.pity_counter < self.hard_pity - 1
        )

    def is_in_hard_pity(self):
        return self.pity_counter == self.hard_pity - 1

    def increment(self):
        self.pity_counter += 1

    def reset(self):
        self.pity_counter = 0


@dataclass
class Wish(casino.CasinoGame):
    name: str = "wish"
    p_five_star: float = 0.006
    p_promoted: float = 0.5

    wish_counter: int = 0
    pity_counter: int = 0
    player_hits: int = 0
    promo_hits: int = 0

    pity: Pity = Pity(90, 74, p_five_star, False)

    minimum_bet_per_round: int = 3

    def __post_init__(self):
        self.cap_house_earnings_per_game: float = (
            self.avg_rounds_per_game * self.minimum_bet_per_round
        )
        self.cap_earnings_per_day: float = (
            self.games_per_day * self.cap_house_earnings_per_game
        )

    def wish(self):
        ot = self.simulate()
        self.wish_counter += 1
        return ot

    def simulate(self):
        # Roll dice
        hit_type = "STANDARD"
        rate = self.pity.get_rate()
        roll = random.uniform(0, 1)
        if roll > rate:
            # No luck =/
            self.pity.increment()
            return 0, hit_type

        print("Roll %d => Pity %d" % (self.wish_counter, self.pity.pity_counter))
        # Check for rate-up or 50/50 pity
        promo_roll = random.uniform(0, 1)
        if self.pity.has_50_pity or promo_roll <= 0.5:
            self.hit_promo()
            hit_type = "FEATURED"
        else:
            self.hit()

        return 1, hit_type

    def hit(self):
        print("Well, at least it's a 5-star :(")
        self.player_hits += 1
        print("Lost previous 50/50, turning pity on.")
        self.pity.has_50_pity = True
        self.pity.reset()

    def hit_promo(self):
        print("Got the banner 5-star!!")
        self.promo_hits += 1
        self.pity.has_50_pity = False
        self.pity.reset()

    # def calc_earnings(self):
    #     return (self.wish_counter - self.player_hits) * self.minimum_bet_per_round
