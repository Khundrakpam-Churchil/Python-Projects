import Number_guesing

quiz_data = [
    ("What is 5 + 7?", "12"),
    ("What is the capital of France?", "paris"),
    ("Which animal is known as the King of the Jungle?", "lion")
]

quiz_score = 0
last_quiz_score = 0
last_quiz_details = []


def run_quiz():
    global quiz_score, last_quiz_score, last_quiz_details
    quiz_score = 0
    last_quiz_details = []
    print("\nWelcome to the Simple Quiz!")

    for question, answer in quiz_data:
        user_answer = input(f"\n{question} ").strip().lower()
        correct = user_answer == answer
        last_quiz_details.append((question, user_answer, answer, correct))

        if correct:
            print("Correct! 🎉")
            quiz_score += 1
        else:
            print(f"Wrong! The correct answer is: {answer.capitalize()}.")

    last_quiz_score = quiz_score
    print(f"\nYour final score is: {quiz_score}/{len(quiz_data)}")


def show_last_results():
    print("\nLast Results")
    print("--------------")
    if last_quiz_details:
        print(f"Last quiz score: {last_quiz_score}/{len(quiz_data)}")
    else:
        print("No quiz played yet.")

    if Number_guesing.last_result == "win":
        print(f"Last guessing game: guessed {Number_guesing.last_number} in {Number_guesing.last_attempts} attempts.")
        print(f"Last hint given: {Number_guesing.last_hint}")
    else:
        print("No number guessing game completed yet.")


def main_menu():
    while True:
        print("\n===== Game Menu =====")
        print("1. Play Simple Quiz")
        print("2. Play Number Guessing Game")
        print("3. Show Last Results")
        print("4. Exit")

        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            run_quiz()
        elif choice == "2":
            Number_guesing.run_number_guessing_game()
        elif choice == "3":
            show_last_results()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main_menu()
