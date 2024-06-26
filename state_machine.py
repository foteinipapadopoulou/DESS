import math
from collections import defaultdict
from copy import deepcopy

import pandas as pd
from transitions import Machine
from transitions.extensions import GraphMachine
import os
import platform

if platform.system() == "Windows":
    os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'


class CustomGraphMachine(GraphMachine):
    """
    Code adapted from https://github.com/pytransitions/transitions/blob/master/examples/Frequently%20asked%20questions.ipynb
    """

    # Override Graphmachine's default styling for nodes and edges [1]
    # Copy default graph attributes but change direction to top to bottom
    machine_attributes = deepcopy(GraphMachine.machine_attributes)
    machine_attributes["rankdir"] = "TB"  # Left to right layout

    # Reset styling
    style_attributes = defaultdict(dict)
    style_attributes["node"]["default"] = {"fontname": "arial", "shape": "circle"}
    style_attributes["edge"]["default"] = {"fontname": "arial"}


class StateMachine(object):
    def __init__(self, exercise_steps, K=6, graph_machine=False):
        self.score = 0
        self.state = None
        self.steps = exercise_steps.set_index('step_id')  # get all the steps based on the step_id
        self.transitions = []
        self.primary_path, self.max_score = self.get_correctness_path_score()
        self.answered_questions = {}
        self.K = K
        self.depth = {}
        self.hint_states = self.get_hint_states()

        for step_id in self.primary_path:
            self.depth[step_id] = 0
            self.get_depth_level(step_id)

        for step_id, step in self.steps.iterrows():
            weight = step.get('weight', 1)  # Default weight is 1 if not specified
            question_score = step.get('score', 0)
            if self.is_hint(step):
                self.handle_hint(step_id, step, weight, question_score)
            else:
                self.handle_question(step_id, step, weight, question_score)

        # Initialize the state machine
        states = ['start'] + list(map(str, self.steps.index.unique())) + ['end']
        initial_state = str(list(self.steps[self.steps['is_first_step']].index)[0])
        # connect start with the first step
        transition = {
            'trigger': 'initialization',
            'source': 'start',
            'dest': str(initial_state),
        }
        self.transitions.append(transition)
        if graph_machine:
            self.machine = CustomGraphMachine(model=self, states=states,
                                              initial='start',
                                              transitions=self.transitions,
                                              auto_transitions=False,
                                              )
        else:
            self.machine = Machine(model=self, states=states,
                                   initial='start',
                                   transitions=self.transitions,
                                   auto_transitions=False,
                                   )

    def get_depth_level(self, source):
        """
        Use Breadth First Search to determine the level of each question
        """
        Q = []
        Q.append(source)
        visited = []
        visited.append(source)

        while Q:
            s = Q.pop(0)

            rows = self.steps[self.steps.index == s]
            rows = rows.reset_index()

            for index, row in rows.iterrows():
                if not math.isnan(row.possible_answer_next_step_id) or not math.isnan(row.step_next_step_id):
                    next_step_id = row.possible_answer_next_step_id
                    if math.isnan(row.possible_answer_next_step_id):
                        next_step_id = row.step_next_step_id
                    if next_step_id not in visited and next_step_id not in self.primary_path:
                        Q.append(int(next_step_id))
                        visited.append(int(next_step_id))
                        self.depth[int(next_step_id)] = self.depth[s] + 1

    def path_correctness(self, step_id, path, score):
        """
        Calculate the maximum path score by iterating over the path
        """
        rows = self.steps[self.steps.index == step_id]
        rows = rows.reset_index()

        for index, row in rows.iterrows():

            if math.isnan(row.possible_answer_next_step_id) and math.isnan(
                    row.step_next_step_id):  # the end of an exercise
                if not math.isnan(row.score):
                    score += row.score
                return path, score
            elif math.isnan(row.possible_answer_next_step_id):  # the path of correctness contains a hint
                path.append(int(row.step_next_step_id))
                return self.path_correctness(row.step_next_step_id, path, score)
            elif row.answer_interpretation == "correct":
                path.append(int(row.possible_answer_next_step_id))
                score += row.score
                return self.path_correctness(row.possible_answer_next_step_id, path, score)

    def get_correctness_path_score(self):
        """
        Find the first steps of the exercise
        Calculate the scores based on the correctness path
        """
        first_steps = self.steps[self.steps.is_first_step == True]
        initial_score = 0
        step_id_initial_step = first_steps.index[0]
        initial_path = [int(step_id_initial_step)]
        path, score = self.path_correctness(step_id_initial_step, initial_path, initial_score)
        return path, score

    def is_hint(self, data):
        """
        Check if the step is a hint
        A hint is a step that does not have a possible_answer_id,
        possible_answer_next_step_id, score, format, answer_text, and answer_interpretation
        """
        return pd.isna(data['score']) and pd.isna(data['possible_answer_id']) \
            and pd.isna(data['possible_answer_next_step_id']) and pd.isna(data['answer_text']) and pd.isna(
                data['answer_interpretation'])

    def handle_hint(self, step_id, data, weight, score):
        """
        Handle the hint step and create the transitions for the possible answers
        If it doesn't have a next step, it will go to the end
        """
        next_state = data['step_next_step_id'] if pd.notna(data['step_next_step_id']) else 'end'
        self.create_transition(step_id, next_state, 'auto_proceed', weight, 'neutral', score)

    def handle_question(self, step_id, data, weight, score):
        """
        Handle the question step and create the transitions for the possible answers
        If it doesn't have a next step, it will go to the end
        it adds a trigger suffix based on the answer interpretation
        """
        trigger_suffix = ''
        if data['answer_interpretation'] == 'correct':
            trigger_suffix = 'correct_answer'
        elif data['answer_interpretation'] == 'incorrect':
            trigger_suffix = 'incorrect_answer'
        elif data['answer_interpretation'] == 'neutral':
            trigger_suffix = 'neutral_answer'

        next_state = data['possible_answer_next_step_id'] if pd.notna(data['possible_answer_next_step_id']) else 'end'

        self.create_transition(step_id, next_state, f'answer_{int(data["possible_answer_id"])}_{trigger_suffix}',
                               weight, data['answer_interpretation'], score)

    def create_transition(self, source, dest, trigger, weight, interpretation, score):
        """
        Create a transition with the given parameters
        If dest is NaN, it will be set to 'end'
        """
        if pd.isna(dest):
            dest = "end"

        if dest != "end":
            dest = str(int(dest))

        path_type = 'primary'
        if self.depth[int(source)] > 1:
            path_type = 'helper'

        transition = {
            'trigger': trigger,
            'source': str(source),
            'dest': str(dest),
            'before': lambda: self.update_score(weight, interpretation, score, str(source), path_type),
        }
        self.transitions.append(transition)

    def update_score(self, weight, interpretation, score, id, path_type):
        """
        Update the score based on the interpretation and how many times the student has tried the question
        """

        if id not in self.answered_questions:
            self.answered_questions[id] = 1
        else:
            self.answered_questions[id] += 1

        count = self.answered_questions[id]
        new_score = self.score
        ### IS primary
        if interpretation == 'correct' and count == 1 and path_type == 'primary':
            new_score += score
        elif interpretation == 'correct' and count > 1 and path_type == 'primary':
            new_score += round(score / count, 1)
        ### IS Helper
        if interpretation == 'correct' and count == 1 and path_type == 'helper':
            new_score += round(score / self.depth[int(id)], 1)
        elif interpretation == 'correct' and count > 1 and path_type == 'helper':
            new_score += round(score / self.depth[int(id)], 1) * round(score / count, 1)
            # is incorrect multiple times
        elif interpretation == 'incorrect' and count == self.K:
            new_score -= score * count * 0.1

        self.score = min(new_score, self.max_score)
        self.score = max(0, self.score)

    def show_graph(self, filename='state_diagram'):
        # Draw the state diagram
        graph = self.machine.get_graph()
        graph.node_attr.update(fillcolor="turquoise")
        graph.edge_attr.update(color="blue")
        graph.draw(f'{filename}.png', prog='dot', args='-Gnodesep=1')

    def get_hint_states(self):
        # Returns a set of all hint states
        return {str(step_id) for step_id, data in self.steps.iterrows() if self.is_hint(data)}

    def process_responses(self, exercise_answers):

        for index, response in exercise_answers.iterrows():

            while self.state in self.hint_states and self.machine.get_triggers(self.state):
                trigger_method = getattr(self, 'auto_proceed')
                trigger_method()

            # search the possible triggers for the current state
            possible_triggers = [t for t in self.machine.get_triggers(self.state) if
                                 f'answer_{response["possible_answer_id"]}' in t]
            if possible_triggers:
                # Execute the first relevant trigger found
                trigger_method = getattr(self, possible_triggers[0])
                trigger_method()


def generate_score(exercise_steps_path, exercise_answers_path, selected_exercise_type_id, weight_exercise_not_finished,
                   select_student_id, K=6, graph_machine=False):
    exercise_steps = pd.read_csv(exercise_steps_path)
    exercise_answers = pd.read_csv(exercise_answers_path)

    # Filter steps and answers for the specific exercise
    specific_exercise_steps = exercise_steps[exercise_steps['exercise_type_id'] == selected_exercise_type_id]
    specific_exercise_answers = exercise_answers[(exercise_answers['exercise_type_id'] == selected_exercise_type_id) &
                                                 (exercise_answers['student_id'] == select_student_id)]
    sorted_answers = specific_exercise_answers.sort_values(by='ans_inserted_at')

    # group them by the exercise_tracking_id
    grouped_answers = sorted_answers.groupby('exercise_tracking_id')

    for tracking_id, attempt_data in grouped_answers:
        attempt_data = attempt_data.sort_values(by='ans_inserted_at')

        print(f"Processing answers for tracking ID: {tracking_id}")
        # Instantiate the state machine with the specific exercise steps
        sm = StateMachine(exercise_steps=specific_exercise_steps, K=K, graph_machine=graph_machine)
        # trigger the initialization transition
        sm.initialization()

        # Process each answer for the exercise
        sm.process_responses(attempt_data)

        if not attempt_data['is_exercise_finished'].iloc[0]:
            sm.score = max(0, sm.score - (sm.max_score * weight_exercise_not_finished))
        print(f"Total score for the exercise: {sm.score}")
    if graph_machine:
        sm.show_graph('state_diagram')


if __name__ == '__main__':
    # Load CSV files
    exercise_steps_path = 'files/exercise_steps_2024-05-27T07_18_53.350009Z.csv'
    exercise_answers_path = 'files/exercise_answers_2024-06-17T10_21_22.864852Z.csv'

    # Select a specific exercise_type_id to filter
    selected_exercise_type_id = 1497
    # Set the weight for the exercise not finished to subtract points
    weight_exercise_not_finished = 0.01
    # Select a student ID to filter
    select_student_id = 1447
    generate_score(exercise_steps_path, exercise_answers_path,
                   selected_exercise_type_id, weight_exercise_not_finished, select_student_id, True)
