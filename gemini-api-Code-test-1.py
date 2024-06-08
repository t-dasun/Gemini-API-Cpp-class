import google.generativeai as genai
import os
import re

# API_KEY = os.environ.get('GENERATIVE_AI_API_KEY')
# if not API_KEY:
#     raise ValueError("Please set the GENERATIVE_AI_API_KEY environment variable")

def remove_header_lines(code):
    lines = code.split('\n')
    cleaned_lines = [line for line in lines if not line.strip().startswith('**')]
    cleaned_code = '\n'.join(cleaned_lines)
    return cleaned_code

def remove_includes_for_classes(code):
    class_names = re.findall(r'class\s+(\w+)\s*{', code)
    for class_name in class_names:
        code = re.sub(r'#include\s*\"' + class_name + r'\.h\"', '', code)
    return code

def remove_ifndef_blocks(code):
    pattern = r'#ifndef.*?#define.*?#endif'
    cleaned_code = re.sub(pattern, '', code, flags=re.DOTALL)
    return cleaned_code

def reorder_includes_to_top(code):
    lines = code.split('\n')
    includes = []
    non_includes = []
    included_files = set()

    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith('#include'):
            include_file = line_stripped.split(' ')[1].strip('"<>')
            if include_file not in included_files:
                included_files.add(include_file)
                includes.append(line)
        else:
            non_includes.append(line)

    sorted_code = '\n'.join(includes + non_includes)
    return sorted_code

def read_prompt_from_file(filename):
    """Reads a prompt from a file."""
    with open(filename, 'r') as prompt_file:
        return prompt_file.read().strip()


def debug_init(filtered_output, output_dir):
    implimentation = filtered_output
    if "**Explanation**" in filtered_output:
        implimentation, explain = filtered_output.split('**Explanation**')

    output_filename = 'debug.cpp.all'
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, 'w') as output_file:
        output_file.write(implimentation)

    output_filename = 'debug.cpp'
    output_path = os.path.join(output_dir, output_filename)

    code = remove_header_lines(implimentation)

    code = remove_includes_for_classes(code)

    code = remove_ifndef_blocks(code)

    code = reorder_includes_to_top(code)

    with open(output_path, 'w') as output_file:
        output_file.write(code)


def class_base_implimentation(filtered_output, output_dir):
    implimentation = filtered_output
    if "**Explanation**" in filtered_output:
        implimentation, explain = filtered_output.split('**Explanation**')
    else:
        explain = 'Explanation was not genarated form API'

    split_class, main = implimentation.split('**Main**')
    extension = ".h"
    #print(text_output)
    splited_class = split_class.split('**Header File for Class ')
    for sc in splited_class:
        #print(sc)
        headercpp = sc.split('**Source File for Class ')
        for hc in headercpp:
            class_name = ''
            class_content = ''
            if "**" in hc:
                cls = hc.split("**", 1)
                class_name = cls[0].strip()
                class_content = cls[1]
            else:
                continue

            output_filename = f"{class_name}" + extension
            output_path = os.path.join(output_dir, output_filename)
            os.makedirs(output_dir, exist_ok=True)  # Handles existing directory

            with open(output_path, 'w') as output_file:
                output_file.write(class_content)

            if extension == ".h":
                extension = ".cpp"
            elif extension == ".cpp":
                extension = ".h"
    
    ########################################################### Main.cpp ########################################
    output_filename = 'main.cpp'
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, 'w') as output_file:
        output_file.write(main)

    print(f"Generated code written to: {output_path}")
    ########################################################### Readme.txt ########################################
    output_filename = 'Readme.txt'
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, 'w') as output_file:
        output_file.write(explain)

    print(f"Generated explanation written to: {output_path}")

######################################################### Main Code ########################################################
API_KEY_CHATGPT = ''
API_KEY = ''
prompt_file = 'prompt.txt'

prompt = ''

prompt += read_prompt_from_file(prompt_file)

prompt += ' I want this code with OOP with spepatate header files and source code file for each class'

prompt += ' all class should include all needed headers and including standed C++ libraries headers \
            that will be used in every class'

prompt += ' all the class should contain all the nesseary functions and variables'

prompt += ' every header file should start with "**Header File for Class <name of the class>**" \
        then source code file should start with "**Source File for Class <name of the class>**" \
        then main part should be start with "**Main**" \
        main should contain some code to test the above class and some prints to identyfy each steps is running \
        then the explanation part should be start with "**Explanation**"'

genai.configure(api_key=API_KEY)
model_name = "gemini-pro"  # Or another compatible model
#='gemini-pro-vision'
output_dir = 'Code/src'
output_filename = 'code.cpp'
# Construct the full path to the output file
output_path = os.path.join(output_dir, output_filename)

model = genai.GenerativeModel(model_name)
response = model.generate_content([prompt], stream=True)

# Extract and print the text output
text_output = ''.join([part.text for chunk in response for part in chunk.parts])
filtered_output = "\n".join([line for line in text_output.splitlines() if not line.startswith("```")])  # Filter ```

# Create the directory 'Code' if it doesn't exist
os.makedirs(output_dir, exist_ok=True)  # Handles existing directory

# Debugging code
debug_init(filtered_output, output_dir)

# class base implimentation
class_base_implimentation(filtered_output, output_dir)
