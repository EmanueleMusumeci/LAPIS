(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   red_block_1 yellow_block_1 yellow_block_2 purple_block_1 grey_block_1 - block
 )
 (:init (ontable red_block_1) (ontable yellow_block_1) (ontable yellow_block_2) (on purple_block_1 red_block_1) (ontable grey_block_1) (clear yellow_block_1) (clear yellow_block_2) (clear purple_block_1) (clear grey_block_1) (handempty) (= (total-cost) 0))
 (:goal (and (on yellow_block_2 purple_block_1)))
 (:constraints (sometime (not (clear purple_block_1))) (sometime-after (not (clear purple_block_1)) (holding red_block_1)))
 (:metric minimize (total-cost))
)
