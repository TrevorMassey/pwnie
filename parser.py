


def parse(data, direction):
    prefix, data = data[:4], data[4:]
    _dir = '->' if direction == 1 else '<-'
    parsed_string = f"{self.port} {_dir} {prefix} {data}"
    print(parsed_string)

