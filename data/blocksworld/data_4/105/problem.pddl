(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   brown_block_1 grey_block_1 brown_block_2 blue_block_1 red_block_1 - block
 )
 (:init (ontable brown_block_1) (on grey_block_1 brown_block_1) (on brown_block_2 grey_block_1) (ontable blue_block_1) (on red_block_1 brown_block_2) (clear blue_block_1) (clear red_block_1) (handempty) (= (total-cost) 0))
 (:goal (and (ontable grey_block_1)))
 (:constraints (sometime (holding brown_block_2)) (sometime-after (holding brown_block_2) (holding blue_block_1)) (sometime (not (on brown_block_1 grey_block_1))) (sometime-after (not (on brown_block_1 grey_block_1)) (or (on red_block_1 grey_block_1) (holding red_block_1))) (always (not (ontable brown_block_2))) (sometime (clear brown_block_1)) (sometime-before (clear brown_block_1) (or (not (on grey_block_1 brown_block_1)) (not (ontable blue_block_1)))))
 (:metric minimize (total-cost))
)
