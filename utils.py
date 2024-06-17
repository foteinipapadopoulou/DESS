import math
import pandas as pd


def extract_exercise_df(exercise_steps, exercise_id):
    """
    Extract an exercise dataframe based on the exercise_id
    """
    return exercise_steps[exercise_steps.exercise_type_id == exercise_id]


def find_first_step(exercise):
    """
    Find the rows from the dataframe that are the first step
    """
    return exercise[exercise.is_first_step == True]


def path_correctness(exercise, step_id, path, score):
    """
    Calculate the maximum path score by iterating over the path
    """
    rows = exercise[exercise.step_id == step_id]
    rows = rows.reset_index()

    for index, row in rows.iterrows():

        if math.isnan(row.possible_answer_next_step_id) and math.isnan(row.step_next_step_id):  # the end of an exercise
            if row.score != 0:
                score += row.score
            return path, score
        elif math.isnan(row.possible_answer_next_step_id):  # the path of correctness contains a hint
            path.append(row.step_next_step_id)
            return path_correctness(exercise, row.step_next_step_id, path, score)
        elif row.answer_interpretation == "correct":
            path.append(row.possible_answer_next_step_id)
            score += row.score
            return path_correctness(exercise, row.possible_answer_next_step_id, path, score)


def get_correctness_path_score(exercise):
    """
    Find the first steps of the exercise
    Calculate the scores based on the correctness path
    """
    first_steps = find_first_step(exercise)
    initial_path = []
    initial_score = 0
    step_id_initial_step = first_steps.iloc[0].step_id
    path, score = path_correctness(exercise, step_id_initial_step, initial_path, initial_score)
    return path, score


def calculate_max_score(exercises_steps, exercise_id):
    """
    Calculate the maximum score of an exercise based on the correctness path
    """
    specific_exercise = extract_exercise_df(exercises_steps, exercise_id)
    path, max_score = get_correctness_path_score(specific_exercise)
    print(f"Max score of exercise with ID: {exercise_id} = {max_score}")
    return max_score


if __name__ == '__main__':
    # Load the data
    exercise_steps = pd.read_csv("files/exercise_steps_2024-05-27T07_18_53.350009Z.csv")
    exercise_id = 1497
    max_score = calculate_max_score(exercise_steps, exercise_id)
    print(max_score)