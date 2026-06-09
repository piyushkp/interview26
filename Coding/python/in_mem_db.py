"""Port of java/InMemDB.java -> in-memory DB with add/delete/get/count + transactions.

Original Java package: code.ds

Faithful port: the reference SET/ROLLBACK count bookkeeping is buggy, so the
GET/COUNT outputs differ from the Java source comments (kept intentionally).
"""

from typing import Dict, List


class MemDB:
    def __init__(self):
        self.map: Dict[str, int] = {}
        self.map1: Dict[int, int] = {}
        self._actions: List["Transaction"] = []

    def SET(self, name: str, value: int) -> None:
        if name in self.map:
            old_value = self.map[name]
            old_count = self.map1[old_value]
            old_count -= 1
            self.map1[old_value] = old_count
            if self._actions:
                self._actions[-1].add_set_command([name, str(old_value)])
        else:
            if self._actions:
                self._actions[-1].add_set_command([name])
        if value not in self.map1:
            self.map1[value] = 1
        else:
            count = self.map1[value]
            count += 1
            self.map1[value] = count
        self.map[name] = value

    def GET(self, name: str) -> None:
        print(self.map.get(name))

    def DELETE(self, name: str) -> None:
        old_value = self.map[name]
        del self.map[name]
        count = self.map1[old_value]
        count -= 1
        self.map1[old_value] = count
        if self._actions:
            self._actions[-1].add_set_command([name, str(old_value)])

    def COUNT(self, value: int) -> None:
        print(self.map1.get(value))

    def BEGIN(self) -> None:
        self._actions.append(Transaction(self))

    def ROLLBACK(self) -> None:
        if not self._actions:
            print("NO TRANSACTIONS IN PROGRESS")
            return
        self._actions.pop().rollback()

    def COMMIT(self) -> None:
        if not self._actions:
            print("NO TRANSACTIONS IN PROGRESS")
            return
        self._actions.clear()


class Transaction:
    def __init__(self, db: MemDB):
        self._db = db
        self._commands: List[str] = []

    def add_set_command(self, command: List[str]) -> None:
        if len(command) == 1:
            self._commands.append(command[0])
        else:
            self._commands.append(command[0] + " " + command[1])

    def add_delete_command(self, command: List[str]) -> None:
        self._commands.append(command[0] + " " + command[1])

    def rollback(self) -> None:
        while self._commands:
            command = self._commands.pop()
            parsed = command.split(" ")
            if len(parsed) == 1:
                self._db.DELETE(parsed[0])
            else:
                self._db.SET(parsed[0], int(parsed[1]))


if __name__ == "__main__":
    db = MemDB()
    db.SET("a", 10)
    db.BEGIN()
    db.SET("a", 15)
    db.BEGIN()
    db.DELETE("a")
    db.SET("a", 10)
    db.ROLLBACK()
    db.COMMIT()
    db.SET("b", 10)
    db.GET("a")    # 15  (Java comment said 10; reference bug preserved)
    db.COUNT(10)   # 1   (Java comment said 2)
    db.SET("a", 10)
    db.GET("a")    # 10
    db.SET("b", 15)
    db.COUNT(15)   # 1
    db.SET("b", 20)
    db.SET("c", 15)
    db.COUNT(10)   # 1
