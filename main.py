import argparse

from state_machine import generate_score


def main():
    parser = argparse.ArgumentParser(description='Generate score for an exercise.')
    parser.add_argument('--steps_path', type=str, required=True, help='Path to the exercise steps CSV file')
    parser.add_argument('--answers_path', type=str, required=True, help='Path to the exercise answers CSV file')
    parser.add_argument('--exercise_type_id', type=int, required=True, help='Selected exercise type ID to filter')
    parser.add_argument('--student_id', type=int, required=True,  help='Selected student ID to filter')
    parser.add_argument('--weight', type=float, nargs='?', default=0.01,
                        help='Weight for exercise not finished to subtract points (default: 0.01)')
    parser.add_argument('--graph', action='store_true',
                        help='Selected if you want to generate a graph (default: False)')
    parser.add_argument('--K', type=int, nargs='?', default=6,
                        help='Selected number of incorrect answers before reducing score (default: 6)')

    args = parser.parse_args()

    generate_score(args.steps_path, args.answers_path, args.exercise_type_id,
                   args.weight, args.student_id, args.K, args.graph)


if __name__ == '__main__':
    main()
