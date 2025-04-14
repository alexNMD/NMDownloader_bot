import time

BAR_LENGTH = 15


def get_progress_bar(progress: int, total: int) -> str:
    percent = 100 * (progress / float(total))
    filled_length = int(BAR_LENGTH * progress // total)
    bar = "⬛" * filled_length + "⬜" * (BAR_LENGTH - filled_length)
    return f"\r|{bar}| {percent:.1f}%"


# Exemple d'utilisation :
if __name__ == "__main__":
    _total = 100
    for i in range(_total + 1):
        print(get_progress_bar(i, _total))
        time.sleep(0.05)
    print("\nTerminé !")
