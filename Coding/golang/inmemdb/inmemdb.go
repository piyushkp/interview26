package main

import (
	"fmt"
	"strconv"
	"strings"
)

// MemDB is an in-memory key/value store that supports nested transactions via
// SET, DELETE, GET, COUNT, BEGIN, ROLLBACK and COMMIT.
type MemDB struct {
	m       map[string]int // name -> value
	count   map[int]int    // value -> number of names currently holding it
	actions []*Transaction // open transaction stack
}

func NewMemDB() *MemDB {
	return &MemDB{m: make(map[string]int), count: make(map[int]int)}
}

func (db *MemDB) SET(name string, value int) {
	if oldValue, ok := db.m[name]; ok {
		oldCount := db.count[oldValue]
		oldCount--
		db.count[oldValue] = oldCount
		if len(db.actions) != 0 {
			db.actions[len(db.actions)-1].addSetCommand([]string{name, strconv.Itoa(oldValue)})
		}
	} else {
		if len(db.actions) != 0 {
			db.actions[len(db.actions)-1].addSetCommand([]string{name})
		}
	}
	if _, ok := db.count[value]; !ok {
		db.count[value] = 1
	} else {
		db.count[value]++
	}
	db.m[name] = value
}

func (db *MemDB) GET(name string) {
	if v, ok := db.m[name]; ok {
		fmt.Println(v)
	} else {
		fmt.Println("null")
	}
}

func (db *MemDB) DELETE(name string) {
	oldValue := db.m[name]
	delete(db.m, name)
	db.count[oldValue]--
	if len(db.actions) != 0 {
		db.actions[len(db.actions)-1].addSetCommand([]string{name, strconv.Itoa(oldValue)})
	}
}

func (db *MemDB) COUNT(value int) {
	if c, ok := db.count[value]; ok {
		fmt.Println(c)
	} else {
		fmt.Println("null")
	}
}

func (db *MemDB) BEGIN() {
	db.actions = append(db.actions, NewTransaction(db))
}

func (db *MemDB) ROLLBACK() {
	if len(db.actions) == 0 {
		fmt.Println("NO TRANSACTIONS IN PROGRESS")
		return
	}
	t := db.actions[len(db.actions)-1]
	db.actions = db.actions[:len(db.actions)-1]
	t.rollback()
}

func (db *MemDB) COMMIT() {
	if len(db.actions) == 0 {
		fmt.Println("NO TRANSACTIONS IN PROGRESS")
		return
	}
	db.actions = db.actions[:0]
}

// Transaction records the inverse commands needed to roll back a set of changes.
type Transaction struct {
	commands []string
	db       *MemDB
}

func NewTransaction(db *MemDB) *Transaction {
	return &Transaction{db: db}
}

func (t *Transaction) addSetCommand(command []string) {
	if len(command) == 1 {
		t.commands = append(t.commands, command[0])
	} else {
		t.commands = append(t.commands, command[0]+" "+command[1])
	}
}

func (t *Transaction) addDeleteCommand(command []string) {
	t.commands = append(t.commands, command[0]+" "+command[1])
}

func (t *Transaction) rollback() {
	for len(t.commands) != 0 {
		command := t.commands[len(t.commands)-1]
		t.commands = t.commands[:len(t.commands)-1]
		parsed := strings.Split(command, " ")
		if len(parsed) == 1 {
			t.db.DELETE(parsed[0])
		} else {
			v, _ := strconv.Atoi(parsed[1])
			t.db.SET(parsed[0], v)
		}
	}
}

func main() {
	db := NewMemDB()
	db.SET("a", 10)
	db.BEGIN()
	db.SET("a", 15)
	db.BEGIN()
	db.DELETE("a")
	db.SET("a", 10)
	db.ROLLBACK()
	db.COMMIT()
	db.SET("b", 10)
	db.GET("a")  // 10
	db.COUNT(10) // 2
	db.SET("a", 10)
	db.GET("a")
	db.SET("b", 15)
	db.COUNT(15)
	db.SET("b", 20)
	db.SET("c", 15)
	db.COUNT(10)
}
