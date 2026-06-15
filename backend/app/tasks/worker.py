import time


def main() -> None:
    print("AI recruitment worker started. Queue integration is reserved for the next iteration.")
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
