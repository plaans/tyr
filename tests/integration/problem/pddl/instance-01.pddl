(define (problem Fake)
	(:domain Fake)

	(:objects
		robot0 - robot
		place0 place1 place2 place3 - place
	)
	(:init
		(at robot0 place0)
	)
	(:goal (and
		(at robot0 place1)
	))
	(:metric minimize (total-time))
)