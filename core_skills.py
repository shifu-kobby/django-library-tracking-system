import random
# rand_list =
# assuming 20 is inclusive
random_numbered_list = random.sample(range(1, 21), 10)

list_comprehension_below_10 = [number for number in random_numbered_list if number < 10]

list_comprehension_below_10_using_filter = list(filter(lambda x: x < 10, random_numbered_list))