package main

import (
	"fmt"
	"sort"
)

// FriendNetwork is a generic social graph (Java FriendNetwork<T>).
type FriendNetwork[T any] struct {
	allFriendships     []*Friendship[T]
	allUser            map[string]*User[T]
	allIndirectFriends map[string]bool
}

func NewFriendNetwork[T any]() *FriendNetwork[T] {
	return &FriendNetwork[T]{
		allFriendships: make([]*Friendship[T], 0),
		allUser:        make(map[string]*User[T]),
	}
}

func (fn *FriendNetwork[T]) addUser(userName string) *User[T] {
	if u, ok := fn.allUser[userName]; ok {
		return u
	}
	v := newUser[T](userName)
	fn.allUser[userName] = v
	return v
}

func (fn *FriendNetwork[T]) getUser(userName string) *User[T] {
	return fn.allUser[userName]
}

func (fn *FriendNetwork[T]) addFriendship(user1, user2 string) {
	var u1 *User[T]
	if u, ok := fn.allUser[user1]; ok {
		u1 = u
	} else {
		u1 = newUser[T](user1)
		fn.allUser[user1] = u1
	}
	var u2 *User[T]
	if u, ok := fn.allUser[user2]; ok {
		u2 = u
	} else {
		u2 = newUser[T](user2)
		fn.allUser[user2] = u2
	}
	f := newFriendship[T](u1, u2)
	fn.allFriendships = append(fn.allFriendships, f)
	u1.addAdjacentUser(f, u2)
	u2.addAdjacentUser(f, u1)
}

func (fn *FriendNetwork[T]) removeFriendship(user1, user2 string) {
	u1 := fn.allUser[user1]
	u2 := fn.allUser[user2]
	f := newFriendship[T](u1, u2)
	fn.allFriendships = removeFriendshipMatch(fn.allFriendships, f)
	if u1 != nil {
		u1.removeAdjacentUser(f, u2)
	}
	if u2 != nil {
		u2.removeAdjacentUser(f, u1)
	}
}

func (fn *FriendNetwork[T]) getDirectFriends(userName string) map[string]bool {
	allDirectFriends := make(map[string]bool)
	user := fn.getUser(userName)
	// NOTE: faithfully ported - Java always reads getUser2() of each friendship.
	for _, friend := range user.getFriendships() {
		allDirectFriends[friend.getUser2().userName] = true
	}
	return allDirectFriends
}

func (fn *FriendNetwork[T]) getIndirectFriends(userName string) map[string]bool {
	fn.allIndirectFriends = make(map[string]bool)
	user := fn.getUser(userName)
	friends := user.getAdjacentUseres()
	visited := make(map[string]bool)
	visited[userName] = true
	for _, frd := range user.getFriendships() {
		friend := frd.getUser2()
		if !visited[friend.userName] {
			fn.getIndirectFriendsHelper(friend, visited, friends)
		}
	}
	return fn.allIndirectFriends
}

// getIndirectFriendsHelper is the recursive helper (renamed Java overload).
func (fn *FriendNetwork[T]) getIndirectFriendsHelper(friend *User[T], visited map[string]bool, directFriends []*User[T]) {
	visited[friend.userName] = true
	for _, frd := range friend.getAdjacentUseres() {
		if !visited[frd.userName] {
			if !containsUser(directFriends, frd) {
				fn.allIndirectFriends[frd.userName] = true
			}
			fn.getIndirectFriendsHelper(frd, visited, directFriends)
		}
	}
}

func (fn *FriendNetwork[T]) getAllFriendships() []*Friendship[T] { return fn.allFriendships }

func (fn *FriendNetwork[T]) getAllUser() []*User[T] {
	out := make([]*User[T], 0, len(fn.allUser))
	for _, u := range fn.allUser {
		out = append(out, u)
	}
	return out
}

func (fn *FriendNetwork[T]) String() string {
	out := ""
	for _, f := range fn.getAllFriendships() {
		out += f.String() + "\n"
	}
	return out
}

// User is a network member carrying generic data.
type User[T any] struct {
	userName     string
	data         T
	friendships  []*Friendship[T]
	adjacentUser []*User[T]
}

func newUser[T any](userName string) *User[T] {
	return &User[T]{userName: userName}
}

func (u *User[T]) getUserName() string { return u.userName }

func (u *User[T]) addAdjacentUser(e *Friendship[T], v *User[T]) {
	u.friendships = append(u.friendships, e)
	u.adjacentUser = append(u.adjacentUser, v)
}

func (u *User[T]) removeAdjacentUser(e *Friendship[T], v *User[T]) {
	u.friendships = removeFriendshipMatch(u.friendships, e)
	u.adjacentUser = removeUserMatch(u.adjacentUser, v)
}

func (u *User[T]) getAdjacentUseres() []*User[T]    { return u.adjacentUser }
func (u *User[T]) getFriendships() []*Friendship[T] { return u.friendships }

// Friendship is an undirected relationship between two users.
type Friendship[T any] struct {
	user1 *User[T]
	user2 *User[T]
}

func newFriendship[T any](user1, user2 *User[T]) *Friendship[T] {
	return &Friendship[T]{user1: user1, user2: user2}
}

func (f *Friendship[T]) getUser1() *User[T] { return f.user1 }
func (f *Friendship[T]) getUser2() *User[T] { return f.user2 }

func (f *Friendship[T]) String() string {
	u1, u2 := "<nil>", "<nil>"
	if f.user1 != nil {
		u1 = f.user1.userName
	}
	if f.user2 != nil {
		u2 = f.user2.userName
	}
	return fmt.Sprintf("Friendship [User1=%s, User2=%s]", u1, u2)
}

// sameUsers reports whether two friendships connect the same user pair.
func sameUsers[T any](a, b *Friendship[T]) bool {
	return a != nil && b != nil && a.user1 == b.user1 && a.user2 == b.user2
}

func removeFriendshipMatch[T any](list []*Friendship[T], f *Friendship[T]) []*Friendship[T] {
	for i, e := range list {
		if e == f || sameUsers(e, f) {
			return append(list[:i:i], list[i+1:]...)
		}
	}
	return list
}

func removeUserMatch[T any](list []*User[T], u *User[T]) []*User[T] {
	for i, e := range list {
		if e == u || (e != nil && u != nil && e.userName == u.userName) {
			return append(list[:i:i], list[i+1:]...)
		}
	}
	return list
}

func containsUser[T any](list []*User[T], u *User[T]) bool {
	for _, e := range list {
		if e == u || (e != nil && u != nil && e.userName == u.userName) {
			return true
		}
	}
	return false
}

func sortedKeys(m map[string]bool) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}

// Java had no main() in FriendNetwork; this demo exercises the network.
func main() {
	fn := NewFriendNetwork[string]()
	fn.addFriendship("A", "B")
	fn.addFriendship("B", "C")
	fn.addFriendship("C", "D")
	fn.addFriendship("A", "E")

	fmt.Print(fn)

	direct := fn.getDirectFriends("A")
	fmt.Println("Direct friends of A:", sortedKeys(direct))

	indirect := fn.getIndirectFriends("A")
	fmt.Println("Indirect friends of A:", sortedKeys(indirect))

	fmt.Println("Total users:", len(fn.getAllUser()))
}
