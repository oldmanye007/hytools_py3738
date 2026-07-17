
try:
    import hytools as ht
    print(ht.__version__)

except ImportError:
    assert print("Warning: hytools is not installed.")


assert print("Finished.")==None