"""Simulate a battle between two ordered teams of monsters.

battle(team1, team2) returns an Outcome (winner's name + event log). The team
passed first attacks first; one champion from each team fights at a time, and a
defeated champion is replaced by the next monster in its team. The first team
with no monsters left loses.

Follow-up: monsters may have a `type` and a `weakness`. Damage is doubled when
the attacker's type matches the defender's weakness ("super effective"), halved
and rounded down when the defender's type matches the attacker's weakness ("not
very effective"), and unchanged otherwise.

If neither current monster can damage the other, the fight cannot progress, so
battle returns a stalemate Outcome (winning_team_name = None) instead of
looping forever.
"""


class Monster:
    """A combatant with life, attack, and an optional type/weakness."""

    def __init__(self, name, life_points, attack, type_=None, weakness=None):
        # Time: O(1), Space: O(1) - stores its fields.
        self.name = name
        self.life_points = life_points
        self.attack = attack
        self.type = type_
        self.weakness = weakness


class Team:
    """A named, ordered roster of monsters."""

    def __init__(self, name, monsters):
        # Time: O(1), Space: O(1) - keeps a reference to the roster.
        self.name = name
        self.monsters = monsters


class Outcome:
    """The battle result: the winning team's name (None on a stalemate), the
    event log, and a stalemate flag."""

    def __init__(self, winning_team_name, log, is_stalemate=False):
        # Time: O(1), Space: O(1).
        self.winning_team_name = winning_team_name
        self.log = log
        self.is_stalemate = is_stalemate


def _clone_monsters(monsters):
    """Copy the monsters so a battle never mutates the caller's teams."""
    # Time: O(m) for m monsters. Space: O(m) - the new list.
    clones = []
    for monster in monsters:
        clones.append(Monster(monster.name, monster.life_points,
                              monster.attack, monster.type, monster.weakness))
    return clones


def _effective_damage(attacker, defender):
    """Damage the attacker deals, plus a modifier label. Doubled when the
    attacker's type is the defender's weakness, halved when the defender's type
    is the attacker's weakness. modifier is 'super effective', 'not very
    effective', or None."""
    # Time: O(1), Space: O(1) - a couple of comparisons.
    base = attacker.attack
    if attacker.type is not None and attacker.type == defender.weakness:
        return base * 2, "super effective"
    if defender.type is not None and defender.type == attacker.weakness:
        return base // 2, "not very effective"    # halved, rounded down
    return base, None


def _describe(monster):
    """'Name (Type)' when the monster has a type, else just 'Name'."""
    # Time: O(1), Space: O(1).
    if monster.type is not None:
        return f"{monster.name} ({monster.type})"
    return monster.name


def _attack_message(attacker, defender, damage, modifier):
    """One attack log line, noting the modifier when one applied."""
    # Time: O(1), Space: O(1) - builds one string.
    message = (f"{_describe(attacker)} attacks {_describe(defender)} "
               f"for {damage} damage")
    if modifier is not None:
        message += f" ({modifier})"
    return message


# Approach (in plain terms):
#   Picture two line-ups of monsters, one champion from each side in the ring
#   at a time. The teams take turns; on its turn the active team's champion
#   hits the enemy champion, subtracting its attack from their life (types can
#   double or halve the hit). When a champion's life hits 0 it is knocked out
#   and the next monster in that line-up steps in. The first team to run out of
#   monsters loses. Before each hit we check the current pair: if neither can
#   dent the other (both would deal 0 damage), the fight is stuck, so we stop
#   and call it a stalemate instead of looping forever.
def battle(team1, team2):
    """Simulate team1 vs team2 (team1 attacks first). Returns an Outcome with
    the winner's name and an event log, or a stalemate Outcome if the fight
    cannot progress."""
    # t = total monsters, L = total starting life across both teams.
    # Time: O(t + L) - each landed hit removes >= 1 life; matchups advance at
    #       most t times. Space: O(t + L) - the working copies plus the log.
    log = []
    fighters1 = _clone_monsters(team1.monsters)
    fighters2 = _clone_monsters(team2.monsters)
    index1 = 0
    index2 = 0
    team1_attacks = True                # team1 (first argument) attacks first

    while index1 < len(fighters1) and index2 < len(fighters2):
        blue = fighters1[index1]
        red = fighters2[index2]

        # Stalemate: if neither current monster can hurt the other, stop.
        if (_effective_damage(blue, red)[0] == 0
                and _effective_damage(red, blue)[0] == 0):
            log.append("Stalemate - neither team can make progress")
            return Outcome(None, log, is_stalemate=True)

        if team1_attacks:
            attacker_team, attacker, defender = team1, blue, red
        else:
            attacker_team, attacker, defender = team2, red, blue

        log.append(f"{attacker_team.name} turn")
        damage, modifier = _effective_damage(attacker, defender)
        defender.life_points = max(0, defender.life_points - damage)
        log.append(_attack_message(attacker, defender, damage, modifier))

        if defender.life_points == 0:
            log.append(f"{defender.name} is defeated")
            if team1_attacks:
                index2 += 1                 # team2's champion falls
            else:
                index1 += 1                 # team1's champion falls

        team1_attacks = not team1_attacks   # turns alternate

    winner = team2 if index1 >= len(fighters1) else team1
    log.append(f"{winner.name} wins")
    return Outcome(winner.name, log)


if __name__ == "__main__":
    # ----- Example: basic battle (from the problem statement) -----
    blue_team = Team("Team Blue",
                     [Monster("Dog", 3, 2), Monster("Wolf", 4, 1)])
    red_team = Team("Team Red",
                    [Monster("Cat", 3, 3), Monster("Tiger", 4, 5)])
    result = battle(blue_team, red_team)
    for line in result.log:
        print(line)
    print("winner:", result.winning_team_name)
    # Team Blue turn / Dog attacks Cat for 2 damage / Team Red turn /
    # Cat attacks Dog for 3 damage / Dog is defeated / Team Blue turn /
    # Wolf attacks Cat for 1 damage / Cat is defeated / Team Red turn /
    # Tiger attacks Wolf for 5 damage / Wolf is defeated / Team Red wins
    # winner: Team Red

    print("---")

    # ----- Follow-up: type advantages (super / not very effective) -----
    fire_team = Team("Fire", [Monster("Dragon", 12, 5, "Fire", "Water")])
    earth_team = Team("Earth", [Monster("Troll", 20, 4, "Earth", "Fire")])
    result = battle(fire_team, earth_team)
    for line in result.log:
        print(line)
    print("winner:", result.winning_team_name)
    # Dragon (Fire) attacks Troll (Earth) for 10 damage (super effective)
    # Troll (Earth) attacks Dragon (Fire) for 2 damage (not very effective)
    # ... Fire wins

    print("---")

    # ----- Stalemate: neither monster can deal damage -----
    rocks = Team("Rocks", [Monster("Pebble", 5, 0)])
    stones = Team("Stones", [Monster("Boulder", 5, 0)])
    result = battle(rocks, stones)
    for line in result.log:
        print(line)
    print("stalemate:", result.is_stalemate)
    print("winner:", result.winning_team_name)
    # Stalemate - neither team can make progress
    # stalemate: True
    # winner: None
