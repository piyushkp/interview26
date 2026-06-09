package main

import (
	"fmt"
	"math/rand"
)

// Card models the abstract Java Card. value() is the abstract method that concrete
// cards must implement; the rest is shared behaviour provided by baseCard.
type Card interface {
	value() int
	getSuit() Suit
	isAvailable() bool
	markUnavailable()
	markAvailable()
	print()
}

// Suit enumerates the four card suits (value matches the Java enum ordinal).
type Suit int

const (
	Club Suit = iota
	Diamond
	Heart
	Spade
)

func (s Suit) getValue() int {
	return int(s)
}

// getSuitFromValue returns the Suit for a value, and false if the value is invalid.
func getSuitFromValue(value int) (Suit, bool) {
	switch value {
	case 0:
		return Club, true
	case 1:
		return Diamond, true
	case 2:
		return Heart, true
	case 3:
		return Spade, true
	default:
		return 0, false
	}
}

// baseCard holds the state and shared behaviour common to all cards.
type baseCard struct {
	available bool
	// faceValue is a number 2-10, 11 for Jack, 12 for Queen, 13 for King, or 1 for Ace.
	faceValue int
	suit      Suit
}

func newBaseCard(c int, s Suit) baseCard {
	return baseCard{available: true, faceValue: c, suit: s}
}

func (b *baseCard) getSuit() Suit       { return b.suit }
func (b *baseCard) isAvailable() bool    { return b.available }
func (b *baseCard) markUnavailable()     { b.available = false }
func (b *baseCard) markAvailable()       { b.available = true }

func (b *baseCard) print() {
	faceValues := []string{"A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"}
	fmt.Print(faceValues[b.faceValue-1])
	switch b.suit {
	case Club:
		fmt.Print("c")
	case Heart:
		fmt.Print("h")
	case Diamond:
		fmt.Print("d")
	case Spade:
		fmt.Print("s")
	}
	fmt.Print(" ")
}

// simpleCard is a concrete Card used for demonstration. The reference Java Card is
// abstract with an abstract value(); this provides a minimal value() implementation.
type simpleCard struct {
	baseCard
}

func newSimpleCard(faceValue int, suit Suit) *simpleCard {
	return &simpleCard{newBaseCard(faceValue, suit)}
}

func (c *simpleCard) value() int { return c.faceValue }

// Deck is a deck of cards that deals from the top.
type Deck struct {
	cards      []Card
	dealtIndex int // marks first undealt card
}

func (d *Deck) setDeckOfCards(deckOfCards []Card) {
	d.cards = deckOfCards
}

func (d *Deck) shuffle() {
	for i := len(d.cards) - 1; i > 0; i-- {
		// Faithful port of Java `(int) Math.random() % (i + 1)`: truncating a value
		// in [0,1) to an int yields 0, so j is always 0 (reference bug preserved).
		j := int(rand.Float64()) % (i + 1)
		card1 := d.cards[i]
		card2 := d.cards[j]
		d.cards[i] = card2
		d.cards[j] = card1
	}
}

func (d *Deck) remainingCards() int {
	return len(d.cards) - d.dealtIndex
}

func (d *Deck) dealHand(number int) []Card {
	if d.remainingCards() < number {
		return nil
	}
	hand := make([]Card, number)
	count := 0
	for count < number {
		card := d.dealCard()
		if card != nil {
			hand[count] = card
			count++
		}
	}
	return hand
}

func (d *Deck) dealCard() Card {
	if d.remainingCards() == 0 {
		return nil
	}
	card := d.cards[d.dealtIndex]
	card.markUnavailable()
	d.dealtIndex++
	return card
}

func (d *Deck) print() {
	for _, card := range d.cards {
		card.print()
	}
}

// Hand is a collection of cards held by a player.
type Hand struct {
	cards []Card
}

func (h *Hand) score() int {
	score := 0
	for _, card := range h.cards {
		score += card.value()
	}
	return score
}

func (h *Hand) addCard(card Card) {
	h.cards = append(h.cards, card)
}

func (h *Hand) print() {
	for _, card := range h.cards {
		card.print()
	}
}

func main() {
	var cards []Card
	for v := 1; v <= 13; v++ {
		for s := 0; s < 4; s++ {
			suit, _ := getSuitFromValue(s)
			cards = append(cards, newSimpleCard(v, suit))
		}
	}

	deck := &Deck{}
	deck.setDeckOfCards(cards)
	deck.shuffle()

	fmt.Printf("Remaining cards: %d\n", deck.remainingCards())

	dealt := deck.dealHand(5)
	hand := &Hand{}
	for _, c := range dealt {
		hand.addCard(c)
	}

	fmt.Print("Dealt hand: ")
	hand.print()
	fmt.Println()
	fmt.Printf("Hand score: %d\n", hand.score())
}
