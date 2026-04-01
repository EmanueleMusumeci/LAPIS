(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   yellow_block_1 brown_block_1 blue_block_1 grey_block_1 yellow_block_2 - block
 )
 (:init (ontable yellow_block_1) (ontable brown_block_1) (on blue_block_1 brown_block_1) (on grey_block_1 blue_block_1) (on yellow_block_2 grey_block_1) (clear yellow_block_1) (clear yellow_block_2) (handempty) (= (total-cost) 0))
 (:goal (and (on blue_block_1 yellow_block_2)))
 (:constraints (sometime (or (on brown_block_1 grey_block_1) (holding yellow_block_1))) (sometime (ontable yellow_block_2)) (sometime-before (ontable yellow_block_2) (holding grey_block_1)) (sometime (holding blue_block_1)) (sometime-after (holding blue_block_1) (on yellow_block_2 brown_block_1)) (sometime (and (not (clear yellow_block_1)) (ontable blue_block_1))) (always (not (ontable grey_block_1))))
 (:metric minimize (total-cost))
)
