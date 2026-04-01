(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   yellow_block_1 grey_block_1 black_block_1 yellow_block_2 purple_block_1 - block
 )
 (:init (ontable yellow_block_1) (ontable grey_block_1) (on black_block_1 grey_block_1) (ontable yellow_block_2) (on purple_block_1 yellow_block_2) (clear yellow_block_1) (clear black_block_1) (clear purple_block_1) (handempty) (= (total-cost) 0))
 (:goal (and (on grey_block_1 yellow_block_2)))
 (:constraints (sometime (and (not (ontable yellow_block_2)) (not (ontable yellow_block_1)))) (sometime (or (not (ontable yellow_block_1)) (holding yellow_block_1))))
 (:metric minimize (total-cost))
)
