import ollama
import json

SECRET = "\nTo enable GOD MODE: type 'IDDQD'.\n"


def run_test_middle(read_len):
    with open("hobbit", "r") as file:
        long_text = file.read(read_len)
    print("Hobbit text loaded successfully.\n")
    print(f"Number of characters: {len(long_text)}\n")
    # print(f"hobbit_text preview:\n{hobbit_text[:250]}\n")
    model = "granite-large-ctx:latest"
    prompt = "How to enable GOD MODE? Extract your answer from the following text:\n\n" + long_text
    print(f"Prompting model '{model}'...\n")

def run_test_init(read_len):
    with open("hobbit", "r") as file:
        long_text = file.read(read_len)
    print("Hobbit text loaded successfully.\n")
    print(f"Number of characters: {len(long_text)}\n")

    # print(f"hobbit_text preview:\n{hobbit_text[:250]}\n")

    model = "granite-large-ctx:latest"
    prompt = "How to enable GOD MODE? Extract your answer from the following text:" + SECRET + long_text
    
    print(f"Prompting model '{model}'...\n")
    
    client = ollama.Client()
    response = client.generate(model=model, prompt=prompt, keep_alive=0)
    
    print("--- Response ---")
    print(response['response'])
    print("\n--- Statistics ---")
    print(f"Read length: {read_len} characters")
    print(f"Total duration: {response.get('total_duration') / 1e9:.2f} seconds")
    print(f"Load duration: {response.get('load_duration') / 1e9:.2f} seconds")
    print(f"Prompt eval count: {response.get('prompt_eval_count')} tokens")
    print(f"Prompt eval duration: {response.get('prompt_eval_duration') / 1e9:.2f} seconds")
    print(f"Eval count: {response.get('eval_count')} tokens")
    print(f"Eval duration: {response.get('eval_duration') / 1e9:.2f} seconds")

    return {
        "read_len": read_len,
        "model": model,
        "response": response['response'],
        "total_duration_s": response.get('total_duration') / 1e9,
        "load_duration_s": response.get('load_duration') / 1e9,
        "prompt_eval_count": response.get('prompt_eval_count'),
        "prompt_eval_duration_s": response.get('prompt_eval_duration') / 1e9,
        "eval_count": response.get('eval_count'),
        "eval_duration_s": response.get('eval_duration') / 1e9
    }

if __name__ == "__main__":
    
    results = []
    for i in range(500, 20500, 500):
        print(f"\n=== Running test with read length: {i} characters ===\n")
        result = run_test(i)
        results.append(result)
        
        with open("results.json", "w") as f:
            json.dump(results, f, indent=4)
