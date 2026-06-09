"""Friend network modelled as an undirected graph of users.

Idiomatic Python 3 port of java/FriendNetwork.java (original package code.ds).
The Java source has no ``main``; a demonstrative one is added at the bottom.
"""


class User:
    def __init__(self, user_name):
        self.user_name = user_name
        self._data = None
        self._friendships = []   # list of Friendship
        self._adjacent_user = []  # list of User

    def get_user_name(self):
        return self.user_name

    def add_adjacent_user(self, e, v):
        self._friendships.append(e)
        self._adjacent_user.append(v)

    def remove_adjacent_user(self, e, v):
        if e in self._friendships:
            self._friendships.remove(e)
        if v in self._adjacent_user:
            self._adjacent_user.remove(v)

    def get_adjacent_users(self):
        return self._adjacent_user

    def get_friendships(self):
        return self._friendships

    def __hash__(self):
        # NOTE: the Java hashCode parses userName as an Integer (a latent bug for
        # non-numeric names). We key on the string instead so the class is usable
        # with any user name.
        return hash(self.user_name)

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, User):
            return False
        return self.user_name == other.user_name


class Friendship:
    def __init__(self, user1, user2):
        self.user1 = user1
        self.user2 = user2

    def get_user1(self):
        return self.user1

    def get_user2(self):
        return self.user2

    def __hash__(self):
        return hash((self.user1, self.user2))

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Friendship):
            return False
        return self.user1 == other.user1 and self.user2 == other.user2

    def __str__(self):
        return "Friendship [User1={}, User2={}]".format(
            self.user1.user_name, self.user2.user_name)


class FriendNetwork:
    def __init__(self):
        self.all_friendships = []   # list of Friendship
        self.all_user = {}          # dict[str, User]
        self.all_indirect_friends = None  # set[str], rebuilt per query

    def add_user(self, user_name):
        if user_name in self.all_user:
            return self.all_user[user_name]
        v = User(user_name)
        self.all_user[user_name] = v
        return v

    def get_user(self, user_name):
        return self.all_user.get(user_name)

    def add_friendship(self, user1, user2):
        if user1 in self.all_user:
            u1 = self.all_user[user1]
        else:
            u1 = User(user1)
            self.all_user[user1] = u1
        if user2 in self.all_user:
            u2 = self.all_user[user2]
        else:
            u2 = User(user2)
            self.all_user[user2] = u2

        friendship = Friendship(u1, u2)
        self.all_friendships.append(friendship)
        u1.add_adjacent_user(friendship, u2)
        u2.add_adjacent_user(friendship, u1)

    def remove_friendship(self, user1, user2):
        u1 = self.all_user.get(user1)  # no-user-found exception omitted, as in Java
        u2 = self.all_user.get(user2)

        friendship = Friendship(u1, u2)
        if friendship in self.all_friendships:
            self.all_friendships.remove(friendship)
        if u1 is not None:
            u1.remove_adjacent_user(friendship, u2)
        if u2 is not None:
            u2.remove_adjacent_user(friendship, u1)

    def get_direct_friends(self, user_name):
        all_direct_friends = set()
        user = self.get_user(user_name)
        for friend in user.get_friendships():
            all_direct_friends.add(friend.get_user2().user_name)
        return all_direct_friends

    def get_indirect_friends(self, user_name):
        self.all_indirect_friends = set()
        user = self.get_user(user_name)
        friends = user.get_adjacent_users()
        visited = set()
        visited.add(user_name)
        for frd in user.get_friendships():
            friend = frd.get_user2()
            if friend.user_name not in visited:
                self._get_indirect_friends_helper(friend, visited, friends)
        return self.all_indirect_friends

    # Recursive helper (Java overloaded this as getIndirectFriends; renamed since
    # Python has no method overloading).
    def _get_indirect_friends_helper(self, friend, visited, direct_friends):
        visited.add(friend.user_name)
        for frd in friend.get_adjacent_users():
            if frd.user_name not in visited:
                if frd not in direct_friends:
                    self.all_indirect_friends.add(frd.user_name)
                self._get_indirect_friends_helper(frd, visited, direct_friends)

    def get_all_friendships(self):
        return self.all_friendships

    def get_all_user(self):
        return list(self.all_user.values())

    def __str__(self):
        parts = []
        for friendship in self.get_all_friendships():
            parts.append("{} {}\n".format(
                friendship.get_user1().user_name, friendship.get_user2().user_name))
        return "".join(parts)


if __name__ == "__main__":
    print("FriendNetwork")

    net = FriendNetwork()
    net.add_friendship("A", "B")
    net.add_friendship("A", "E")
    net.add_friendship("B", "C")
    net.add_friendship("C", "D")

    print("direct friends of A:", sorted(net.get_direct_friends("A")))
    print("indirect friends of A:", sorted(net.get_indirect_friends("A")))
    print("all users:", sorted(u.get_user_name() for u in net.get_all_user()))

    net.remove_friendship("A", "E")
    print("direct friends of A after removing E:",
          sorted(net.get_direct_friends("A")))
