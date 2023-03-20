import json

# define the path to the JSON file
VEGETABLES_FILE = 'vegetables.json'

# initialize an empty list to store the vegetable data
vegetables = []

# load the existing data from the JSON file, if it exists
try:
    with open(VEGETABLES_FILE, 'r') as f:
        vegetables = json.load(f)
except FileNotFoundError:
    pass

def save_vegetables():
    """Saves the current vegetable data to the JSON file"""
    with open(VEGETABLES_FILE, 'w') as f:
        json.dump(vegetables, f)

def get_vegetable_by_id(vegetable_id):
    """Returns the vegetable entry with the specified ID, or None if not found"""
    for vegetable in vegetables:
        if vegetable['id'] == vegetable_id:
            return vegetable
    return None

def delete_vegetable_by_id(vegetable_id):
    """Deletes the vegetable entry with the specified ID"""
    for i, vegetable in enumerate(vegetables):
        if vegetable['id'] == vegetable_id:
            del vegetables[i]
            save_vegetables()
            break

def get_vegetable_by_name(name):
    """Returns the vegetable entry with the specified name, or None if not found"""
    for vegetable in vegetables:
        if vegetable['name'] == name:
            return vegetable
    return None

def add_vegetable(name, shape, hsv_range, min_size, max_size):
    """Adds a new vegetable entry to the database by name"""
    # check if the vegetable already exists in the database
    if get_vegetable_by_name(name):
        raise ValueError(f"Vegetable '{name}' already exists in the database")
    
    # generate a new ID for the vegetable
    new_id = 1
    if vegetables:
        new_id = max([v['id'] for v in vegetables]) + 1

    # create a new vegetable dictionary and add it to the list
    new_vegetable = {
        'id': new_id,
        'name': name,
        'shape': shape,
        'hsv_range': hsv_range,
        'min_size': min_size,
        'max_size' : max_size
    }
    vegetables.append(new_vegetable)

    # save the updated data to the JSON file
    save_vegetables()

def delete_vegetable_by_name(name):
    """Deletes the vegetable entry with the specified name"""
    for i, vegetable in enumerate(vegetables):
        if vegetable['name'] == name:
            del vegetables[i]
            save_vegetables()
            break

def get_shape_by_name(name):
    """Returns the shape for the vegetable with the specified name, or None if not found"""
    vegetable = get_vegetable_by_name(name)
    if vegetable:
        return vegetable['shape']
    return None

def get_min_size_by_name(name):
    """Returns the min size for the vegetable with the specified name, or None if not found"""
    vegetable = get_vegetable_by_name(name)
    if vegetable:
        return vegetable['min_size']
    return None

def get_max_size_by_name(name):
    """Returns the max size for the vegetable with the specified name, or None if not found"""
    vegetable = get_vegetable_by_name(name)
    if vegetable:
        return vegetable['max_size']
    return None

def get_hsv_range_by_name(name):
    """Returns the HSV range for the vegetable with the specified name as an array of integers, or None if not found"""
    vegetable = get_vegetable_by_name(name)
    if vegetable:
        hsv_range = vegetable['hsv_range']
        return [int(x) for x in hsv_range.split(',')]
    return None
