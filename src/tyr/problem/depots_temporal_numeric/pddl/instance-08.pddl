(define (problem depotprob4321) (:domain Depot)
(:objects
	depot0 depot1 depot2 depot3 depot4 depot5 depot6 depot7 depot8 depot9 - Depot
	distributor0 distributor1 distributor2 distributor3 distributor4 distributor5 distributor6 distributor7 distributor8 distributor9 - Distributor
	truck0 truck1 truck2 truck3 truck4 - Truck
	pallet0 pallet1 pallet2 pallet3 pallet4 pallet5 pallet6 pallet7 pallet8 pallet9 pallet10 pallet11 pallet12 pallet13 pallet14 pallet15 pallet16 pallet17 pallet18 pallet19 pallet20 pallet21 pallet22 pallet23 pallet24 pallet25 pallet26 pallet27 pallet28 pallet29 - Pallet
	crate0 crate1 crate2 crate3 crate4 crate5 crate6 crate7 crate8 crate9 crate10 crate11 crate12 crate13 crate14 crate15 crate16 crate17 crate18 crate19 crate20 crate21 crate22 crate23 crate24 crate25 crate26 crate27 crate28 crate29 crate30 crate31 crate32 crate33 crate34 crate35 crate36 crate37 crate38 crate39 - Crate
	hoist0 hoist1 hoist2 hoist3 hoist4 hoist5 hoist6 hoist7 hoist8 hoist9 hoist10 hoist11 hoist12 hoist13 hoist14 hoist15 hoist16 hoist17 hoist18 hoist19 - Hoist)
(:init
	(at pallet0 depot0)
	(clear pallet0)
	(at pallet1 depot1)
	(clear crate23)
	(at pallet2 depot2)
	(clear crate16)
	(at pallet3 depot3)
	(clear crate37)
	(at pallet4 depot4)
	(clear crate21)
	(at pallet5 depot5)
	(clear crate38)
	(at pallet6 depot6)
	(clear crate4)
	(at pallet7 depot7)
	(clear crate34)
	(at pallet8 depot8)
	(clear crate5)
	(at pallet9 depot9)
	(clear crate35)
	(at pallet10 distributor0)
	(clear crate14)
	(at pallet11 distributor1)
	(clear pallet11)
	(at pallet12 distributor2)
	(clear crate30)
	(at pallet13 distributor3)
	(clear crate12)
	(at pallet14 distributor4)
	(clear pallet14)
	(at pallet15 distributor5)
	(clear crate7)
	(at pallet16 distributor6)
	(clear pallet16)
	(at pallet17 distributor7)
	(clear crate27)
	(at pallet18 distributor8)
	(clear crate19)
	(at pallet19 distributor9)
	(clear crate36)
	(at pallet20 distributor2)
	(clear crate32)
	(at pallet21 distributor6)
	(clear crate22)
	(at pallet22 depot9)
	(clear crate3)
	(at pallet23 distributor4)
	(clear crate29)
	(at pallet24 distributor5)
	(clear crate11)
	(at pallet25 distributor1)
	(clear crate9)
	(at pallet26 depot7)
	(clear pallet26)
	(at pallet27 depot6)
	(clear crate39)
	(at pallet28 distributor9)
	(clear pallet28)
	(at pallet29 depot2)
	(clear pallet29)
	(at truck0 depot2)
	(= (speed truck0) 1)
	(at truck1 depot4)
	(= (speed truck1) 10)
	(at truck2 depot8)
	(= (speed truck2) 4)
	(at truck3 depot6)
	(= (speed truck3) 1)
	(at truck4 distributor9)
	(= (speed truck4) 4)
	(at hoist0 depot0)
	(available hoist0)
	(= (power hoist0) 6)
	(at hoist1 depot1)
	(available hoist1)
	(= (power hoist1) 2)
	(at hoist2 depot2)
	(available hoist2)
	(= (power hoist2) 6)
	(at hoist3 depot3)
	(available hoist3)
	(= (power hoist3) 2)
	(at hoist4 depot4)
	(available hoist4)
	(= (power hoist4) 6)
	(at hoist5 depot5)
	(available hoist5)
	(= (power hoist5) 4)
	(at hoist6 depot6)
	(available hoist6)
	(= (power hoist6) 5)
	(at hoist7 depot7)
	(available hoist7)
	(= (power hoist7) 2)
	(at hoist8 depot8)
	(available hoist8)
	(= (power hoist8) 1)
	(at hoist9 depot9)
	(available hoist9)
	(= (power hoist9) 8)
	(at hoist10 distributor0)
	(available hoist10)
	(= (power hoist10) 2)
	(at hoist11 distributor1)
	(available hoist11)
	(= (power hoist11) 3)
	(at hoist12 distributor2)
	(available hoist12)
	(= (power hoist12) 6)
	(at hoist13 distributor3)
	(available hoist13)
	(= (power hoist13) 6)
	(at hoist14 distributor4)
	(available hoist14)
	(= (power hoist14) 6)
	(at hoist15 distributor5)
	(available hoist15)
	(= (power hoist15) 10)
	(at hoist16 distributor6)
	(available hoist16)
	(= (power hoist16) 10)
	(at hoist17 distributor7)
	(available hoist17)
	(= (power hoist17) 7)
	(at hoist18 distributor8)
	(available hoist18)
	(= (power hoist18) 4)
	(at hoist19 distributor9)
	(available hoist19)
	(= (power hoist19) 1)
	(at crate0 distributor1)
	(on crate0 pallet25)
	(= (weight crate0) 1)
	(at crate1 distributor2)
	(on crate1 pallet20)
	(= (weight crate1) 1)
	(at crate2 distributor5)
	(on crate2 pallet15)
	(= (weight crate2) 1)
	(at crate3 depot9)
	(on crate3 pallet22)
	(= (weight crate3) 1)
	(at crate4 depot6)
	(on crate4 pallet6)
	(= (weight crate4) 1)
	(at crate5 depot8)
	(on crate5 pallet8)
	(= (weight crate5) 1)
	(at crate6 distributor3)
	(on crate6 pallet13)
	(= (weight crate6) 1)
	(at crate7 distributor5)
	(on crate7 crate2)
	(= (weight crate7) 1)
	(at crate8 distributor1)
	(on crate8 crate0)
	(= (weight crate8) 1)
	(at crate9 distributor1)
	(on crate9 crate8)
	(= (weight crate9) 1)
	(at crate10 depot7)
	(on crate10 pallet7)
	(= (weight crate10) 1)
	(at crate11 distributor5)
	(on crate11 pallet24)
	(= (weight crate11) 1)
	(at crate12 distributor3)
	(on crate12 crate6)
	(= (weight crate12) 1)
	(at crate13 distributor0)
	(on crate13 pallet10)
	(= (weight crate13) 1)
	(at crate14 distributor0)
	(on crate14 crate13)
	(= (weight crate14) 1)
	(at crate15 depot2)
	(on crate15 pallet2)
	(= (weight crate15) 1)
	(at crate16 depot2)
	(on crate16 crate15)
	(= (weight crate16) 1)
	(at crate17 distributor2)
	(on crate17 pallet12)
	(= (weight crate17) 1)
	(at crate18 distributor6)
	(on crate18 pallet21)
	(= (weight crate18) 1)
	(at crate19 distributor8)
	(on crate19 pallet18)
	(= (weight crate19) 1)
	(at crate20 distributor6)
	(on crate20 crate18)
	(= (weight crate20) 1)
	(at crate21 depot4)
	(on crate21 pallet4)
	(= (weight crate21) 1)
	(at crate22 distributor6)
	(on crate22 crate20)
	(= (weight crate22) 1)
	(at crate23 depot1)
	(on crate23 pallet1)
	(= (weight crate23) 1)
	(at crate24 depot9)
	(on crate24 pallet9)
	(= (weight crate24) 1)
	(at crate25 depot6)
	(on crate25 pallet27)
	(= (weight crate25) 1)
	(at crate26 distributor7)
	(on crate26 pallet17)
	(= (weight crate26) 1)
	(at crate27 distributor7)
	(on crate27 crate26)
	(= (weight crate27) 1)
	(at crate28 depot3)
	(on crate28 pallet3)
	(= (weight crate28) 1)
	(at crate29 distributor4)
	(on crate29 pallet23)
	(= (weight crate29) 1)
	(at crate30 distributor2)
	(on crate30 crate17)
	(= (weight crate30) 1)
	(at crate31 distributor9)
	(on crate31 pallet19)
	(= (weight crate31) 1)
	(at crate32 distributor2)
	(on crate32 crate1)
	(= (weight crate32) 1)
	(at crate33 depot3)
	(on crate33 crate28)
	(= (weight crate33) 1)
	(at crate34 depot7)
	(on crate34 crate10)
	(= (weight crate34) 1)
	(at crate35 depot9)
	(on crate35 crate24)
	(= (weight crate35) 1)
	(at crate36 distributor9)
	(on crate36 crate31)
	(= (weight crate36) 1)
	(at crate37 depot3)
	(on crate37 crate33)
	(= (weight crate37) 1)
	(at crate38 depot5)
	(on crate38 pallet5)
	(= (weight crate38) 1)
	(at crate39 depot6)
	(on crate39 crate25)
	(= (weight crate39) 1)
	(= (distance depot0 depot0) 0)
	(= (distance depot0 depot1) 9)
	(= (distance depot0 depot2) 3)
	(= (distance depot0 depot3) 7)
	(= (distance depot0 depot4) 10)
	(= (distance depot0 depot5) 2)
	(= (distance depot0 depot6) 10)
	(= (distance depot0 depot7) 3)
	(= (distance depot0 depot8) 6)
	(= (distance depot0 depot9) 4)
	(= (distance depot0 distributor0) 9)
	(= (distance depot0 distributor1) 6)
	(= (distance depot0 distributor2) 6)
	(= (distance depot0 distributor3) 8)
	(= (distance depot0 distributor4) 8)
	(= (distance depot0 distributor5) 7)
	(= (distance depot0 distributor6) 8)
	(= (distance depot0 distributor7) 10)
	(= (distance depot0 distributor8) 7)
	(= (distance depot0 distributor9) 10)
	(= (distance depot1 depot0) 3)
	(= (distance depot1 depot1) 0)
	(= (distance depot1 depot2) 1)
	(= (distance depot1 depot3) 3)
	(= (distance depot1 depot4) 7)
	(= (distance depot1 depot5) 5)
	(= (distance depot1 depot6) 6)
	(= (distance depot1 depot7) 10)
	(= (distance depot1 depot8) 8)
	(= (distance depot1 depot9) 3)
	(= (distance depot1 distributor0) 2)
	(= (distance depot1 distributor1) 3)
	(= (distance depot1 distributor2) 2)
	(= (distance depot1 distributor3) 5)
	(= (distance depot1 distributor4) 10)
	(= (distance depot1 distributor5) 1)
	(= (distance depot1 distributor6) 6)
	(= (distance depot1 distributor7) 9)
	(= (distance depot1 distributor8) 3)
	(= (distance depot1 distributor9) 1)
	(= (distance depot2 depot0) 3)
	(= (distance depot2 depot1) 2)
	(= (distance depot2 depot2) 0)
	(= (distance depot2 depot3) 8)
	(= (distance depot2 depot4) 9)
	(= (distance depot2 depot5) 5)
	(= (distance depot2 depot6) 4)
	(= (distance depot2 depot7) 7)
	(= (distance depot2 depot8) 4)
	(= (distance depot2 depot9) 1)
	(= (distance depot2 distributor0) 6)
	(= (distance depot2 distributor1) 7)
	(= (distance depot2 distributor2) 1)
	(= (distance depot2 distributor3) 7)
	(= (distance depot2 distributor4) 9)
	(= (distance depot2 distributor5) 7)
	(= (distance depot2 distributor6) 1)
	(= (distance depot2 distributor7) 4)
	(= (distance depot2 distributor8) 7)
	(= (distance depot2 distributor9) 9)
	(= (distance depot3 depot0) 7)
	(= (distance depot3 depot1) 9)
	(= (distance depot3 depot2) 1)
	(= (distance depot3 depot3) 0)
	(= (distance depot3 depot4) 3)
	(= (distance depot3 depot5) 1)
	(= (distance depot3 depot6) 8)
	(= (distance depot3 depot7) 9)
	(= (distance depot3 depot8) 9)
	(= (distance depot3 depot9) 1)
	(= (distance depot3 distributor0) 10)
	(= (distance depot3 distributor1) 2)
	(= (distance depot3 distributor2) 2)
	(= (distance depot3 distributor3) 6)
	(= (distance depot3 distributor4) 9)
	(= (distance depot3 distributor5) 1)
	(= (distance depot3 distributor6) 1)
	(= (distance depot3 distributor7) 3)
	(= (distance depot3 distributor8) 8)
	(= (distance depot3 distributor9) 4)
	(= (distance depot4 depot0) 3)
	(= (distance depot4 depot1) 4)
	(= (distance depot4 depot2) 1)
	(= (distance depot4 depot3) 4)
	(= (distance depot4 depot4) 0)
	(= (distance depot4 depot5) 10)
	(= (distance depot4 depot6) 10)
	(= (distance depot4 depot7) 1)
	(= (distance depot4 depot8) 3)
	(= (distance depot4 depot9) 7)
	(= (distance depot4 distributor0) 9)
	(= (distance depot4 distributor1) 10)
	(= (distance depot4 distributor2) 6)
	(= (distance depot4 distributor3) 10)
	(= (distance depot4 distributor4) 7)
	(= (distance depot4 distributor5) 9)
	(= (distance depot4 distributor6) 10)
	(= (distance depot4 distributor7) 4)
	(= (distance depot4 distributor8) 7)
	(= (distance depot4 distributor9) 9)
	(= (distance depot5 depot0) 4)
	(= (distance depot5 depot1) 6)
	(= (distance depot5 depot2) 10)
	(= (distance depot5 depot3) 6)
	(= (distance depot5 depot4) 2)
	(= (distance depot5 depot5) 0)
	(= (distance depot5 depot6) 7)
	(= (distance depot5 depot7) 2)
	(= (distance depot5 depot8) 2)
	(= (distance depot5 depot9) 4)
	(= (distance depot5 distributor0) 6)
	(= (distance depot5 distributor1) 5)
	(= (distance depot5 distributor2) 7)
	(= (distance depot5 distributor3) 6)
	(= (distance depot5 distributor4) 8)
	(= (distance depot5 distributor5) 7)
	(= (distance depot5 distributor6) 5)
	(= (distance depot5 distributor7) 8)
	(= (distance depot5 distributor8) 8)
	(= (distance depot5 distributor9) 8)
	(= (distance depot6 depot0) 4)
	(= (distance depot6 depot1) 6)
	(= (distance depot6 depot2) 7)
	(= (distance depot6 depot3) 10)
	(= (distance depot6 depot4) 5)
	(= (distance depot6 depot5) 4)
	(= (distance depot6 depot6) 0)
	(= (distance depot6 depot7) 4)
	(= (distance depot6 depot8) 7)
	(= (distance depot6 depot9) 4)
	(= (distance depot6 distributor0) 3)
	(= (distance depot6 distributor1) 1)
	(= (distance depot6 distributor2) 10)
	(= (distance depot6 distributor3) 2)
	(= (distance depot6 distributor4) 7)
	(= (distance depot6 distributor5) 2)
	(= (distance depot6 distributor6) 10)
	(= (distance depot6 distributor7) 3)
	(= (distance depot6 distributor8) 3)
	(= (distance depot6 distributor9) 1)
	(= (distance depot7 depot0) 7)
	(= (distance depot7 depot1) 9)
	(= (distance depot7 depot2) 5)
	(= (distance depot7 depot3) 4)
	(= (distance depot7 depot4) 5)
	(= (distance depot7 depot5) 2)
	(= (distance depot7 depot6) 1)
	(= (distance depot7 depot7) 0)
	(= (distance depot7 depot8) 10)
	(= (distance depot7 depot9) 8)
	(= (distance depot7 distributor0) 8)
	(= (distance depot7 distributor1) 3)
	(= (distance depot7 distributor2) 4)
	(= (distance depot7 distributor3) 5)
	(= (distance depot7 distributor4) 3)
	(= (distance depot7 distributor5) 8)
	(= (distance depot7 distributor6) 8)
	(= (distance depot7 distributor7) 10)
	(= (distance depot7 distributor8) 2)
	(= (distance depot7 distributor9) 4)
	(= (distance depot8 depot0) 4)
	(= (distance depot8 depot1) 4)
	(= (distance depot8 depot2) 5)
	(= (distance depot8 depot3) 4)
	(= (distance depot8 depot4) 6)
	(= (distance depot8 depot5) 1)
	(= (distance depot8 depot6) 5)
	(= (distance depot8 depot7) 5)
	(= (distance depot8 depot8) 0)
	(= (distance depot8 depot9) 8)
	(= (distance depot8 distributor0) 6)
	(= (distance depot8 distributor1) 1)
	(= (distance depot8 distributor2) 7)
	(= (distance depot8 distributor3) 1)
	(= (distance depot8 distributor4) 5)
	(= (distance depot8 distributor5) 1)
	(= (distance depot8 distributor6) 3)
	(= (distance depot8 distributor7) 5)
	(= (distance depot8 distributor8) 10)
	(= (distance depot8 distributor9) 2)
	(= (distance depot9 depot0) 3)
	(= (distance depot9 depot1) 7)
	(= (distance depot9 depot2) 5)
	(= (distance depot9 depot3) 6)
	(= (distance depot9 depot4) 2)
	(= (distance depot9 depot5) 7)
	(= (distance depot9 depot6) 4)
	(= (distance depot9 depot7) 9)
	(= (distance depot9 depot8) 7)
	(= (distance depot9 depot9) 0)
	(= (distance depot9 distributor0) 3)
	(= (distance depot9 distributor1) 10)
	(= (distance depot9 distributor2) 9)
	(= (distance depot9 distributor3) 7)
	(= (distance depot9 distributor4) 4)
	(= (distance depot9 distributor5) 4)
	(= (distance depot9 distributor6) 8)
	(= (distance depot9 distributor7) 9)
	(= (distance depot9 distributor8) 9)
	(= (distance depot9 distributor9) 2)
	(= (distance distributor0 depot0) 6)
	(= (distance distributor0 depot1) 4)
	(= (distance distributor0 depot2) 2)
	(= (distance distributor0 depot3) 2)
	(= (distance distributor0 depot4) 4)
	(= (distance distributor0 depot5) 7)
	(= (distance distributor0 depot6) 3)
	(= (distance distributor0 depot7) 7)
	(= (distance distributor0 depot8) 2)
	(= (distance distributor0 depot9) 3)
	(= (distance distributor0 distributor0) 0)
	(= (distance distributor0 distributor1) 4)
	(= (distance distributor0 distributor2) 9)
	(= (distance distributor0 distributor3) 2)
	(= (distance distributor0 distributor4) 10)
	(= (distance distributor0 distributor5) 10)
	(= (distance distributor0 distributor6) 9)
	(= (distance distributor0 distributor7) 3)
	(= (distance distributor0 distributor8) 9)
	(= (distance distributor0 distributor9) 5)
	(= (distance distributor1 depot0) 8)
	(= (distance distributor1 depot1) 1)
	(= (distance distributor1 depot2) 5)
	(= (distance distributor1 depot3) 7)
	(= (distance distributor1 depot4) 8)
	(= (distance distributor1 depot5) 8)
	(= (distance distributor1 depot6) 1)
	(= (distance distributor1 depot7) 5)
	(= (distance distributor1 depot8) 6)
	(= (distance distributor1 depot9) 9)
	(= (distance distributor1 distributor0) 7)
	(= (distance distributor1 distributor1) 0)
	(= (distance distributor1 distributor2) 3)
	(= (distance distributor1 distributor3) 8)
	(= (distance distributor1 distributor4) 4)
	(= (distance distributor1 distributor5) 7)
	(= (distance distributor1 distributor6) 5)
	(= (distance distributor1 distributor7) 7)
	(= (distance distributor1 distributor8) 3)
	(= (distance distributor1 distributor9) 6)
	(= (distance distributor2 depot0) 9)
	(= (distance distributor2 depot1) 10)
	(= (distance distributor2 depot2) 9)
	(= (distance distributor2 depot3) 8)
	(= (distance distributor2 depot4) 2)
	(= (distance distributor2 depot5) 9)
	(= (distance distributor2 depot6) 8)
	(= (distance distributor2 depot7) 10)
	(= (distance distributor2 depot8) 1)
	(= (distance distributor2 depot9) 6)
	(= (distance distributor2 distributor0) 4)
	(= (distance distributor2 distributor1) 9)
	(= (distance distributor2 distributor2) 0)
	(= (distance distributor2 distributor3) 8)
	(= (distance distributor2 distributor4) 5)
	(= (distance distributor2 distributor5) 4)
	(= (distance distributor2 distributor6) 6)
	(= (distance distributor2 distributor7) 5)
	(= (distance distributor2 distributor8) 8)
	(= (distance distributor2 distributor9) 2)
	(= (distance distributor3 depot0) 3)
	(= (distance distributor3 depot1) 4)
	(= (distance distributor3 depot2) 4)
	(= (distance distributor3 depot3) 6)
	(= (distance distributor3 depot4) 2)
	(= (distance distributor3 depot5) 7)
	(= (distance distributor3 depot6) 2)
	(= (distance distributor3 depot7) 6)
	(= (distance distributor3 depot8) 3)
	(= (distance distributor3 depot9) 4)
	(= (distance distributor3 distributor0) 2)
	(= (distance distributor3 distributor1) 1)
	(= (distance distributor3 distributor2) 4)
	(= (distance distributor3 distributor3) 0)
	(= (distance distributor3 distributor4) 8)
	(= (distance distributor3 distributor5) 6)
	(= (distance distributor3 distributor6) 9)
	(= (distance distributor3 distributor7) 6)
	(= (distance distributor3 distributor8) 5)
	(= (distance distributor3 distributor9) 9)
	(= (distance distributor4 depot0) 1)
	(= (distance distributor4 depot1) 9)
	(= (distance distributor4 depot2) 8)
	(= (distance distributor4 depot3) 7)
	(= (distance distributor4 depot4) 7)
	(= (distance distributor4 depot5) 2)
	(= (distance distributor4 depot6) 10)
	(= (distance distributor4 depot7) 2)
	(= (distance distributor4 depot8) 7)
	(= (distance distributor4 depot9) 8)
	(= (distance distributor4 distributor0) 4)
	(= (distance distributor4 distributor1) 9)
	(= (distance distributor4 distributor2) 1)
	(= (distance distributor4 distributor3) 7)
	(= (distance distributor4 distributor4) 0)
	(= (distance distributor4 distributor5) 3)
	(= (distance distributor4 distributor6) 4)
	(= (distance distributor4 distributor7) 6)
	(= (distance distributor4 distributor8) 9)
	(= (distance distributor4 distributor9) 6)
	(= (distance distributor5 depot0) 10)
	(= (distance distributor5 depot1) 10)
	(= (distance distributor5 depot2) 7)
	(= (distance distributor5 depot3) 4)
	(= (distance distributor5 depot4) 10)
	(= (distance distributor5 depot5) 5)
	(= (distance distributor5 depot6) 9)
	(= (distance distributor5 depot7) 8)
	(= (distance distributor5 depot8) 10)
	(= (distance distributor5 depot9) 4)
	(= (distance distributor5 distributor0) 7)
	(= (distance distributor5 distributor1) 10)
	(= (distance distributor5 distributor2) 2)
	(= (distance distributor5 distributor3) 4)
	(= (distance distributor5 distributor4) 7)
	(= (distance distributor5 distributor5) 0)
	(= (distance distributor5 distributor6) 6)
	(= (distance distributor5 distributor7) 6)
	(= (distance distributor5 distributor8) 10)
	(= (distance distributor5 distributor9) 2)
	(= (distance distributor6 depot0) 3)
	(= (distance distributor6 depot1) 3)
	(= (distance distributor6 depot2) 1)
	(= (distance distributor6 depot3) 4)
	(= (distance distributor6 depot4) 9)
	(= (distance distributor6 depot5) 5)
	(= (distance distributor6 depot6) 6)
	(= (distance distributor6 depot7) 2)
	(= (distance distributor6 depot8) 1)
	(= (distance distributor6 depot9) 5)
	(= (distance distributor6 distributor0) 8)
	(= (distance distributor6 distributor1) 10)
	(= (distance distributor6 distributor2) 4)
	(= (distance distributor6 distributor3) 5)
	(= (distance distributor6 distributor4) 4)
	(= (distance distributor6 distributor5) 4)
	(= (distance distributor6 distributor6) 0)
	(= (distance distributor6 distributor7) 2)
	(= (distance distributor6 distributor8) 1)
	(= (distance distributor6 distributor9) 9)
	(= (distance distributor7 depot0) 6)
	(= (distance distributor7 depot1) 8)
	(= (distance distributor7 depot2) 9)
	(= (distance distributor7 depot3) 7)
	(= (distance distributor7 depot4) 2)
	(= (distance distributor7 depot5) 5)
	(= (distance distributor7 depot6) 5)
	(= (distance distributor7 depot7) 7)
	(= (distance distributor7 depot8) 1)
	(= (distance distributor7 depot9) 4)
	(= (distance distributor7 distributor0) 8)
	(= (distance distributor7 distributor1) 3)
	(= (distance distributor7 distributor2) 7)
	(= (distance distributor7 distributor3) 9)
	(= (distance distributor7 distributor4) 7)
	(= (distance distributor7 distributor5) 5)
	(= (distance distributor7 distributor6) 3)
	(= (distance distributor7 distributor7) 0)
	(= (distance distributor7 distributor8) 7)
	(= (distance distributor7 distributor9) 3)
	(= (distance distributor8 depot0) 6)
	(= (distance distributor8 depot1) 5)
	(= (distance distributor8 depot2) 3)
	(= (distance distributor8 depot3) 10)
	(= (distance distributor8 depot4) 9)
	(= (distance distributor8 depot5) 7)
	(= (distance distributor8 depot6) 3)
	(= (distance distributor8 depot7) 8)
	(= (distance distributor8 depot8) 9)
	(= (distance distributor8 depot9) 4)
	(= (distance distributor8 distributor0) 7)
	(= (distance distributor8 distributor1) 4)
	(= (distance distributor8 distributor2) 1)
	(= (distance distributor8 distributor3) 5)
	(= (distance distributor8 distributor4) 10)
	(= (distance distributor8 distributor5) 3)
	(= (distance distributor8 distributor6) 10)
	(= (distance distributor8 distributor7) 4)
	(= (distance distributor8 distributor8) 0)
	(= (distance distributor8 distributor9) 10)
	(= (distance distributor9 depot0) 7)
	(= (distance distributor9 depot1) 7)
	(= (distance distributor9 depot2) 3)
	(= (distance distributor9 depot3) 3)
	(= (distance distributor9 depot4) 5)
	(= (distance distributor9 depot5) 9)
	(= (distance distributor9 depot6) 8)
	(= (distance distributor9 depot7) 8)
	(= (distance distributor9 depot8) 10)
	(= (distance distributor9 depot9) 5)
	(= (distance distributor9 distributor0) 1)
	(= (distance distributor9 distributor1) 6)
	(= (distance distributor9 distributor2) 10)
	(= (distance distributor9 distributor3) 4)
	(= (distance distributor9 distributor4) 6)
	(= (distance distributor9 distributor5) 9)
	(= (distance distributor9 distributor6) 10)
	(= (distance distributor9 distributor7) 8)
	(= (distance distributor9 distributor8) 6)
	(= (distance distributor9 distributor9) 0)
)

(:goal (and
		(on crate0 crate19)
		(on crate1 crate9)
		(on crate3 pallet1)
		(on crate4 crate12)
		(on crate5 crate29)
		(on crate7 pallet28)
		(on crate8 pallet7)
		(on crate9 crate5)
		(on crate11 crate32)
		(on crate12 pallet0)
		(on crate14 crate11)
		(on crate15 crate27)
		(on crate16 pallet6)
		(on crate17 crate1)
		(on crate18 crate25)
		(on crate19 crate3)
		(on crate20 pallet2)
		(on crate21 pallet23)
		(on crate22 crate20)
		(on crate23 pallet10)
		(on crate24 crate0)
		(on crate25 pallet18)
		(on crate26 pallet15)
		(on crate27 pallet21)
		(on crate28 pallet27)
		(on crate29 pallet8)
		(on crate30 pallet19)
		(on crate31 pallet20)
		(on crate32 pallet3)
		(on crate33 crate21)
		(on crate35 crate24)
		(on crate37 crate14)
		(on crate38 crate28)
		(on crate39 crate7)
	)
)

(:metric minimize (total-time)))
