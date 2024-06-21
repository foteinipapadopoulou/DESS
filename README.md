# Digital Evaluation Subsystem

## Description
In this repository, we have built a script that is based on state machine logic to calculate  individual scores for exercises created from the Enlight Ed software based on the responses provided in CSV files. The script filters responses by exercise type and student ID to provide targeted insights into individual performance and progress. The script also generates a visual diagram of the state machine to help visualize the state transitions.

## Setup
Ensure that Python 3 is installed on your system.

If you want to generate a visual diagram of the state machine, you will need to install the `graphviz` package. You can install it using the following instructuions based on your operating system:
* Windows:
  * Navigate to the [Graphviz download page](https://graphviz.gitlab.io/_pages/Download/Download_windows.html) 
  * Download the EXE installer(32-bit or 64-bit)
* Linux: 
  * ```bash
    sudo add-apt-repository universe --yes > /dev/null 2>&1
    sudo apt update --yes -q
    sudo apt-get install graphviz graphviz-dev --yes -q
    ```



### Dependencies
- Python 3
- pandas
- transitions
- graphviz

Install required Python packages using the following command:

```bash
pip install requirements.txt
```

## Usage

To run the script, you will need to provide paths to the CSV files containing the exercise steps and answers, along with the exercise type ID and student ID that you wish to filter by. Optionally, you can also specify a weight for exercises that are not completed and if you want to generate a visual diagram of the state machine.

**Command Line Arguments**

    --steps_path (required): The file path to the CSV containing the exercise steps.
    --answers_path (required): The file path to the CSV containing the answers.
    --exercise_type_id (required): The ID used to filter the exercise steps and answers.
    --student_id (required): The ID of the student to filter the scores.
    --weight (optional): A float representing the weight to subtract from the total score for exercises not completed. Default is 0.01.
    --graph (optional): A boolean flag to generate a visual diagram of the state machine. Default is False.
    --Κ (optional):  Attention threshold, an integer representing the number to allow students to input incorrect answers for the same question until lowering the total score. Default is 6.
## Example Command

Run the script using the following command template:

```bash
python main.py --steps_path .\files\exercise_steps_2024-05-27T07_18_53.350009Z.csv --answers_path .\files\exercise_answers_2024-06-17T10_21_22.864852Z.csv --exercise_type_id 1497 --student_id 1447 --weight 0.01 --graph
```

## Output

The script will output the calculated score directly to the console. If configured base on the graph flag, it also generates a visual diagram showing the state transitions based on the exercise named `state_diagram.png`.
### Example logs and generated scores
The following are example logs and generated scores for `exercise_type_id=1497` and `student_id=1447` provided in the file `exercise_answers_2024-06-17T10_21_22.864852Z.csv`:

```
Processing answers for tracking ID: 2024-05-21T08:56:37
Total score for the exercise: 30.0
Processing answers for tracking ID: 2024-05-21T08:57:34
Total score for the exercise: 0
Processing answers for tracking ID: 2024-05-21T11:40:57
Total score for the exercise: 30.0
Processing answers for tracking ID: 2024-05-25T09:50:21
Total score for the exercise: 25.0
Processing answers for tracking ID: 2024-05-25T09:51:12
Total score for the exercise: 9.7
```
* If the student id or the exercise type id is not found in the provided CSV files, the script will not output any logs or scores.
