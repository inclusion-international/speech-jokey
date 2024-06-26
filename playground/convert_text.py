text = "Hello, this is Isabella. I am trying something? Let's see."
print("Input text: ", text)

def convert_text(text):
    text_arr = list(text)
    output_text = ""
    for char in text_arr:
        # print(char)
        if char == ",": # default pause
            output_text = output_text + "<break time=\"0.0s\" />"

        elif char == "." or char == "?" or char == "!":
            output_text = output_text + "<break time=\"0.5s\" />"

        elif char == ";":
            output_text = output_text + "<break time=\"0.5s\" />"

        output_text = output_text + char

    print(output_text)



convert_text(text)