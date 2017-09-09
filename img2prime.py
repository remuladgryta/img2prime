from PIL import Image
import argparse
import random
import textwrap


def to_ascii_art(image, mapping):
    """Convert each pixel in an image to a character."""
    ascii_art = ''
    for y in range(image.height):
        for x in range(image.width):
            "assuming a greyscale image, so we'll only use the first channel"
            value = image.getpixel((x, y))[0]
            ascii_art += mapping[value]
        ascii_art += '\n'
    return ascii_art


def linear_map(inputs, outputs):
    ratio = len(outputs)/len(inputs)
    mapping = {}
    for index, value in enumerate(inputs):
        mapping[value] = outputs[int(index*ratio)]
    return mapping


def probably_prime(
    number,
    primes=[
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
        67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137,
        139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211,
        223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283,
        293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379,
        383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461,
        463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563,
        569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643,
        647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739,
        743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829,
        839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937,
        941, 947, 953, 967, 971, 977, 983, 991, 997
    ]
):
    """Check if a number is probably prime."""
    for prime in primes:
        "Rule out candidates with small prime factors first"
        if number % prime == 0:
            return False
    "If the candidate might still be prime, use the more costly Miller-Rabin"
    return miller_rabin(number)


def skipahead(test_function, args):
    skip = args.skip
    quiet = args.quiet
    "mute everything until we've skipped"
    args.quiet = True
    skipped = 0

    def f(number):
        nonlocal skipped
        if skipped < skip:
            if not quiet and skipped % 1000 == 0:
                if skipped == 0:
                    print('Skipping ahead...', end='')
                else:
                    print('.', end='', flush=True)
            skipped += 1
            if skipped == skip:
                args.quiet = quiet
            return False
        else:
            return test_function(number)
    return f


def find_next_prime(number, args, test_function=probably_prime):
    i = 1
    while not test_function(number):
        if not args.quiet:
            print("checked {} candidates".format(i))
        i += 1
        number += 2
    return number


def find_prime_by_morphing(
        number,
        args,
        printer=print,
        test_function=probably_prime
):
    trials = 0
    morphs = {morph[0]: morph[1:] for morph in args.morph}

    def find_prime_by_morphing_recursive(number, recursion_depth):
        nonlocal trials
        digits = list(str(number))
        for index in range(len(digits)):
            digit = digits[-index]
            if index >= recursion_depth:
                break
            try:
                for morph in morphs[digit]:
                    morphed = list(digits)
                    morphed[-index] = morph
                    morphed = ''.join(morphed)
                    if not args.quiet:
                        printer('Tested {} numbers so far.'.format(trials))
                        printer(morphed)
                    if test_function(int(morphed)):
                        return int(morphed)
                    trials += 1
                    prime = find_prime_by_morphing_recursive(
                        morphed,
                        recursion_depth=index,
                    )
                    if prime:
                        return prime
            except KeyError:
                continue

    return find_prime_by_morphing_recursive(
        number,
        recursion_depth=len(str(number)),
    )


def miller_rabin(n, k=10):
    """Check if a number n is probaby prime.

       See https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test
    """
    r = 1
    d = (n-1) // 2
    while d % 2 == 0:
        d //= 2
        r *= 2
    for i in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for j in range(r-1):
            x = pow(x, 2, n)
            if x == 1:
                return False
            if x == n - 1:
                continue
        return False
    return True


def prettyprinter(width):
    def pretty(s):
        print(textwrap.fill(s, width))
    return pretty


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Convert an image to ascii art digits and find a prime number close to it."
    )
    parser.add_argument('image')
    parser.add_argument(
        '-c', '--charset', default='8045692317',
        help="Which digits should be used to represent the image, "
             "in ascending order of brightness. default=%(default)s"
    )
    parser.add_argument('-q', '--quiet', action='store_true')
    parser.add_argument(
        '-s', '--skip', type=int, metavar='N', default=0,
        help="Skip testing the first N numbers generated."
    )
    g = parser.add_argument_group('methods')
    methods = g.add_mutually_exclusive_group()
    methods.add_argument(
        '-m', '--morph', nargs='+',
        help="Generate candidates by changing only certain digits in the "
             "ascii art image into certain other digits. Each morph is on the "
             "form MORP... and specifies that the digit M is allowed to "
             "change into any of the digits O, R, P, etc."
    )
    methods.add_argument(
        '-a', '--ascending', action='store_true',
        help="Generate candidates by incrementing the previous one by 2. "
             "(this is the default method)"
    )
    args = parser.parse_args()

    image = Image.open(args.image)
    ascii = to_ascii_art(image, linear_map(range(256), args.charset))
    if not args.quiet:
        print("Base ascii art: \n\n{}".format(ascii))

    number = int(ascii.replace('\n', ''))

    test_function = probably_prime
    if args.skip:
        test_function = skipahead(test_function, args=args)

    if args.morph:
        prime = find_prime_by_morphing(
            number,
            args=args,
            printer=prettyprinter(image.width),
            test_function=test_function
        )
    else:
        prime = find_next_prime(number, args, test_function=test_function)
    if not args.quiet:
        print("Prime found!")
    print(textwrap.fill(str(prime), image.width))
