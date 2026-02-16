import random
import string

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    random_str = ''.join(random.choices(letters_and_digits, k=length))
    return random_str
