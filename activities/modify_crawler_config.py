import json
def read_config():
    path = "/sd/lib/crawler/config.json"
    file = open(path).read()
    content = json.loads(file)
    return content

def write_config(content):
    path = "/sd/lib/crawler/config.json"

    with open(path, "w") as outfile:
        outfile.write(json.dumps(content))

    print(read_config())

def set_offset(index, joint, offset):
    # index: leg index, [0, 1, 2, 3]
    # joint: upper, lower
    assert index < 4, print("Error: Leg index should be from 0 to 3")
    assert type(index) == int, print("Error: Leg index should be integer")
    assert (joint == "upper") or (joint == "lower"), print("Error: joint should be either upper or lower")

    content = read_config()
    content["leg{}".format(index)][joint]["offset"] = offset
    write_config(content)

def set_pin(index, joint, pin):
    # index: leg index, [0, 1, 2, 3]
    # joint: upper, lower
    assert index < 4, print("Error: Leg index should be from 0 to 3")
    assert type(index) == int, print("Error: Leg index should be integer")
    assert (joint == "upper") or (joint == "lower"), print("Error: joint should be either upper or lower")

    content = read_config()
    content["leg{}".format(index)][joint]["pin"] = pin
    write_config(content)

set_offset(0, "upper", 0)
set_offset(3, "lower", 0)