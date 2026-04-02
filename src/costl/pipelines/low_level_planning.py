import os
import sys
import csv
import time
from pathlib import Path



from src.costl.pipelines.base import BasePipeline
from src.costl.logger_cfg import logger

# ContextMatters imports (now local)
from src.costl.planner.low.utils.log import (
    save_file, save_statistics,
)
from src.costl.planner.low.planner_utils import plan_with_output
from src.costl.planner.low.pddl_generation import (
    generate_domain, generate_problem, refine_problem,
    check_domain_adequacy, check_problem_adequacy,
)
from src.costl.planner.low.pddl_verification import translate_plan, VAL_validate, VAL_ground

class LowLevelPlanningPipeline(BasePipeline):

    def __init__(self, 
                determine_possibility: bool,
                prevent_impossibility: bool,
                pddl_gen_iterations: int,
                planner_timeout: int = 180,
                **base_init_kwargs,
                ):
        super().__init__(**base_init_kwargs)
        self.determine_possibility: bool = determine_possibility
        self.prevent_impossibility: bool = prevent_impossibility
        self.pddl_gen_iterations: int = pddl_gen_iterations
        self.planner_timeout: int = planner_timeout
        
    def _initialize_csv(self, csv_filepath):
        # Initialize CSV with headers
        header = ["Task", "Scene", "Problem", "Planning Successful", "Grounding Successful", 
                "Plan Length", "Refinements per iteration",
                "Domain Generation Time", "Problem Generation Time", "Problem Refinement Time", 
                "Total LLM Time",
                "Failure Stage", "Failure Reason"]
        
        with open(csv_filepath, mode="w", newline='') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow(header)
        
        if self.determine_possibility:
            possibility_header = ["Task", "Scene", "Problem", "Possible", "Explanation"]
            with open(os.path.join(self.results_dir, self.experiment_name, self.timestamp, "possibility.csv"), mode="w", newline='') as f:
                writer = csv.writer(f, delimiter='|')
                writer.writerow(possibility_header)

    def _run_and_log_pipeline(self, task_name, scene_name, problem_id, results_problem_dir,
                            domain_file_path, domain_description,
                            csv_filepath):
        # Run the pipeline
        results = self.grounded_planning(
            goal_file_path=os.path.join(results_problem_dir, "task.txt"),
            initial_location_file_path=os.path.join(results_problem_dir, "init_loc.txt"),
            domain_file_path=domain_file_path,
            results_dir=results_problem_dir,
            domain_description=domain_description,
        )
        
        (final_problem_file_path, final_plan_file_path,
            planning_successful, grounding_successful, task_possible,
            possibility_explanation, refinements_per_iteration,
            domain_generation_time, problem_generation_time,
            problem_refinement_time, total_llm_time,
            failure_stage, failure_reason) = results
        
        # Save the final problem and plan if successful
        plan_length = 0
        if planning_successful and grounding_successful:
            with open(final_problem_file_path, "r") as f:
                save_file(f.read(), os.path.join(results_problem_dir, "problem_final.pddl"))

            with open(final_plan_file_path, "r") as f:
                final_generated_plan = f.read()
                save_file(final_generated_plan, os.path.join(results_problem_dir, "plan_final.txt"))
                plan_length = len(final_generated_plan.split(", "))

        # Format refinements
        refinements_per_iteration_str = ";".join(map(str, refinements_per_iteration))

        # Save results to the main CSV file
        with open(csv_filepath, mode="a", newline='') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow([
                task_name, scene_name, problem_id, planning_successful, grounding_successful,
                plan_length, refinements_per_iteration_str,
                domain_generation_time, problem_generation_time,
                problem_refinement_time, total_llm_time,
                failure_stage, failure_reason
            ])

        # Save the possibility result if enabled
        if self.determine_possibility:
            with open(os.path.join(self.results_dir, self.experiment_name, self.timestamp, "possibility.csv"), mode="a", newline='') as f:
                writer = csv.writer(f, delimiter='|')
                writer.writerow([
                    task_name, scene_name, problem_id, task_possible,
                    possibility_explanation.strip().replace('\n', ' ').replace('\r', '')
                ])            
        return
    
    def grounded_planning(self, **kwargs):
        '''
        Grounded planning without goal relaxation.
        '''
        goal_file_path = kwargs.get("goal_file_path")
        initial_location_file_path = kwargs.get("initial_location_file_path")
        domain_file_path = kwargs.get("domain_file_path")
        results_dir = kwargs.get("results_dir")
        domain_description = kwargs.get("domain_description")

        # Optional arguments for multi-level planning
        current_goal_text = kwargs.get("current_goal_text") # If passed directly
        initial_robot_location_arg = kwargs.get("initial_robot_location")
        extracted_sg_str_arg = kwargs.get("extracted_sg_str")  # Environment description string

        # Approach A ablation flags
        clean_domain_prompt = kwargs.get("clean_domain_prompt", True)
        inject_domain_schema = kwargs.get("inject_domain_schema", True)
        check_adequacy = kwargs.get("check_adequacy", False)  # CoT adequacy checks (domain + problem)
        
        # Harmonized High-Level Planner Data
        hl_domain = kwargs.get("hl_domain")
        hl_problem = kwargs.get("hl_problem")
        hl_actions = kwargs.get("hl_actions")
        hl_goal = kwargs.get("hl_goal")
        hl_constraints = kwargs.get("hl_constraints")

        # Resolve initial_robot_location: explicit kwarg takes priority, then read from file
        initial_robot_location = initial_robot_location_arg
        if initial_robot_location is None and initial_location_file_path:
            if os.path.exists(initial_location_file_path):
                initial_robot_location = open(initial_location_file_path).read().strip()

        # Initialize timing variables
        domain_generation_time = 0.0
        problem_generation_time = 0.0
        problem_refinement_time = 0.0

        # Determine scene/environment description
        extracted_sg_str = extracted_sg_str_arg if extracted_sg_str_arg else ""
        
        # Construct domain description for generation
        domain_description = kwargs.get("domain_description")
        if not domain_description and hl_domain:
             domain_description = f"Domain: {hl_domain}"
             if hl_actions:
                 domain_description += f"\nActions: {hl_actions}"
        
        if current_goal_text:
            current_goal = current_goal_text
        elif hl_goal and hl_constraints:
             # Construct goal from HL data if available and not passed explicitly
             current_goal = f"Goal: {hl_goal}\nConstraints: {hl_constraints}"
        else:
            current_goal = open(goal_file_path, "r").read()

            

        
        # Initialize workflow variables
        planning_successful = False
        grounding_successful = False

        pddlenv_error_log = None
        planner_error_log = None
        VAL_validation_log = None
        planner_statistics = None
        
        task_possible = None
        possibility_explanation = ""
        
        refinements_per_iteration = []
        
        # Single iteration (no relaxation loop)
        iteration = 0
        
        # Reset VAL-related flags
        VAL_grounding_successful = False
        
        logger.info(f"------------ Grounded Planning ------------")
        
        iteration_dir = os.path.join(results_dir, f"iteration_{iteration}")
        os.makedirs(iteration_dir, exist_ok=True)
        
        problem_dir = os.path.join(iteration_dir, "refinement_0")
        os.makedirs(problem_dir, exist_ok=True)

        problem_file_path = os.path.join(problem_dir, "problem.pddl")
        
        if domain_file_path is None:
            domain_file_path = os.path.join(iteration_dir, "generated_domain.pddl")

        logs_dir = os.path.join(iteration_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        

                    
        if domain_description is not None:
            logger.info("Generating domain")
            domain_start_time = time.time()
            generate_domain(
                domain_file_path=domain_file_path,
                goal_file_path=goal_file_path if goal_file_path else None,
                domain_description=domain_description if domain_description else f"{hl_domain}\n{hl_actions}" if hl_domain and hl_actions else None,
                agent=self.agent,
                logs_dir=logs_dir,
                clean_domain_prompt=clean_domain_prompt,
            )

            domain_generation_time += time.time() - domain_start_time

            # Check domain with VAL using helper method
            VAL_successful, VAL_validation_log = self._check_val(domain_file_path)

            # Adequacy check: can the generated domain represent the observed world?
            if check_adequacy and current_goal:
                domain_pddl = open(domain_file_path).read()
                amended_domain = check_domain_adequacy(
                    domain_pddl=domain_pddl,
                    raw_observation=current_goal,
                    objects_list="",
                    agent=self.agent,
                    logs_dir=logs_dir,
                )
                if amended_domain != domain_pddl:
                    with open(domain_file_path, "w") as _f: _f.write(amended_domain)
                    VAL_ok, _vlog = self._check_val(domain_file_path)
                    if not VAL_ok:
                        logger.warning("Domain adequacy amendment broke VAL; reverting.")
                        with open(domain_file_path, "w") as _f: _f.write(domain_pddl)
                    else:
                        domain_generation_time += 0  # time already counted above

            self.current_phase = "DOMAIN_GENERATION"
            save_statistics(
                dir=results_dir,
                workflow_iteration=iteration,
                phase=self.current_phase,
                VAL_validation_log=VAL_validation_log,
                domain_generation_time=domain_generation_time
            )

        logger.info("Generating problem")
        problem_start_time = time.time()
        generate_problem(
            domain_file_path=domain_file_path,
            task=current_goal,
            environment=extracted_sg_str,
            problem_file_path=problem_file_path,
            logs_dir=logs_dir,
            workflow_iteration=iteration,
            agent=self.agent,
            ADD_PREDICATE_UNDERSCORE_EXAMPLE=(domain_description is not None or (hl_domain is not None and hl_actions is not None)),
            inject_domain_schema=inject_domain_schema,
        )

        problem_generation_time += time.time() - problem_start_time

        # Adequacy check: does the generated problem correctly encode the observed state?
        if check_adequacy and current_goal:
            problem_pddl = open(problem_file_path).read()
            domain_pddl = open(domain_file_path).read()
            amended_problem = check_problem_adequacy(
                problem_pddl=problem_pddl,
                domain_pddl=domain_pddl,
                raw_observation=current_goal,
                objects_list="",
                agent=self.agent,
                logs_dir=logs_dir,
            )
            if amended_problem != problem_pddl:
                with open(problem_file_path, "w") as _f: _f.write(amended_problem)

        # Check problem and domain with VAL using helper method
        VAL_successful, VAL_validation_log = self._check_val(domain_file_path, problem_file_path)
        
        plan_file_path = os.path.join(problem_dir, "plan_0.out")
        planner_output_file_path = os.path.join(problem_dir, "logs", "planner_output_0.log")
        
        plan, pddlenv_error_log, planner_error_log, planner_statistics = plan_with_output(
            domain_file_path, problem_dir, plan_file_path,
            planner_name="up_fd", search_flag=None, timeout=self.planner_timeout
        )      
        planning_successful = plan is not None
        
        # Check planning with VAL (outer loop version) using helper method.
        VAL_successful, VAL_validation_log, VAL_ground_successful, VAL_grounding_log = \
            self._check_val_planning(domain_file_path, problem_file_path, plan_file_path, 
                                    translation_suffix=str(iteration), problem_dir=problem_dir)
        VAL_grounding_successful = VAL_successful and VAL_ground_successful
            
        self.current_phase = "INITIAL_PLANNING"
        save_statistics(
            dir=results_dir,
            workflow_iteration=iteration,
            plan_successful=(plan is not None),
            pddlenv_error_log=pddlenv_error_log,
            planner_error_log=planner_error_log,
            VAL_grounding_log=VAL_grounding_log,
            VAL_validation_log=VAL_validation_log,
            planner_statistics=planner_statistics,
            phase=self.current_phase
        )

        # Logging the exact status before deciding on refinement
        logger.debug(f"[REFINEMENT CHECK] planning_successful: {planning_successful}, VAL_grounding_successful: {VAL_grounding_successful}")

            
        # Inner loop (PDDL Refinement)
        PDDL_loop_iteration = 0
        
        # Explicit check: If both succeeded, skip refinement entirely
        should_refine = not planning_successful or not VAL_grounding_successful
        
        if should_refine:
            if not planning_successful:
                logger.info("Entering PDDL refinement because initial planning failed (plan is None).")
            elif not VAL_grounding_successful:
                logger.info("Entering PDDL refinement because initial plan failed VAL validation or grounding.")
            
            self.current_phase = "PDDL_REFINEMENT"
                
            while PDDL_loop_iteration < self.pddl_gen_iterations and \
                (not planning_successful or not VAL_grounding_successful):
                logger.info(f"------------ Refinement iteration {PDDL_loop_iteration+1}/{self.pddl_gen_iterations} ------------")

                logger.debug(f"Problem directory: {problem_dir}")
                    
                logger.info("Refining problem")
                refinement_start_time = time.time()
                new_problem, _refinement_history = refine_problem(
                    domain_file_path=domain_file_path,
                    problem_file_path=problem_file_path,
                    scene_graph=extracted_sg_str,
                    task=current_goal,
                    logs_dir=logs_dir,
                    workflow_iteration=iteration,
                    refinement_iteration=PDDL_loop_iteration,
                    agent=self.agent,
                    pddlenv_error_log=pddlenv_error_log,
                    planner_error_log=planner_error_log,
                    VAL_validation_log=VAL_validation_log,
                    VAL_grounding_log=VAL_grounding_log,
                )
                problem_refinement_time += time.time() - refinement_start_time
                    
                new_problem_dir = str(Path(problem_dir).parent / f"refinement_{PDDL_loop_iteration+1}")
                os.makedirs(new_problem_dir, exist_ok=True)
                    
                new_problem_file_path = os.path.join(new_problem_dir, "problem.pddl")
                    
                logger.debug(f"Saving new problem to {new_problem_file_path}")
                with open(new_problem_file_path, "w") as file:
                    file.write(new_problem)
                        
                problem_dir = new_problem_dir
                problem_file_path = new_problem_file_path
                PDDL_loop_iteration += 1
                    
                # Check new planning phase
                plan_file_path = os.path.join(problem_dir, f"plan_{PDDL_loop_iteration}.out") 
                planner_output_file_path = os.path.join(problem_dir, "logs", f"planner_output_{PDDL_loop_iteration}.log")
                    
                # Attempt planning with refined problem
                plan, pddlenv_error_log, planner_error_log, planner_statistics = plan_with_output(
                    domain_file_path, problem_dir, plan_file_path,
                    planner_name="up_fd", timeout=self.planner_timeout
                )
                planning_successful = plan is not None
                    
                # Check planning with VAL (inner loop version)
                VAL_successful, VAL_validation_log, VAL_ground_successful, VAL_grounding_log = \
                    self._check_val_planning(domain_file_path, problem_file_path, plan_file_path, 
                                            translation_suffix=f"{PDDL_loop_iteration}", problem_dir=problem_dir)
                VAL_grounding_successful = VAL_successful and VAL_ground_successful
                    
                save_statistics(
                    dir=results_dir,
                    workflow_iteration=iteration,
                    plan_successful=(plan is not None),
                    pddlenv_error_log=pddlenv_error_log,
                    planner_error_log=planner_error_log,
                    planner_statistics=planner_statistics,
                    phase=self.current_phase,
                    pddl_refinement_iteration=PDDL_loop_iteration,
                    VAL_grounding_log=VAL_grounding_log,
                    VAL_validation_log=VAL_validation_log
                )
        else:
            planning_successful = True
            pddlenv_error_log = None
            planner_error_log = None
            planner_statistics = None
            
        # Record the number of refinements
        refinements_per_iteration.append(PDDL_loop_iteration)
            
        if planning_successful and VAL_grounding_successful:
            logger.info("Planning and grounding successful")
            grounding_successful = True
        else:
            logger.info("Out of PDDL refinements")

        # Calculate total LLM time
        total_llm_time = domain_generation_time + problem_generation_time + problem_refinement_time
        
        # Save total inference time statistics
        save_statistics(
            dir=results_dir,
            workflow_iteration=iteration,
            phase="TOTAL_INFERENCE",
            domain_generation_time=domain_generation_time,
            problem_generation_time=problem_generation_time,
            problem_decomposition_time=problem_refinement_time,
            total_inference_time=total_llm_time
        )
        
        # Return final problem and plan
        return (problem_file_path, plan_file_path,
                planning_successful, grounding_successful, task_possible,
                possibility_explanation, refinements_per_iteration,
                domain_generation_time, problem_generation_time, problem_refinement_time, total_llm_time,
                "", "")

        
    def _check_val(self, domain_file_path, problem_file_path=None):
        """
        Helper method to perform VAL validation.
        """
        if problem_file_path:
            logger.info("Checking problem and domain with VAL")
            VAL_successful, VAL_validation_log = VAL_validate(domain_file_path, problem_file_path)
        else:
            logger.info("Checking domain with VAL")
            VAL_successful, VAL_validation_log = VAL_validate(domain_file_path)
        if not VAL_successful:
            logger.info("VAL validation check failed")
            logger.debug(VAL_validation_log)
        else:
            logger.info("VAL validation check passed")
        return VAL_successful, VAL_validation_log


    def _check_val_planning(self, domain_file_path, problem_file_path, plan_file_path, translation_suffix, problem_dir):
        """
        Helper method to perform VAL validation and grounding for planning.
        """
        # Translate the plan into a format parsable by VAL
        translated_plan_path = os.path.join(problem_dir, f"translated_plan_{translation_suffix}.txt")
        translate_plan(plan_file_path, translated_plan_path)
        logger.info("Checking planning with VAL")
        VAL_successful, VAL_validation_log = VAL_validate(domain_file_path, problem_file_path, translated_plan_path)
        if VAL_successful:
            logger.info("VAL validation check passed")
            logger.info("Attempting to ground the plan")
            VAL_ground_successful, VAL_grounding_log = VAL_ground(domain_file_path, problem_file_path)
            if VAL_ground_successful:
                logger.info("Plan is grounded")
            else:
                logger.info("Plan is not grounded")
                logger.debug(VAL_grounding_log)
        else:
            logger.info("VAL validation check failed")
            logger.debug(VAL_validation_log)
            VAL_ground_successful = False
            VAL_grounding_log = None
        return VAL_successful, VAL_validation_log, VAL_ground_successful, VAL_grounding_log
