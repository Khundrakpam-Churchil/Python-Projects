import random

number_to_guess = None
attempts = 0
last_result = None
last_attempts = 0
last_number = None
last_hint = ""


def init_number_guessing_game():
    global number_to_guess, attempts, last_result, last_hint
    number_to_guess = random.randint(1, 100)
    attempts = 0
    last_result = None
    last_hint = ""
    print("\nWelcome to the Number Guessing Game!")
    print("I have selected a random number between 1 and 100. Can you guess it?")


def run_number_guessing_game():
    global attempts, last_result, last_attempts, last_number, last_hint
    init_number_guessing_game()

    while True:
        try:
            user_guess = int(input("\nEnter your guess: "))
            attempts += 1

            if user_guess < number_to_guess:
                print("Too low! Try again.")
            elif user_guess > number_to_guess:
                print("Too high! Try again.")
            else:
                last_result = "win"
                last_attempts = attempts
                last_number = number_to_guess
                print(f"🎉 Congratulations! You've guessed the number {number_to_guess} in {attempts} attempts!")
                break

            if attempts == 3:
                if number_to_guess % 2 == 0:
                    last_hint = "EVEN"
                    print("💡 Hint: The secret number is EVEN.")
                else:
                    last_hint = "ODD"
                    print("💡 Hint: The secret number is ODD.")
            elif attempts == 6:
                divisors = [i for i in range(2, 11) if number_to_guess % i == 0]
                if divisors:
                    divisor_hint = random.choice(divisors)
                    last_hint = f"multiple of {divisor_hint}"
                    print(f"💡 Hint: The secret number is a multiple of {divisor_hint}.")
                else:
                    last_hint = "prime or does not divide cleanly under 11"
                    print("💡 Hint: The secret number is a prime number (or doesn't divide cleanly by anything under 11)!")

        except ValueError:
            print("Please enter a valid integer.")


if __name__ == "__main__":
    run_number_guessing_game()
    