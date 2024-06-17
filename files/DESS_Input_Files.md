# Master Challenge - DESS Input Files

The DESS challenge has two input files:

1. Exercise Structure input file (Exercise Steps.csv)
2. Exercise Answers input file (Exercise Answers.csv)

## Exercise Structure

The exercise structure input file captures the steps for an exercise steps and their connectivity.

It is a flattened representation of the exercise step directed graph. Each line in the file represents a step in an exercise. For question steps there is
one line for each possible answer, so for a question step with one correct and one incorrect answer is captured by two lines. Hint steps are captured in a single line.

The 10 fields of this CSV are:

| Field                 |                                   Description                                                                 |
------------------------|---------------------------------------------------------------------------------------------------------------
|exercise_type_id       |id of an exercise, steps with the same exercise_type_id belong to the same exercise                     |
|step_id                |id of an exercise step, a step can be a: question or a hint; quesitons can be multi-choice or free-text |
|step_text              |contains the text that is shown for the student when this step is active it is either the text of the question or of the hint|
|step_next_step_id      |filled in for hints, it is the id of the step that follows, for questions this field is null, if the field is null for a hint it means that the hint was the last step of the exercise|
|format                 |filled in for question steps, it can be multi-choice or free-form                                              |
|score                  |filled in for question steps, it is the score that the student gets for giving the correct answer, for hints this field is null|
|is_first_step          |flag indicating if this is the first step of the exercise, both hints and questions can be first steps         |
|possible_answer_id     |for question types, it is the id of the possible answer this line represents                                   |
|possible_answer_next_step_id| filled in for questions, it is the id of the step that follows, for hints this field is null, if the field is null for a question's possible answer, it means that giving this answer the exercise is finished|
|answer_text            | the text of the possible answer|
| answer_interpretation | meta-data indicating if the answer is correct, incorrect or neutral|

## Exercise Answers

The answers given by a user while solving an exercises are captured for each practice session. Every time a user starts an exercise, a new practice session is
created.

Some of the fields from exercise answers reference the exercise structure csv above.

The 10 fields of the CSV are:

| Field                 |                                   Description                                                                 |
------------------------|---------------------------------------------------------------------------------------------------------------
| id                    | id of an interaction where the user gave an answer|
| student_id            | id of the student giving the answer|
|exercise_tracking_id   | id of the practice session, the DESS score should be calculated for each session|
|possible_answer_id     | id of the answer the student gave, for free-text questions with 'other-answers' see the user_input for the actual value, same as in the exercise structure file|
|ans_inserted_at        | timestamp when the answer was captured|
|ans_user_input         | for free-text questions with 'other-answers' the value given by the student, otherwise empty|
|is_exercise_finished   | true when the student completed the exercise|
|exercise_tracking_started_at| timestamp for the start of the practice session|
|exerise_tracking_finished_at| timestamp for the end of the practice session|
|exercise_type_id| id of the exercise, same as in the exercise structure file|


