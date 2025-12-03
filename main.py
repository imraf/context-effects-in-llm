import ollama

READ_LEN = 25000

def main():
    with open("hobbit", "r") as file:
        hobbit_text = file.read(READ_LEN)
    print("Hobbit text loaded successfully.\n")
    print(f"Number of characters: {len(hobbit_text)}\n")

    # print(f"hobbit_text preview:\n{hobbit_text[:250]}\n")

    model = "granite-large-ctx:latest"
    prompt = "who was the leader of the wolf pack? Extract your answer from the following text:\n\n" + hobbit_text
    
    print(f"Prompting model '{model}'...\n")
    
    response = ollama.chat(model=model, messages=[
        {
            'role': 'user',
            'content': prompt,
        },
    ])
    
    print("--- Response ---")
    print(response['message']['content'])
    print("\n--- Statistics ---")
    print(f"Read length: {READ_LEN} characters")
    print(f"Total duration: {response.get('total_duration') / 1e9:.2f} seconds")
    print(f"Load duration: {response.get('load_duration') / 1e9:.2f} seconds")
    print(f"Prompt eval count: {response.get('prompt_eval_count')} tokens")
    print(f"Prompt eval duration: {response.get('prompt_eval_duration') / 1e9:.2f} seconds")
    print(f"Eval count: {response.get('eval_count')} tokens")
    print(f"Eval duration: {response.get('eval_duration') / 1e9:.2f} seconds")

if __name__ == "__main__":
    main()
