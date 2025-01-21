if pulse[j] <= peak * jsn["main"]["decay_low"]:
            print(f"decay:{j}")
            decay_10 = j
            break