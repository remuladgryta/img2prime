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


def find_next_prime(number, quiet=True):
    i = 1
    while not miller_rabin(number):
        if not quiet:
            print("checked {} candidates".format(i))
        i += 1
        number += 2
    return number


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Convert an image to ascii art digits and find a prime number close to it."
    )
    parser.add_argument('image')
    parser.add_argument('-c', '--charset', default='8045692317')
    parser.add_argument('-q', '--quiet', action='store_true')
    args = parser.parse_args()

    image = Image.open(args.image)
    ascii = to_ascii_art(image, linear_map(range(256), args.charset))
    if not args.quiet:
        print("Base ascii art: \n\n{}".format(ascii))

    number = int(ascii.replace('\n', ''))
    prime = find_next_prime(number, args.quiet)
    if not args.quiet:
        print("Prime found!")
    print(textwrap.fill(str(prime), image.width))
