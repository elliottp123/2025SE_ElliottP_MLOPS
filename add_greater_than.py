# Example usage
input_filepath = 'data.txt'
output_filepath = 'splain.txt'

def add_greater_than(input_filepath, output_filepath):
    with open(input_filepath, 'r') as infile, open(output_filepath, 'w') as outfile:
        for line in infile:
            outfile.write(f'>{line}')


add_greater_than(input_filepath, output_filepath)
