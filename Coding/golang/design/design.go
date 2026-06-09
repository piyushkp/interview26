package main

// Ported from Coding/java/design.java (original package code.ds).
// Parking-lot OO design. The Java file had no main; a small demo is added.

import "fmt"

const (
	numberOfSmallSlots   = 10
	numberOfCompactSlots = 10
	numberOfLargeSlots   = 10
)

func main() {
	lot := newParkingLot()
	car := newCar()
	token := lot.park(car)
	// canFit* all return false in the reference design, so park yields -1.
	fmt.Println("Parked vehicle, token:", token)
}

// Vehicle is the abstract base for things that can be parked.
type Vehicle interface {
	canFitInSmallSlot() bool
	canFitInCompactSlot() bool
	canFitInLargeSlot() bool
	hashCode() int64
}

type baseVehicle struct {
	licencePlate string
	id           int64
}

func (v *baseVehicle) canFitInSmallSlot() bool   { return false }
func (v *baseVehicle) canFitInCompactSlot() bool { return false }
func (v *baseVehicle) canFitInLargeSlot() bool   { return false }
func (v *baseVehicle) hashCode() int64           { return v.id }

var vehicleCounter int64

func nextVehicleID() int64 {
	vehicleCounter++
	return vehicleCounter
}

type Car struct{ baseVehicle }
type Motorcycle struct{ baseVehicle }
type Bus struct{ baseVehicle }
type Truck struct{ baseVehicle }

func newCar() *Car               { return &Car{baseVehicle{id: nextVehicleID()}} }
func newMotorcycle() *Motorcycle { return &Motorcycle{baseVehicle{id: nextVehicleID()}} }
func newBus() *Bus               { return &Bus{baseVehicle{id: nextVehicleID()}} }
func newTruck() *Truck           { return &Truck{baseVehicle{id: nextVehicleID()}} }

// Slot is the abstract base for a parking slot.
type Slot interface {
	park()
	unPark()
	isOccupied() bool
	getSlotNumber() int
}

type baseSlot struct {
	occupied   bool // renamed from isOccupied to avoid clashing with isOccupied()
	slotNumber int
}

func (s *baseSlot) isOccupied() bool   { return s.occupied }
func (s *baseSlot) getSlotNumber() int { return s.slotNumber }
func (s *baseSlot) park()              { s.occupied = true }
func (s *baseSlot) unPark()            { s.occupied = false }

func (s *baseSlot) equals(o Slot) bool {
	return o.getSlotNumber() == s.slotNumber
}

func (s *baseSlot) hashCode() int {
	hash := 5
	hash = 53*hash + s.slotNumber
	return hash
}

type SmallSlot struct{ baseSlot }
type CompactSlot struct{ baseSlot }
type LargeSlot struct{ baseSlot }

func newSmallSlot(n int) *SmallSlot     { return &SmallSlot{baseSlot{slotNumber: n}} }
func newCompactSlot(n int) *CompactSlot { return &CompactSlot{baseSlot{slotNumber: n}} }
func newLargeSlot(n int) *LargeSlot     { return &LargeSlot{baseSlot{slotNumber: n}} }

// ParkingLot manages slots of each size as stacks.
type ParkingLot struct {
	occupiedSlots map[int64]Slot
	smallSlots    []Slot
	compactSlots  []Slot
	largeSlots    []Slot
}

func newParkingLot() *ParkingLot {
	p := &ParkingLot{occupiedSlots: map[int64]Slot{}}
	p.createSlots()
	return p
}

func (p *ParkingLot) createSlots() {
	for i := 1; i <= numberOfSmallSlots; i++ {
		p.smallSlots = append(p.smallSlots, newSmallSlot(i))
	}
	for i := 1; i <= numberOfCompactSlots; i++ {
		p.compactSlots = append(p.compactSlots, newCompactSlot(i))
	}
	for i := 1; i <= numberOfLargeSlots; i++ {
		p.largeSlots = append(p.largeSlots, newLargeSlot(i))
	}
}

// popSlot pops the top slot off a stack, or nil if empty.
func popSlot(stack *[]Slot) Slot {
	s := *stack
	if len(s) == 0 {
		return nil
	}
	top := s[len(s)-1]
	*stack = s[:len(s)-1]
	return top
}

func (p *ParkingLot) park(vehicle Vehicle) int64 {
	var slot Slot
	var uniqueToken int64 = -1

	if vehicle.canFitInSmallSlot() {
		slot = popSlot(&p.smallSlots)
		if slot != nil {
			uniqueToken = p.parkHelper(slot, vehicle)
		}
	}
	if vehicle.canFitInCompactSlot() {
		slot = popSlot(&p.compactSlots)
		if slot != nil {
			uniqueToken = p.parkHelper(slot, vehicle)
		}
	}
	if vehicle.canFitInLargeSlot() {
		slot = popSlot(&p.largeSlots)
		if slot != nil {
			uniqueToken = p.parkHelper(slot, vehicle)
		}
	}
	return uniqueToken
}

func (p *ParkingLot) unPark(uniqueToken int64) {
	slot := p.occupiedSlots[uniqueToken]
	if slot == nil {
		return
	}
	slot.unPark()
	if _, ok := slot.(*SmallSlot); ok {
		p.smallSlots = append(p.smallSlots, slot)
	}
	delete(p.occupiedSlots, uniqueToken)
}

func (p *ParkingLot) parkHelper(slot Slot, vehicle Vehicle) int64 {
	slot.park()
	uniqueToken := vehicle.hashCode() * 43
	p.occupiedSlots[uniqueToken] = slot
	return uniqueToken
}

// ParkingFloor groups available/occupied slots per floor.
type ParkingFloor struct {
	availableCarParkingSlots  []Slot
	availableBikeParkingSlots []Slot
	occupiedCarParkingSlots   []Slot
	occupiedBikeParkingSlots  []Slot
}

func (f *ParkingFloor) getNumberOfAvailableCarParkingSlots() []Slot {
	return []Slot{}
}

func (f *ParkingFloor) getNumberOfAvailableBikeParkingSlots() []Slot {
	return []Slot{}
}

// ParkingArea groups multiple floors.
type ParkingArea struct {
	parkingFloors []*ParkingFloor
}
