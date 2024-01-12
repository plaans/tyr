(define (domain Fake)

  (:requirements :negative-preconditions)

  (:types robot place)

  (:predicates
    (at ?r - robot ?p - place)
  )

  (:action move
    :parameters (?r - robot ?f ?t - place)
    :precondition (and 
        (at ?r ?f)
        (not (at ?r ?t))
    )
    :effect (and 
        (not (at ?r ?f)) 
        (at ?r ?t)
    )
  )
)