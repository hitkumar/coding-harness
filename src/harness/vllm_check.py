from harness import VLLMClient


def main() -> None:
    client = VLLMClient(model="Qwen/Qwen3.6-27B-FP8", timeout=120)
    print(client.complete("Write a python function to reverse a string", 512))


if __name__ == "__main__":
    main()
